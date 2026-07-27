# 🚀 Quick Start: 3D Research Visualizations

Everything is now set up and working!

## What Was Installed

✅ **python-tk** - Tkinter GUI backend for matplotlib  
✅ **matplotlib** - 3D plotting library (v3.11.1)  
✅ **numpy** - Numerical computing (v2.5.1)  
✅ **All visualization scripts** - 5 different 3D animations + ASCII

## How to Use

### Option 1: Direct Commands (Recommended)

```bash
# 3D Brain Model (rotating brain with neural activity)
python3 autopilot/visualize_3d.py --type brain

# 3D Progress Towers (stacked blocks for each BET)
python3 autopilot/visualize_3d.py --type tower

# 3D Research Landscape (terrain with peaks)
python3 autopilot/visualize_3d.py --type landscape

# 3D Network Graph (BET dependencies)
python3 autopilot/visualize_3d.py --type network

# 3D Radar Chart (brain-advantage benchmarks)
python3 autopilot/visualize_3d.py --type radar

# ASCII Terminal (2D, works everywhere)
python3 autopilot/visualize.py
```

### Option 2: Interactive Menu

```bash
bash autopilot/start_visualizations.sh
```

Then select 1-8 from the menu.

### Option 3: Using Aliases (After Terminal Restart)

```bash
vibrasim-3d --type brain
vibrasim-3d-tower
vibrasim-ascii
```

## Visualization Types

| # | Type | Description | Command |
|---|------|-------------|---------|
| 1 | **Brain** | Rotating 3D brain with neural activity points | `--type brain` |
| 2 | **Tower** | Two towers with stacked BET blocks | `--type tower` |
| 3 | **Landscape** | Terrain map with peaks for successful BETs | `--type landscape` |
| 4 | **Network** | 3D graph showing BET dependencies | `--type network` |
| 5 | **Radar** | Spider chart for brain-advantage benchmarks | `--type radar` |
| 6 | **ASCII** | Terminal-based with brain art | `visualize.py` |

## Color Coding

| Status | Color | Meaning |
|--------|-------|---------|
| ✅ Passed | Green | Success! |
| ➖ Null | Light Blue | Informative failure |
| ❌ Failed | Red | Hard failure |
| ▶️ Running | Blue | Currently executing |
| ⏳ Queued | Gold | Waiting to run |

## Controls (In 3D Windows)

**Mouse:**
- **Left-click + drag** = Rotate view
- **Right-click + drag** = Pan view  
- **Scroll wheel** = Zoom in/out

**Keyboard:**
- **q** = Quit/close window
- **r** = Reset view

## Troubleshooting

### If you get "No module named '_tkinter'"
```bash
brew install python-tk
```

### If you get "No module named 'matplotlib'"
```bash
python3 -m pip install --break-system-packages matplotlib numpy
```

### To verify everything works
```bash
python3 -c "import matplotlib; matplotlib.use('TkAgg'); import _tkinter; print('All good!')"
```

## What You're Seeing

Each visualization shows **real data** from your dual-path autopilot:

- **Current running BETs** (EA-001, EA-002, DB-001, etc.)
- **Queue status** (queued, running, passed, null, failed)
- **Path A vs Path B** separation
- **Progress toward benchmarks**

The visualizations **update in real-time** as the autopilot processes items.

## Files Created

```
autopilot/
├── visualize_3d.py        # 5 x 3D visualization types
├── visualize.py          # ASCII terminal visualization
├── start_visualizations.sh  # Interactive menu
├── setup_visualizations.sh  # Setup script
├── run_3d.sh             # Wrapper script
├── paths.yaml           # Dual-path configuration
├── VISUALIZATIONS.md    # Full documentation
└── README.md             # Dual-path autopilot docs

~/.eqmod/autopilot/
├── path_a/              # Path A state
│   ├── queue.yaml       # BET items
│   ├── current_item.txt  # Currently running
│   └── dispatcher.log   # Log
└── path_b/              # Path B state
    ├── queue.yaml
    ├── current_item.txt
    └── dispatcher.log
```

## Ready to Go! ✅

Run this to see the brain:
```bash
python3 autopilot/visualize_3d.py --type brain
```

Or this for the menu:
```bash
bash autopilot/start_visualizations.sh
```
