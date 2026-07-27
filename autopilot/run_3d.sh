#!/bin/bash
# Wrapper script to run 3D visualizations with correct Python

# Get absolute path to this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# The repo is always 2 levels up from autopilot directory
# No matter where this script is run from
if [[ "$SCRIPT_DIR" == *"autopilot"* ]]; then
    # We're in the autopilot directory
    REPO_DIR="$(dirname "$SCRIPT_DIR")"
else
    # We're somewhere else, assume current directory is repo
    REPO_DIR="$SCRIPT_DIR"
fi

# Use absolute path to repo
REPO_DIR="$(cd "$REPO_DIR" && pwd)"

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

# Execute with absolute path
SCRIPT_PATH="$REPO_DIR/autopilot/visualize_3d.py"
if [ -f "$SCRIPT_PATH" ]; then
    exec $PYTHON "$SCRIPT_PATH" "$@"
else
    echo "Error: Visualization script not found at $SCRIPT_PATH"
    echo "Repository directory: $REPO_DIR"
    exit 1
fi
