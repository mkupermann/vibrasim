"""Dual-Path Autopilot Dispatcher

Manages two parallel research paths:
  Path A (Elimination): Find what's NOT LLM - pre-LLM substrates without transformer mechanisms
  Path B (Differentiation): Build what LLMs can't do - brain-style capabilities

This dispatcher extends the bet_dispatcher concept to support dual-hypothesis
research, balancing iterations between both paths according to configured
allocations.

Usage:
    python autopilot/dual_path_dispatcher.py          # Run both paths (60s tick)
    python autopilot/dual_path_dispatcher.py --once   # Single tick
    python autopilot/dual_path_dispatcher.py --path path_a  # Only Path A
    python autopilot/dual_path_dispatcher.py --path path_b  # Only Path B
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import random
import signal
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import yaml

# Repo root - update if needed
REPO_DEFAULT = Path("/Users/mkupermann/Documents/GitHub/vibrasim")

DEFAULT_INTERVAL_SECONDS = 60.0
DEFAULT_MAX_RUNTIME_SECONDS = 3600  # 1h iteration cap
DEFAULT_TERM_GRACE_SECONDS = 3


class PathConfig:
    """Configuration for a single research path."""
    
    def __init__(self, config: dict, paths_yaml_path: Path):
        self.name = config.get("name", "Unknown")
        self.description = config.get("description", "")
        self.mandate = config.get("mandate", "")
        self.success_criteria = config.get("success_criteria", [])
        self.queue_prefix = config.get("queue_prefix", "")
        self.state_dir_base = config.get("state_dir", "~/.eqmod/autopilot")
        self.paths_yaml_path = paths_yaml_path
        
        # Expand state_dir
        self.state_dir = Path(self.state_dir_base).expanduser()
        self.queue_path = self.state_dir / "queue.yaml"
        self.stop_path = self.state_dir / "STOP"
        self.pid_path = self.state_dir / "current.pid"
        self.current_item_path = self.state_dir / "current_item.txt"
        self.dispatcher_log = self.state_dir / "dispatcher.log"
        self.logbook_path = self.state_dir / "LOGBOOK.md"
        self.path_key = Path(paths_yaml_path).stem  # e.g., "paths" -> use path name
    
    def __repr__(self):
        return f"PathConfig(name={self.name!r}, prefix={self.queue_prefix!r})"


class DualPathDispatcher:
    """Manages two parallel research paths with configurable allocation."""
    
    def __init__(
        self,
        paths_config_path: Path | str | None = None,
        repo: Path | str | None = None,
        term_grace_seconds: float = DEFAULT_TERM_GRACE_SECONDS,
        evaluate_timeout_seconds: float = 600.0,
        single_path: str | None = None,  # If set, only run this path
    ):
        self.repo = Path(repo) if repo else REPO_DEFAULT
        self.term_grace_seconds = float(term_grace_seconds)
        self.evaluate_timeout_seconds = float(evaluate_timeout_seconds)
        self.single_path = single_path
        
        # Load paths configuration
        if paths_config_path is None:
            paths_config_path = self.repo / "autopilot" / "paths.yaml"
        self.paths_config_path = Path(paths_config_path)
        
        if not self.paths_config_path.exists():
            raise FileNotFoundError(
                f"Paths configuration not found: {self.paths_config_path}"
            )
        
        self.paths_config = yaml.safe_load(self.paths_config_path.read_text())
        self.autopilot_config = self.paths_config.get("autopilot", {})
        
        # Initialize path configs
        self.paths = {}
        for path_name, path_config in self.paths_config.get("paths", {}).items():
            self.paths[path_name] = PathConfig(path_config, self.paths_config_path)
        
        # Get allocation percentages
        self.path_allocation = self.autopilot_config.get("path_allocation", {})
        
        # Override with single_path if specified
        if single_path and single_path in self.paths:
            self.active_paths = [single_path]
        else:
            self.active_paths = list(self.paths.keys())
    
    def log(self, msg: str, path_name: str | None = None) -> None:
        """Log a message, optionally for a specific path."""
        prefix = f"[{path_name}] " if path_name else ""
        line = f"[{_dt.datetime.now().isoformat()}] {prefix}{msg}\n"
        
        # Log to each active path's dispatcher log
        if path_name and path_name in self.paths:
            log_path = self.paths[path_name].dispatcher_log
        else:
            # Log to a central autopilot log
            log_dir = self.paths_config_path.parent / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / "dual_path_dispatcher.log"
        
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with log_path.open("a") as f:
            f.write(line)
    
    def _get_path_dispatcher(self, path_name: str):
        """Import and return a BetDispatcher for a specific path."""
        # Add repo to sys.path so we can import tools.bet_dispatcher
        if str(self.repo) not in sys.path:
            sys.path.insert(0, str(self.repo))
        
        from tools.bet_dispatcher import BetDispatcher
        
        path_config = self.paths[path_name]
        return BetDispatcher(
            state_dir=path_config.state_dir,
            repo=self.repo,
            term_grace_seconds=self.term_grace_seconds,
            evaluate_timeout_seconds=self.evaluate_timeout_seconds,
        )
    
    def load_all_queues(self) -> dict[str, list[dict]]:
        """Load queues for all paths."""
        queues = {}
        for path_name in self.active_paths:
            path_config = self.paths[path_name]
            dispatcher = self._get_path_dispatcher(path_name)
            queue_data = dispatcher.load_queue()
            queues[path_name] = queue_data.get("items") or []
        return queues
    
    def get_next_item(self) -> tuple[str, dict] | None:
        """Select next item to run based on path allocation.
        
        Returns (path_name, item) or None if no items queued.
        """
        queues = self.load_all_queues()
        
        # Get queued items for each path
        queued_items = {}
        for path_name in self.active_paths:
            items = [i for i in queues[path_name] if i.get("status") == "queued"]
            if items:
                queued_items[path_name] = items
        
        if not queued_items:
            return None
        
        # If only one path has items, use it
        if len(queued_items) == 1:
            path_name = list(queued_items.keys())[0]
            return path_name, queued_items[path_name][0]
        
        # Multiple paths have items - use allocation percentages
        # Get allocation weights
        total_weight = sum(self.path_allocation.get(p, 50) for p in queued_items)
        if total_weight == 0:
            # Default to equal distribution
            total_weight = len(queued_items) * 50
        
        # Weighted random selection
        weights = {p: self.path_allocation.get(p, 50) for p in queued_items}
        path_name = random.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]
        
        return path_name, queued_items[path_name][0]
    
    def get_path_status(self, path_name: str) -> dict:
        """Get current status of a path."""
        path_config = self.paths[path_name]
        dispatcher = self._get_path_dispatcher(path_name)
        
        status = {
            "path": path_name,
            "name": path_config.name,
            "running": False,
            "current_item": None,
            "queued_count": 0,
            "running_count": 0,
            "stopped": path_config.stop_path.exists(),
        }
        
        if path_config.pid_path.exists():
            try:
                pid = int(path_config.pid_path.read_text().strip())
                if self._pid_alive(pid):
                    status["running"] = True
                    if path_config.current_item_path.exists():
                        status["current_item"] = path_config.current_item_path.read_text().strip()
            except (ValueError, OSError):
                pass
        
        queue = dispatcher.load_queue()
        for item in queue.get("items") or []:
            if item.get("status") == "queued":
                status["queued_count"] += 1
            elif item.get("status") == "running":
                status["running_count"] += 1
        
        return status
    
    def _pid_alive(self, pid: int) -> bool:
        """Check if a process is alive (not zombie)."""
        try:
            reaped_pid, _ = os.waitpid(pid, os.WNOHANG)
            if reaped_pid == pid:
                return False
        except ChildProcessError:
            pass
        except OSError:
            pass
        try:
            os.kill(pid, 0)
        except (ProcessLookupError, PermissionError):
            return False
        except Exception:
            return False
        try:
            import subprocess as _sp
            r = _sp.run(
                ["/bin/ps", "-o", "stat=", "-p", str(pid)],
                capture_output=True, text=True, timeout=2,
            )
            state = r.stdout.strip()
            if state.startswith("Z"):
                return False
        except Exception:
            pass
        return True
    
    def tick(self) -> dict[str, Any]:
        """Run one dispatcher tick across all paths.
        
        Returns a dict describing what happened.
        """
        self.log("--- dual-path autopilot tick")
        
        # Check if global STOP marker exists
        global_stop = self.paths_config_path.parent / "STOP"
        if global_stop.exists():
            self.log("Global STOP marker present — return stopped")
            return {"action": "stopped", "reason": "global_stop"}
        
        # Check for items to run
        next_item = self.get_next_item()
        
        if next_item is None:
            self.log("No queued items across any path — return idle")
            return {"action": "idle", "reason": "no_queued_items"}
        
        path_name, item = next_item
        self.log(f"Selected path: {path_name}, item: {item.get('id')}", path_name)
        
        # Use the path-specific dispatcher to launch
        dispatcher = self._get_path_dispatcher(path_name)
        
        # Check if path is stopped
        if self.paths[path_name].stop_path.exists():
            self.log(f"Path {path_name} STOP marker present — skipping", path_name)
            return {"action": "skipped", "path": path_name, "reason": "path_stopped"}
        
        # Check if something is already running on this path
        if dispatcher.pid_path.exists():
            try:
                pid = int(dispatcher.pid_path.read_text().strip())
                if self._pid_alive(pid):
                    max_runtime = int(
                        (item.get("max_runtime_seconds") or DEFAULT_MAX_RUNTIME_SECONDS)
                    )
                    elapsed = time.time() - dispatcher.pid_path.stat().st_mtime
                    if elapsed > max_runtime:
                        self.log(
                            f"HARD-CAP VIOLATION on {path_name}: "
                            f"pid={pid} item={item.get('id')} "
                            f"elapsed={elapsed:.0f}s > max={max_runtime}s",
                            path_name
                        )
                        # Let the path dispatcher handle the kill
                        return {
                            "action": "hardcap_violation",
                            "path": path_name,
                            "item": item.get("id"),
                        }
                    return {
                        "action": "already_running",
                        "path": path_name,
                        "item": item.get("id"),
                        "pid": pid,
                    }
            except (ValueError, OSError):
                pass
        
        # Launch the item
        pid = dispatcher.launch_item(item)
        dispatcher.update_item_status(item["id"], "running")
        self.log(f"Launched {item.get('id')} on path {path_name} pid={pid}", path_name)
        
        return {
            "action": "launched",
            "path": path_name,
            "item": item.get("id"),
            "pid": pid,
        }
    
    def get_overall_status(self) -> dict:
        """Get status of all paths."""
        status = {
            "paths": {},
            "allocations": self.path_allocation,
            "active_paths": self.active_paths,
        }
        
        for path_name in self.active_paths:
            status["paths"][path_name] = self.get_path_status(path_name)
        
        return status


# ---- CLI -------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Dual-Path Autopilot Dispatcher",
    )
    parser.add_argument(
        "--interval", type=float, default=DEFAULT_INTERVAL_SECONDS,
        help="seconds between ticks (default 60)",
    )
    parser.add_argument(
        "--paths-config", type=str, default=None,
        help="path to paths.yaml (default autopilot/paths.yaml)",
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help=f"override repo root (default {REPO_DEFAULT})",
    )
    parser.add_argument(
        "--once", action="store_true",
        help="single tick, then exit",
    )
    parser.add_argument(
        "--path", type=str, default=None,
        choices=["path_a_elimination", "path_b_differentiation"],
        help="only run a single path (default: both)",
    )
    parser.add_argument(
        "--status", action="store_true",
        help="print status and exit",
    )
    
    args = parser.parse_args(argv)
    
    dispatcher = DualPathDispatcher(
        paths_config_path=args.paths_config,
        repo=args.repo,
        single_path=args.path,
    )
    
    if args.status:
        status = dispatcher.get_overall_status()
        print(json.dumps(status, default=str, indent=2))
        return 0
    
    if args.once:
        result = dispatcher.tick()
        print(json.dumps(result, default=str))
        return 0
    
    # Continuous polling
    while True:
        try:
            result = dispatcher.tick()
            if result.get("action") == "stopped":
                time.sleep(max(1.0, float(args.interval)))
                continue
        except Exception as exc:
            dispatcher.log(f"tick exception: {exc!r}")
        time.sleep(max(1.0, float(args.interval)))


if __name__ == "__main__":
    sys.exit(main())
