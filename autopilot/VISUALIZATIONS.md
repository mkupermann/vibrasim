# 3D Innovative Animations for Dual-Path Research

This directory contains multiple visualization tools for monitoring the dual-path autopilot research progress in real-time.

## Visualization Types

### 1. **3D Brain Model** (`--type brain`)
**Concept**: A rotating 3D brain with neural activity points representing BET items.

**Features**:
- Gray ellipsoid brain shape
- Colored neural activity points (scatter plot)
- Path A items on left hemisphere, Path B on right
- Height = success rate (status_height)
- Size = number of attempts
- Color = status (gold=queued, blue=running, green=passed, cyan=null, red=failed)
- Continuous 360° rotation

**Interpretation**:
- Dense activity = many BETs running
- High points = passed/null items (success)
- Low points = failed items
- Colors show current state of each research neuron

**Command**:
```bash
source .venv/bin/activate
python3 autopilot/visualize_3d.py --type brain
```

---

### 2. **3D Progress Towers** (`--type tower`)
**Concept**: Two towers (Path A and Path B) with stacked blocks for each BET item.

**Features**:
- Left tower = Path A (Elimination)
- Right tower = Path B (Differentiation)
- Each BET = one colored cube
- Height = status (running taller than queued, passed tallest)
- Color = status
- Real-time updates as BETs change status

**Interpretation**:
- Tower height = number of BETs
- Block height = success level
- Colors show distribution of outcomes
- Gaps = completed BETs that moved to archive

**Command**:
```bash
python3 autopilot/visualize_3d.py --type tower
```

---

### 3. **3D Research Landscape** (`--type landscape`)
**Concept**: A terrain map where peaks represent successful BETs.

**Features**:
- 3D terrain with hills and valleys
- Peaks at each BET position
- Peak height = status_height
- Path A on left side, Path B on right
- Current running items = red star markers with labels
- Smooth terrain with gradient coloring

**Interpretation**:
- Mountain range = research progress
- Tall peaks = successful BETs (passed)
- Short peaks = null or failed
- Red stars = currently running experiments

**Command**:
```bash
python3 autopilot/visualize_3d.py --type landscape
```

---

### 4. **3D Network Graph** (`--type network`)
**Concept**: A 3D network showing BET dependencies and connections.

**Features**:
- Path A BETs = blue nodes in lower circle
- Path B BETs = red nodes in upper circle
- Connections between sequential BETs
- Current running items = gold stars
- Interactive rotation and zoom
- Node labels = BET IDs

**Interpretation**:
- Blue circle = Path A research chain
- Red circle = Path B research chain
- Lines = dependency/conceptual connections
- Gold stars = active experiments
- Spatial separation = different research paths

**Command**:
```bash
python3 autopilot/visualize_3d.py --type network
```

---

### 5. **3D Radar Chart** (`--type radar`)
**Concept**: A radar chart showing progress on Brain-Advantage benchmarks.

**Features**:
- 5 axes for the 5 benchmarks:
  1. Continual Learning
  2. Energy Efficiency
  3. Distribution Shift Robustness
  4. Unsupervised Discovery
  5. Sensorimotor Grounding
- Current progress values
- LLM baseline vs target comparison
- Animated rotation
- Filled area showing overall capability

**Interpretation**:
- Distance from center = progress on benchmark
- Outer ring = target value
- Inner area = current achievement
- Goal: Fill the entire radar area

**Command**:
```bash
python3 autopilot/visualize_3d.py --type radar
```

---

## Color Coding (All Visualizations)

| Status | Color | Meaning |
|--------|-------|---------|
| queued | Gold (1.0, 0.8, 0.0) | Waiting to run |
| running | Blue (0.0, 0.5, 1.0) | Currently executing |
| passed | Green (0.0, 1.0, 0.0) | Success! |
| null | Light Blue (0.5, 0.5, 1.0) | Partial/informative failure |
| failed | Red (1.0, 0.0, 0.0) | Hard failure |

---

## Usage Examples

### Run a specific visualization
```bash
source .venv/bin/activate
python3 autopilot/visualize_3d.py --type brain
```

### Run static (no animation)
```bash
python3 autopilot/visualize_3d.py --type tower --static
```

### Save to HTML
```bash
python3 autopilot/visualize_3d.py --type landscape --save research.html
```

### Cycle through all types
```bash
for type in brain tower landscape network radar; do
  echo "=== $type ==="
  python3 autopilot/visualize_3d.py --type $type --static
  sleep 3
  clear
done
```

---

## Interactive Controls

All 3D visualizations support interactive controls (when using matplotlib Tk/Qt backend):

**Mouse Controls:**
- **Left-click + drag**: Rotate the view
- **Right-click + drag**: Pan the view
- **Scroll wheel**: Zoom in/out

**Keyboard Controls:**
- **q**: Quit/close the window
- **r**: Reset view to default

---

## Requirements

- Python 3.8+
- matplotlib
- numpy

Install with:
```bash
source .venv/bin/activate
pip install matplotlib numpy
```

---

## Data Source

All visualizations read from:
- `~/.eqmod/autopilot/path_a/queue.yaml` - Path A BET items
- `~/.eqmod/autopilot/path_b/queue.yaml` - Path B BET items
- `~/.eqmod/autopilot/path_a/current_item.txt` - Currently running A
- `~/.eqmod/autopilot/path_b/current_item.txt` - Currently running B

---

## Performance

- **Refresh rate**: 20 FPS (50ms interval)
- **Rotation**: 2° per frame = 360° every 9 seconds
- **Memory**: ~100-200 MB per window
- **CPU**: Minimal (rendering is GPU-accelerated if available)

---

## Customization

Modify `autopilot/visualize_3d.py` to:
- Change colors in `BETItem.status_color`
- Adjust sizes in `BETItem.status_height`
- Modify rotation speed in `animate()` methods
- Add new visualization types

---

## Philosophy

These visualizations transform abstract research progress into tangible, intuitive 3D forms:

- **Brain Model**: Research as neural activity - fitting for a brain-inspired project
- **Progress Towers**: Research as construction - building knowledge block by block
- **Research Landscape**: Research as exploration - climbing the mountains of knowledge
- **Network Graph**: Research as connection - linking ideas and findings
- **Radar Chart**: Research as capability - expanding the boundaries of what's possible

Each visualization tells a different story about the same data, providing multiple perspectives on the dual-path research progress.
