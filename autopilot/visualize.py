#!/usr/bin/env python3
"""Real-time graphical animation of dual-path research.

A terminal-based visualization showing the status of both research paths,
queue items, and progress. Uses ASCII art with real-time updates.

Usage:
    python3 autopilot/visualize.py

Controls:
    q - Quit
    r - Refresh
    1 - Show Path A details
    2 - Show Path B details
    s - Show overall status
"""
from __future__ import annotations

import os
import sys
import time
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# Try to import curses for better TUI, fall back to simple print
try:
    import curses
    HAS_CURSES = True
except ImportError:
    HAS_CURSES = False

REPO_DEFAULT = Path("/Users/mkupermann/Documents/GitHub/vibrasim")


@dataclass
class QueueItem:
    id: str
    status: str
    hypothesis: str
    pytest_target: str
    attempts: int = 0
    created_at: str = ""
    references: list = field(default_factory=list)
    max_runtime_seconds: int = 3600
    benchmarks: list = field(default_factory=list)
    path: str = ""
    
    @property
    def short_id(self) -> str:
        return self.id[:8]
    
    @property 
    def status_icon(self) -> str:
        icons = {
            "queued": "⏳",
            "running": "▶️", 
            "passed": "✅",
            "null": "➖",
            "failed": "❌",
        }
        return icons.get(self.status, "⚪")
    
    @property
    def status_color(self) -> str:
        colors = {
            "queued": "yellow",
            "running": "blue",
            "passed": "green", 
            "null": "cyan",
            "failed": "red",
        }
        return colors.get(self.status, "white")


@dataclass
class PathStatus:
    name: str
    queued: int = 0
    running: int = 0
    passed: int = 0
    null: int = 0
    failed: int = 0
    current_item: Optional[str] = None
    current_pid: Optional[int] = None
    stopped: bool = False
    items: list[QueueItem] = field(default_factory=list)
    
    @property
    def total(self) -> int:
        return self.queued + self.running + self.passed + self.null + self.failed
    
    @property
    def completion_rate(self) -> float:
        if self.total == 0:
            return 0.0
        return (self.passed + self.null) / self.total


class DualPathVisualizer:
    """Visualizes dual-path research in real-time."""
    
    def __init__(self, repo: Path | None = None):
        self.repo = repo or REPO_DEFAULT
        self.paths_config_path = self.repo / "autopilot" / "paths.yaml"
        
        if not self.paths_config_path.exists():
            raise FileNotFoundError(f"Paths config not found: {self.paths_config_path}")
        
        # Load path configurations
        import yaml
        self.paths_config = yaml.safe_load(self.paths_config_path.read_text())
        self.paths = list(self.paths_config.get("paths", {}).keys())
        self.autopilot_config = self.paths_config.get("autopilot", {})
        self.brain_benchmarks = self.paths_config.get("brain_advantage_benchmarks", [])
        
        # Path state directories
        self.path_states = {
            "path_a_elimination": Path("~/.eqmod/autopilot/path_a").expanduser(),
            "path_b_differentiation": Path("~/.eqmod/autopilot/path_b").expanduser(),
        }
    
    def get_status(self) -> dict[str, PathStatus]:
        """Get current status of all paths."""
        status = {}
        
        for path_name, state_dir in self.path_states.items():
            queue_path = state_dir / "queue.yaml"
            current_item_path = state_dir / "current_item.txt"
            pid_path = state_dir / "current.pid"
            stop_path = state_dir / "STOP"
            
            # Load queue
            items = []
            if queue_path.exists():
                import yaml
                queue_data = yaml.safe_load(queue_path.read_text())
                for item_data in queue_data.get("items") or []:
                    items.append(QueueItem(**item_data))
            
            # Count statuses
            counts = {"queued": 0, "running": 0, "passed": 0, "null": 0, "failed": 0}
            for item in items:
                counts[item.status] = counts.get(item.status, 0) + 1
            
            # Get current item
            current_item = None
            current_pid = None
            if current_item_path.exists():
                current_item = current_item_path.read_text().strip()
            if pid_path.exists():
                try:
                    current_pid = int(pid_path.read_text().strip())
                except (ValueError, OSError):
                    pass
            
            status[path_name] = PathStatus(
                name=self.paths_config["paths"][path_name]["name"],
                stopped=stop_path.exists(),
                current_item=current_item,
                current_pid=current_pid,
                items=items,
                **counts
            )
        
        return status
    
    def get_autopilot_pid(self) -> Optional[int]:
        """Get PID of running dual_path_dispatcher."""
        try:
            import subprocess
            result = subprocess.run(
                ["pgrep", "-f", "dual_path_dispatcher.py"],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                pids = [int(p) for p in result.stdout.strip().split() if p.isdigit()]
                return pids[0] if pids else None
        except Exception:
            pass
        return None
    
    def draw_brain(self, width: int = 40) -> str:
        """Draw a simple brain ASCII art."""
        brain = [
            "      ⢠⣴⣶⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦     ",
            "    ⢠⣿⡟⠛⠛⢻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣆     ",
            "   ⢠⣿⡏  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀    ",
            "  ⢸⣿⡇  ⢸⣿⣿⠈⠛⠛⢿⣿⣿⣿⣿⡇⡇   ",
            " ⢸⣿⡇  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡇⡇  ",
            " ⢸⣿⡇  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⣿⡇⡇⡇  ",
            "  ⢸⣿⡇  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇⡇   ",
            "   ⢠⣿⡇  ⢸⣿⣿⣿⣿⣿⣿⣿⣿⡇⡀    ",
            "    ⢠⣿⡇⢠⣤⣀⣀⠈⠙⠻⣿⣿⣷⣿⣆     ",
            "      ⢠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣷⣦     ",
        ]
        return "\n".join(brain[:width//8])
    
    def draw_gears(self, active: bool = True) -> str:
        """Draw animated gears."""
        frames = [
            ["  ⚙️  ", " ⚙️ ", "⚙️  ", " ⚙️ "],
            [" ⚙️  ", "⚙️  ", "  ⚙️ ", " ⚙️ "],
            ["⚙️  ", "  ⚙️ ", " ⚙️  ", "⚙️  "],
            [" ⚙️ ", " ⚙️  ", "  ⚙️ ", " ⚙️ "],
        ]
        import time
        frame = int(time.time() * 2) % len(frames)
        return " ".join(frames[frame])
    
    def draw_progress_bar(self, current: int, total: int, width: int = 20) -> str:
        """Draw a progress bar."""
        if total == 0:
            return "[" + " " * width + "] 0%"
        filled = int((current / total) * width)
        bar = "█" * filled + "░" * (width - filled)
        pct = int((current / total) * 100)
        return f"[{bar}] {pct}%"
    
    def draw_simple(self) -> str:
        """Draw simple ASCII visualization without curses."""
        status = self.get_status()
        autopilot_pid = self.get_autopilot_pid()
        
        lines = []
        
        # Header
        lines.append("")
        lines.append("=" * 70)
        lines.append("  VIBRASIM DUAL-PATH RESEARCH AUTopilot".center(70))
        lines.append("=" * 70)
        lines.append("")
        
        # Autopilot status
        if autopilot_pid:
            lines.append(f"  ⏳ Dispatcher: RUNNING (PID: {autopilot_pid})")
        else:
            lines.append(f"  ❌ Dispatcher: STOPPED")
        lines.append("")
        
        # Brain art
        brain_art = self.draw_brain()
        for line in brain_art.split("\n"):
            lines.append(f"  {line}")
        lines.append("")
        
        # Paths overview
        lines.append("-" * 70)
        lines.append("  RESEARCH PATHS")
        lines.append("-" * 70)
        
        for path_name, path_status in status.items():
            path_config = self.paths_config["paths"][path_name]
            prefix = "A" if "elimination" in path_name else "B"
            
            # Path header
            name = path_config["name"]
            mand = path_config.get("mandate", "")[:50]
            lines.append(f"  [{prefix}] {name}")
            lines.append(f"      Mandate: {mand}")
            lines.append(f"      Status: {'STOPPED' if path_status.stopped else 'RUNNING'}")
            
            # Stats
            lines.append(f"      Queue: {path_status.queued} queued | {path_status.running} running | "
                        f"{path_status.passed} passed | {path_status.null} null | {path_status.failed} failed")
            lines.append(f"      Completion: {path_status.completion_rate:.0%}")
            
            # Current item
            if path_status.current_item:
                lines.append(f"      Running: {path_status.current_item}")
                if path_status.current_pid:
                    lines.append(f"      PID: {path_status.current_pid}")
            
            lines.append("")
        
        # Brain-Advantage Benchmarks
        lines.append("-" * 70)
        lines.append("  BRAIN-ADVANTAGE BENCHMARKS (Path B Targets)")
        lines.append("-" * 70)
        
        for benchmark in self.brain_benchmarks:
            name = benchmark.get("name", "Unknown")
            target = benchmark.get("target", "N/A")
            llm_baseline = benchmark.get("llm_baseline", "N/A")
            lines.append(f"  • {name}")
            lines.append(f"    LLM Baseline: {llm_baseline} | Target: {target}")
        
        lines.append("")
        lines.append("-" * 70)
        lines.append("  Allocations: Path A 40% | Path B 60%")
        lines.append("-" * 70)
        lines.append("")
        
        # Animation
        lines.append(f"  {self.draw_gears()}  Research in progress...")
        lines.append("")
        
        return "\n".join(lines)
    
    def run_curses(self, stdscr) -> None:
        """Run visualization with curses."""
        if not HAS_CURSES:
            return
        
        curses.curs_set(0)  # Hide cursor
        stdscr.nodelay(1)  # Non-blocking input
        
        while True:
            stdscr.clear()
            
            # Get terminal size
            height, width = stdscr.getmaxyx()
            
            # Draw content
            try:
                content = self.draw_simple()
                for i, line in enumerate(content.split("\n")):
                    if i < height - 1:
                        stdscr.addstr(i, 0, line[:width-1])
            except Exception as e:
                stdscr.addstr(0, 0, f"Error: {e}")
            
            stdscr.refresh()
            
            # Check for quit
            if stdscr.getch() == ord('q'):
                break
            
            time.sleep(0.5)
    
    def run_simple(self) -> None:
        """Run visualization with simple print (no curses)."""
        try:
            while True:
                os.system('clear' if os.name == 'posix' else 'cls')
                print(self.draw_simple())
                time.sleep(2)
        except KeyboardInterrupt:
            print("\nVisualization stopped.")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Real-time visualization of dual-path research"
    )
    parser.add_argument(
        "--repo", type=str, default=None,
        help="Path to vibrasim repository"
    )
    parser.add_argument(
        "--no-animate", action="store_true",
        help="Single display, no animation"
    )
    
    args = parser.parse_args()
    
    try:
        visualizer = DualPathVisualizer(repo=Path(args.repo) if args.repo else None)
        
        if args.no_animate:
            print(visualizer.draw_simple())
        elif HAS_CURSES:
            curses.wrapper(visualizer.run_curses)
        else:
            visualizer.run_simple()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
