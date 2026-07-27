#!/bin/bash
# Wrapper script to run 3D visualizations with correct Python

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"

# Try system Python first, then venv
if python3 -c "import matplotlib; import _tkinter" 2>/dev/null; then
    PYTHON=python3
else
    PYTHON="/Users/mkupermann/Documents/GitHub/vibrasim/.venv/bin/python3"
fi

# Check if matplotlib backend needs to be set
if [ -z "$DISPLAY" ] && [ "$PYTHON" = "python3" ]; then
    # No display, try WebAgg
    $PYTHON -c "import matplotlib; matplotlib.use('WebAgg')" 2>/dev/null
fi

exec $PYTHON "$REPO_DIR/autopilot/visualize_3d.py" "$@"
