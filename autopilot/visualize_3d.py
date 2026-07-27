#!/usr/bin/env python3
"""3D Innovative Animations for Dual-Path Research Progress.

Creates interactive 3D visualizations showing research progress:
1. 3D Brain Model - Rotating brain with neural activity
2. 3D Progress Tower - Stacked blocks representing BET items
3. 3D Research Landscape - Terrain map of research space
4. 3D Network Graph - Substrate connections

Usage:
    python3 autopilot/visualize_3d.py              # Interactive 3D window
    python3 autopilot/visualize_3d.py --type brain   # Brain model
    python3 autopilot/visualize_3d.py --type tower  # Progress tower
    python3 autopilot/visualize_3d.py --type landscape # Research landscape
    python3 autopilot/visualize_3d.py --type network  # Network graph
    python3 autopilot/visualize_3d.py --static        # Single frame, no animation
    python3 autopilot/visualize_3d.py --save         # Save to HTML

Requirements:
    matplotlib, numpy (installed in .venv)
"""
from __future__ import annotations

import os
import sys
import time
import argparse
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Tuple
import json

# Add repo to path
REPO_DEFAULT = Path("/Users/mkupermann/Documents/GitHub/vibrasim")
sys.path.insert(0, str(REPO_DEFAULT))

try:
    import numpy as np
    import matplotlib
    matplotlib.use('TkAgg')  # or 'Qt5Agg' for Qt backend
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.colors import LinearSegmentedColormap
    from mpl_toolkits.mplot3d import Axes3D
    from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    HAS_MATPLOTLIB = True
except ImportError as e:
    HAS_MATPLOTLIB = False
    MATPLOTLIB_ERROR = str(e)


@dataclass
class BETItem:
    """Represents a BET item in the queue."""
    id: str
    status: str
    hypothesis: str
    pytest_target: str
    path: str
    attempts: int = 0
    created_at: str = ""
    benchmarks: List[str] = field(default_factory=list)
    
    @property
    def is_path_a(self) -> bool:
        return "EA-" in self.id or "elimination" in self.path
    
    @property
    def is_path_b(self) -> bool:
        return "DB-" in self.id or "differentiation" in self.path
    
    @property
    def status_color(self) -> Tuple[float, float, float]:
        """RGB color for status."""
        colors = {
            "queued": (1.0, 0.8, 0.0),    # Gold
            "running": (0.0, 0.5, 1.0),   # Blue
            "passed": (0.0, 1.0, 0.0),    # Green
            "null": (0.5, 0.5, 1.0),     # Light blue
            "failed": (1.0, 0.0, 0.0),   # Red
        }
        return colors.get(self.status, (0.8, 0.8, 0.8))
    
    @property
    def status_height(self) -> float:
        """Height multiplier for status."""
        heights = {"queued": 0.5, "running": 1.0, "passed": 1.5, "null": 0.8, "failed": 0.3}
        return heights.get(self.status, 0.5)


class ResearchData:
    """Loads and manages research data from both paths."""
    
    def __init__(self, repo: Path | None = None):
        self.repo = repo or REPO_DEFAULT
        self.paths_config_path = self.repo / "autopilot" / "paths.yaml"
        
        if not self.paths_config_path.exists():
            raise FileNotFoundError(f"Paths config not found: {self.paths_config_path}")
        
        import yaml
        self.paths_config = yaml.safe_load(self.paths_config_path.read_text())
        self.brain_benchmarks = self.paths_config.get("brain_advantage_benchmarks", [])
        
        # Path state directories
        self.path_states = {
            "path_a_elimination": Path("~/.eqmod/autopilot/path_a").expanduser(),
            "path_b_differentiation": Path("~/.eqmod/autopilot/path_b").expanduser(),
        }
    
    def load_all_items(self) -> List[BETItem]:
        """Load all BET items from both paths."""
        items = []
        
        for path_name, state_dir in self.path_states.items():
            queue_path = state_dir / "queue.yaml"
            
            if queue_path.exists():
                import yaml
                queue_data = yaml.safe_load(queue_path.read_text())
                for item_data in queue_data.get("items") or []:
                    item = BETItem(
                        id=item_data.get("id", ""),
                        status=item_data.get("status", "queued"),
                        hypothesis=item_data.get("hypothesis", ""),
                        pytest_target=item_data.get("pytest_target", ""),
                        path=path_name,
                        attempts=item_data.get("attempts", 0),
                        created_at=item_data.get("created_at", ""),
                        benchmarks=item_data.get("benchmarks", []),
                    )
                    items.append(item)
        
        return items
    
    def get_path_stats(self) -> dict:
        """Get statistics for each path."""
        items = self.load_all_items()
        
        stats = {
            "path_a": {"queued": 0, "running": 0, "passed": 0, "null": 0, "failed": 0},
            "path_b": {"queued": 0, "running": 0, "passed": 0, "null": 0, "failed": 0},
        }
        
        for item in items:
            path = "path_a" if item.is_path_a else "path_b"
            if path in stats:
                stats[path][item.status] = stats[path].get(item.status, 0) + 1
        
        return stats
    
    def get_current_items(self) -> dict:
        """Get currently running items."""
        current = {"path_a": None, "path_b": None}
        
        for path_name, state_dir in self.path_states.items():
            current_item_path = state_dir / "current_item.txt"
            if current_item_path.exists():
                item_id = current_item_path.read_text().strip()
                current["path_a" if "path_a" in path_name else "path_b"] = item_id
        
        return current


class Brain3D:
    """3D Brain model animation."""
    
    def __init__(self, data: ResearchData):
        self.data = data
        self.fig = None
        self.ax = None
    
    def create_ellipsoid(self, center, radii, color='gray', alpha=0.8):
        """Create a 3D ellipsoid (simplified brain shape)."""
        u = np.linspace(0, 2 * np.pi, 30)
        v = np.linspace(0, np.pi, 15)
        x = radii[0] * np.outer(np.cos(u), np.sin(v)) + center[0]
        y = radii[1] * np.outer(np.sin(u), np.sin(v)) + center[1]
        z = radii[2] * np.outer(np.ones(np.size(u)), np.cos(v)) + center[2]
        self.ax.plot_surface(x, y, z, color=color, alpha=alpha, rstride=1, cstride=1)
    
    def add_neural_activity(self, path_items: List[BETItem]):
        """Add neural activity points based on BET items."""
        for i, item in enumerate(path_items):
            # Position based on item index and status
            theta = 2 * np.pi * i / len(path_items)
            r = 0.5 + 0.3 * np.random.random()
            
            # Height based on status
            h = item.status_height
            
            x = r * np.cos(theta)
            y = r * np.sin(theta)
            z = h
            
            # Size based on attempts
            size = 10 + 5 * item.attempts
            
            color = item.status_color
            self.ax.scatter(x, y, z, s=size, c=[color], depthshade=True)
    
    def animate(self, frame):
        """Animation update."""
        self.ax.view_init(elev=30, azim=frame * 2)
        return self.ax,
    
    def run(self):
        """Run the 3D brain animation."""
        if not HAS_MATPLOTLIB:
            print(f"Matplotlib not available: {MATPLOTLIB_ERROR}")
            return
        
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        # Draw brain
        self.create_ellipsoid((0, 0, 0), (2, 1.5, 1.2), color='lightgray', alpha=0.6)
        
        # Load data
        items = self.data.load_all_items()
        path_a_items = [i for i in items if i.is_path_a]
        path_b_items = [i for i in items if i.is_path_b]
        
        # Add neural activity
        self.add_neural_activity(path_a_items)
        self.add_neural_activity(path_b_items)
        
        # Add hemisphere division
        self.ax.plot([-2, 2], [0, 0], [0, 0], 'k--', alpha=0.3)
        
        # Labels
        self.ax.set_title('VIBRASIM Research Brain - Neural Activity', fontsize=14)
        self.ax.set_xlabel('Path A (Elimination) ← → Path B (Differentiation)')
        self.ax.set_ylabel('Progress')
        self.ax.set_zlabel('Success Rate')
        
        # Animation
        ani = FuncAnimation(
            self.fig, 
            self.animate, 
            frames=180, 
            interval=50,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return ani


class ProgressTower3D:
    """3D Progress Tower - Each BET is a block in a tower."""
    
    def __init__(self, data: ResearchData):
        self.data = data
        self.fig = None
        self.ax = None
    
    def create_tower(self):
        """Create 3D tower of BET items."""
        items = self.data.load_all_items()
        
        # Separate by path
        path_a_items = [i for i in items if i.is_path_a]
        path_b_items = [i for i in items if i.is_path_b]
        
        max_items = max(len(path_a_items), len(path_b_items), 1)
        
        # Draw Path A tower (left)
        for i, item in enumerate(path_a_items):
            x = -1.5
            y = i / max_items * 2 - 1
            z = 0
            
            color = item.status_color
            height = item.status_height * 0.5
            
            # Create cube
            self.draw_cube((x, y, z), (0.8, 0.8, height), color)
        
        # Draw Path B tower (right)
        for i, item in enumerate(path_b_items):
            x = 1.5
            y = i / max_items * 2 - 1
            z = 0
            
            color = item.status_color
            height = item.status_height * 0.5
            
            self.draw_cube((x, y, z), (0.8, 0.8, height), color)
        
        # Add labels
        self.ax.text(-1.5, -1.2, 0, 'Path A\nElimination', fontsize=10, ha='center')
        self.ax.text(1.5, -1.2, 0, 'Path B\nDifferentiation', fontsize=10, ha='center')
        
        self.ax.set_xlim([-3, 3])
        self.ax.set_ylim([-1.5, 1.5])
        self.ax.set_zlim([0, 2])
        self.ax.set_title('VIBRASIM Progress Towers - BET Items Stacked', fontsize=14)
    
    def draw_cube(self, position, size, color):
        """Draw a 3D cube."""
        x, y, z = position
        dx, dy, dz = size
        
        # Define cube vertices
        vertices = np.array([
            [x, y, z],           # 0
            [x+dx, y, z],        # 1
            [x+dx, y+dy, z],     # 2
            [x, y+dy, z],        # 3
            [x, y, z+dz],        # 4
            [x+dx, y, z+dz],     # 5
            [x+dx, y+dy, z+dz],  # 6
            [x, y+dy, z+dz],     # 7
        ])
        
        # Define cube faces
        faces = [
            [vertices[0], vertices[1], vertices[2], vertices[3]],  # front
            [vertices[4], vertices[5], vertices[6], vertices[7]],  # back
            [vertices[0], vertices[1], vertices[5], vertices[4]],  # bottom
            [vertices[2], vertices[3], vertices[7], vertices[6]],  # top
            [vertices[0], vertices[3], vertices[7], vertices[4]],  # left
            [vertices[1], vertices[2], vertices[6], vertices[5]],  # right
        ]
        
        for face in faces:
            self.ax.add_collection3d(
                Poly3DCollection([face], alpha=0.8, linewidths=0.5, edgecolors='k', facecolors=color)
            )
    
    def animate(self, frame):
        """Animation update."""
        self.ax.view_init(elev=20, azim=frame * 2)
        return self.ax,
    
    def run(self):
        """Run the 3D progress tower animation."""
        if not HAS_MATPLOTLIB:
            print(f"Matplotlib not available: {MATPLOTLIB_ERROR}")
            return
        
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.create_tower()
        
        # Animation
        ani = FuncAnimation(
            self.fig, 
            self.animate, 
            frames=180, 
            interval=50,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return ani


class ResearchLandscape3D:
    """3D Research Landscape - Terrain showing research space."""
    
    def __init__(self, data: ResearchData):
        self.data = data
        self.fig = None
        self.ax = None
    
    def create_landscape(self):
        """Create 3D terrain landscape."""
        # Create grid
        x = np.linspace(-5, 5, 100)
        y = np.linspace(-5, 5, 100)
        X, Y = np.meshgrid(x, y)
        
        # Base terrain (hills)
        Z = np.sin(X) * np.cos(Y) * 0.5
        
        # Add peaks for successful BETs
        items = self.data.load_all_items()
        
        for i, item in enumerate(items):
            # Position based on path
            px = -2 + 4 * (1 if item.is_path_b else 0)
            py = -4 + 8 * (i / max(len(items), 1))
            
            # Height based on status
            height = item.status_height * 0.5
            
            # Add a peak
            distance = np.sqrt((X - px)**2 + (Y - py)**2)
            Z += height * np.exp(-distance * 2)
        
        # Plot surface
        self.ax.plot_surface(X, Y, Z, cmap='terrain', alpha=0.8, rstride=2, cstride=2)
        
        # Add labels for paths
        self.ax.text(-5, -5, 0.5, 'Path A\nElimination', fontsize=12, ha='center')
        self.ax.text(5, -5, 0.5, 'Path B\nDifferentiation', fontsize=12, ha='center')
        
        # Add peaks for current items
        current = self.data.get_current_items()
        for path, item_id in current.items():
            if item_id:
                px = -2 if path == "path_a" else 2
                py = 0
                self.ax.scatter(px, py, 1.5, s=200, c='red', marker='^', depthshade=True)
                self.ax.text(px, py, 1.6, item_id, fontsize=10, ha='center')
        
        self.ax.set_xlim([-5, 5])
        self.ax.set_ylim([-5, 5])
        self.ax.set_zlim([0, 3])
        self.ax.set_title('VIBRASIM Research Landscape - Peaks = Successful BETs', fontsize=14)
        self.ax.set_xlabel('Research Path')
        self.ax.set_ylabel('Progress')
        self.ax.set_zlabel('Success')
    
    def animate(self, frame):
        """Animation update."""
        self.ax.view_init(elev=25, azim=frame * 2)
        return self.ax,
    
    def run(self):
        """Run the 3D research landscape animation."""
        if not HAS_MATPLOTLIB:
            print(f"Matplotlib not available: {MATPLOTLIB_ERROR}")
            return
        
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.create_landscape()
        
        # Animation
        ani = FuncAnimation(
            self.fig, 
            self.animate, 
            frames=180, 
            interval=50,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return ani


class NetworkGraph3D:
    """3D Network Graph - Shows substrate connections."""
    
    def __init__(self, data: ResearchData):
        self.data = data
        self.fig = None
        self.ax = None
    
    def create_network(self):
        """Create 3D network graph of BET dependencies."""
        items = self.data.load_all_items()
        
        # Create nodes in a circle
        n = len(items)
        theta = np.linspace(0, 2*np.pi, n, endpoint=False)
        
        # Separate by path
        path_a_indices = [i for i, item in enumerate(items) if item.is_path_a]
        path_b_indices = [i for i, item in enumerate(items) if item.is_path_b]
        
        # Position nodes
        x_a = np.cos(theta[path_a_indices]) * 2
        y_a = np.sin(theta[path_a_indices]) * 2
        z_a = np.zeros(len(path_a_indices))
        
        x_b = np.cos(theta[path_b_indices]) * 2
        y_b = np.sin(theta[path_b_indices]) * 2
        z_b = np.ones(len(path_b_indices)) * 1.5
        
        # Plot Path A nodes (blue circle)
        self.ax.scatter(x_a, y_a, z_a, s=100, c='blue', depthshade=True, label='Path A')
        for i, idx in enumerate(path_a_indices):
            self.ax.text(x_a[i], y_a[i], z_a[i], items[idx].id, fontsize=8, ha='center')
        
        # Plot Path B nodes (red circle above)
        self.ax.scatter(x_b, y_b, z_b, s=100, c='red', depthshade=True, label='Path B')
        for i, idx in enumerate(path_b_indices):
            self.ax.text(x_b[i], y_b[i], z_b[i], items[idx].id, fontsize=8, ha='center')
        
        # Add connections within paths
        for i in range(len(path_a_indices) - 1):
            self.ax.plot(
                [x_a[i], x_a[i+1]], 
                [y_a[i], y_a[i+1]], 
                [z_a[i], z_a[i+1]], 
                'b-', alpha=0.3
            )
        
        for i in range(len(path_b_indices) - 1):
            self.ax.plot(
                [x_b[i], x_b[i+1]], 
                [y_b[i], y_b[i+1]], 
                [z_b[i], z_b[i+1]], 
                'r-', alpha=0.3
            )
        
        # Add cross-path connections for similar BETs
        # (This would be based on actual dependency analysis)
        
        # Current items highlight
        current = self.data.get_current_items()
        for path, item_id in current.items():
            if item_id:
                for i, item in enumerate(items):
                    if item.id == item_id:
                        px = x_a[i//2] if item.is_path_a else x_b[i//2]
                        py = y_a[i//2] if item.is_path_a else y_b[i//2]
                        pz = z_a[i//2] if item.is_path_a else z_b[i//2]
                        self.ax.scatter(px, py, pz, s=300, c='gold', marker='*', depthshade=True)
        
        self.ax.set_xlim([-3, 3])
        self.ax.set_ylim([-3, 3])
        self.ax.set_zlim([-0.5, 2.5])
        self.ax.set_title('VIBRASIM Network Graph - BET Dependencies', fontsize=14)
        self.ax.legend()
    
    def animate(self, frame):
        """Animation update."""
        self.ax.view_init(elev=20, azim=frame * 2)
        return self.ax,
    
    def run(self):
        """Run the 3D network graph animation."""
        if not HAS_MATPLOTLIB:
            print(f"Matplotlib not available: {MATPLOTLIB_ERROR}")
            return
        
        self.fig = plt.figure(figsize=(12, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.create_network()
        
        # Animation
        ani = FuncAnimation(
            self.fig, 
            self.animate, 
            frames=180, 
            interval=50,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return ani


class RadarChart3D:
    """3D Radar Chart - Multi-dimensional progress."""
    
    def __init__(self, data: ResearchData):
        self.data = data
        self.fig = None
        self.ax = None
    
    def create_radar(self):
        """Create 3D radar chart for brain-advantage benchmarks."""
        benchmarks = self.data.brain_benchmarks
        
        # Create circular grid
        categories = [b.get("name", "") for b in benchmarks]
        n = len(categories)
        angles = np.linspace(0, 2*np.pi, n, endpoint=False).tolist()
        angles += angles[:1]
        
        # Current progress (placeholder - would be actual data)
        progress = [0.4, 0.6, 0.3, 0.7, 0.5]  # Example values
        progress += progress[:1]
        
        # Plot
        for i in range(n):
            # Draw lines from center to each point
            self.ax.plot(
                [0, np.cos(angles[i]) * progress[i]],
                [0, np.sin(angles[i]) * progress[i]],
                [0, 0],
                'b-', alpha=0.3
            )
        
        # Fill area
        x = [np.cos(a) * p for a, p in zip(angles, progress)]
        y = [np.sin(a) * p for a, p in zip(angles, progress)]
        z = [0] * len(x)
        self.ax.plot_surface(
            [x], [y], [z], 
            color='blue', alpha=0.3
        )
        
        # Add labels
        for i, cat in enumerate(categories):
            self.ax.text(
                np.cos(angles[i]) * 1.2,
                np.sin(angles[i]) * 1.2,
                0,
                cat[:15],
                fontsize=9,
                ha='center'
            )
        
        self.ax.set_xlim([-1.5, 1.5])
        self.ax.set_ylim([-1.5, 1.5])
        self.ax.set_zlim([0, 1])
        self.ax.set_title('VIBRASIM Brain-Advantage Benchmarks Progress', fontsize=14)
        self.ax.set_aspect('equal')
    
    def animate(self, frame):
        """Animation update - pulse effect."""
        self.ax.view_init(elev=20, azim=frame * 2)
        return self.ax,
    
    def run(self):
        """Run the 3D radar chart animation."""
        if not HAS_MATPLOTLIB:
            print(f"Matplotlib not available: {MATPLOTLIB_ERROR}")
            return
        
        self.fig = plt.figure(figsize=(10, 10))
        self.ax = self.fig.add_subplot(111, projection='3d')
        
        self.create_radar()
        
        # Animation
        ani = FuncAnimation(
            self.fig, 
            self.animate, 
            frames=180, 
            interval=50,
            blit=False
        )
        
        plt.tight_layout()
        plt.show()
        return ani


def main():
    """Main entry point for 3D visualizations."""
    parser = argparse.ArgumentParser(
        description='3D Innovative Animations for Dual-Path Research'
    )
    parser.add_argument(
        '--type', '-t', type=str, default='brain',
        choices=['brain', 'tower', 'landscape', 'network', 'radar'],
        help='Type of 3D visualization (default: brain)'
    )
    parser.add_argument(
        '--repo', type=str, default=None,
        help='Path to vibrasim repository'
    )
    parser.add_argument(
        '--static', action='store_true',
        help='Show static image, no animation'
    )
    parser.add_argument(
        '--save', type=str, default=None,
        help='Save animation to HTML file'
    )
    
    args = parser.parse_args()
    
    if not HAS_MATPLOTLIB:
        print(f"Error: matplotlib not available - {MATPLOTLIB_ERROR}")
        print("\nTo install: source .venv/bin/activate && pip install matplotlib numpy")
        sys.exit(1)
    
    # Load data
    try:
        data = ResearchData(repo=Path(args.repo) if args.repo else None)
    except Exception as e:
        print(f"Error loading data: {e}")
        sys.exit(1)
    
    # Select visualization type
    viz_types = {
        'brain': Brain3D,
        'tower': ProgressTower3D,
        'landscape': ResearchLandscape3D,
        'network': NetworkGraph3D,
        'radar': RadarChart3D,
    }
    
    viz_class = viz_types.get(args.type, Brain3D)
    viz = viz_class(data)
    
    # Run visualization
    if args.static:
        # Run once without animation
        ani = viz.run()
        if ani:
            plt.show(block=True)
    else:
        ani = viz.run()
        
        # Save if requested
        if args.save:
            try:
                ani.save(args.save, writer='html', fps=30)
                print(f"Saved animation to: {args.save}")
            except Exception as e:
                print(f"Error saving: {e}")


if __name__ == '__main__':
    main()
