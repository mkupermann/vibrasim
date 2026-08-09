#!/usr/bin/env python3
"""Breakthrough Watchdog – Benachrichtigt bei ersten PASSED BETs.

Läuft als Hintergrund-Prozess und überwacht die Queue-Dateien.
Bei jedem neuen "passed" Item: Terminal-Ausgabe + macOS Notification + Sound.

Usage:
    python3 autopilot/breakthrough_watchdog.py          # Einmal prüfen
    python3 autopilot/breakthrough_watchdog.py --watch  # Kontinuierlich alle 60s prüfen
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List
import yaml

# Farbcodes für Terminal
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'


def send_notification(title: str, message: str) -> None:
    """Sendet macOS Notification + Terminal-Ausgabe + Sound."""
    # Terminal
    print(f"\n{BLUE}=== 🔬 BREAKTHROUGH DETECTED ==={RESET}")
    print(f"{GREEN}{title}{RESET}")
    print(f"{YELLOW}{message}{RESET}")
    print(f"{BLUE}==================================={RESET}\n")
    
    # macOS Notification
    try:
        script = f'display notification "{message}" with title "{title}"'
        subprocess.run(['osascript', '-e', script], check=False)
    except Exception:
        pass
    
    # Sound
    try:
        subprocess.run(['afplay', '/System/Library/Sounds/Glass.aiff'], check=False)
    except Exception:
        pass


def load_queue(path: Path) -> List[Dict]:
    """Lädt Queue-Items aus YAML-Datei."""
    if not path.exists():
        return []
    with open(path) as f:
        data = yaml.safe_load(f) or {}
    return data.get('items') or []


def check_breakthroughs() -> Dict[str, List[Dict]]:
    """Prüft beide Queues auf neue PASSED Items."""
    path_a_queue = Path.home() / '.eqmod/autopilot/path_a/queue.yaml'
    path_b_queue = Path.home() / '.eqmod/autopilot/path_b/queue.yaml'
    
    path_a_items = load_queue(path_a_queue)
    path_b_items = load_queue(path_b_queue)
    
    passed_a = [i for i in path_a_items if i.get('status') == 'passed']
    passed_b = [i for i in path_b_items if i.get('status') == 'passed']
    
    return {
        'path_a': passed_a,
        'path_b': passed_b,
        'all_passed': passed_a + passed_b
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description='Breakthrough Watchdog')
    parser.add_argument('--watch', action='store_true', help='Kontinuierlich alle 60s prüfen')
    parser.add_argument('--interval', type=int, default=60, help='Sekunden zwischen Checks')
    args = parser.parse_args(argv)
    
    if args.watch:
        print(f"{BLUE}🔍 Breakthrough Watchdog aktiv – prüfe alle {args.interval}s{RESET}")
        print(f"{YELLOW}Warte auf erste PASSED Ergebnisse...{RESET}\n")
        
        last_passed = set()
        
        while True:
            try:
                result = check_breakthroughs()
                current_passed = {item['id'] for item in result['all_passed']}
                
                new_passed = current_passed - last_passed
                
                for item_id in new_passed:
                    item = next(i for i in result['all_passed'] if i['id'] == item_id)
                    path = 'A' if item['id'].startswith('EA') else 'B'
                    msg = f"BET {item['id']} (Path {path}) → PASSED!\nTarget: {item.get('pytest_target', 'N/A')}"
                    send_notification(f"🎉 BREAKTHROUGH auf Path {path}", msg)
                
                last_passed = current_passed
                
                # Statistik anzeigen
                total_passed = len(current_passed)
                if total_passed > 0:
                    sys.stdout.write(f"\r{GREEN}✓ {total_passed} Breakthroughs bisher{RESET}")
                    sys.stdout.flush()
                
            except Exception as e:
                print(f"{RED}Error: {e}{RESET}")
            
            time.sleep(args.interval)
    
    else:
        # Einmal prüfen
        result = check_breakthroughs()
        
        if result['all_passed']:
            print(f"\n{GREEN}🎉 Aktuelle Breakthroughs:{RESET}")
            for item in result['all_passed']:
                path = 'A (Elimination)' if item['id'].startswith('EA') else 'B (Differentiation)'
                print(f"  {GREEN}{item['id']}{RESET} auf Path {path}")
                print(f"    Target: {item.get('pytest_target', 'N/A')}")
            print()
        else:
            print(f"{YELLOW}⏳ Noch keine Breakthroughs – {len(load_queue(Path.home() / '.eqmod/autopilot/path_a/queue.yaml')) + len(load_queue(Path.home() / '.eqmod/autopilot/path_b/queue.yaml'))} Items in Queue{RESET}")
        
        # Aktuelle Statistik
        path_a_items = load_queue(Path.home() / '.eqmod/autopilot/path_a/queue.yaml')
        path_b_items = load_queue(Path.home() / '.eqmod/autopilot/path_b/queue.yaml')
        
        a_passed = sum(1 for i in path_a_items if i.get('status') == 'passed')
        a_null = sum(1 for i in path_a_items if i.get('status') == 'null')
        a_failed = sum(1 for i in path_a_items if i.get('status') == 'failed')
        
        b_passed = sum(1 for i in path_b_items if i.get('status') == 'passed')
        b_null = sum(1 for i in path_b_items if i.get('status') == 'null')
        b_failed = sum(1 for i in path_b_items if i.get('status') == 'failed')
        
        print(f"\n{BLUE}Aktueller Status:{RESET}")
        print(f"  Path A: {a_passed}✓ {a_null}⚪ {a_failed}✗")
        print(f"  Path B: {b_passed}✓ {b_null}⚪ {b_failed}✗")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
