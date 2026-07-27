#!/bin/bash
# Master script to start all visualizations
# Auto-detects the best Python environment and backend

echo "=========================================="
echo "  VIBRASIM Visualization Control Center"
echo "=========================================="
echo ""

# Find the best Python
if python3 -c "import matplotlib; import _tkinter" 2>/dev/null; then
    PYTHON=python3
    echo "✓ Using system Python with Tkinter"
elif /Users/mkupermann/Documents/GitHub/vibrasim/.venv/bin/python3 -c "import matplotlib; import _tkinter" 2>/dev/null; then
    PYTHON="/Users/mkupermann/Documents/GitHub/vibrasim/.venv/bin/python3"
    echo "✓ Using venv Python with Tkinter"
elif python3 -c "import matplotlib; import _tkinter" 2>/dev/null; then
    PYTHON=python3
    echo "✓ Using system Python with Tkinter"
else
    echo "✗ No working Python with matplotlib + Tkinter found"
    echo "  Install with: brew install python-tk && python3 -m pip install --break-system-packages matplotlib numpy"
    exit 1
fi

echo ""
echo "Select visualization type:"
echo "-------------------------"
echo "  1) 3D Brain Model (rotating brain with neural activity)"
echo "  2) 3D Progress Towers (stacked BET blocks)"
echo "  3) 3D Research Landscape (terrain with peaks)"
echo "  4) 3D Network Graph (BET dependencies)"
echo "  5) 3D Radar Chart (brain-advantage benchmarks)"
echo "  6) ASCII Terminal (2D, zero dependencies)"
echo "  7) All 3D visualizations in sequence"
echo "  8) Exit"
echo ""
echo -n "Choose (1-8): "
read choice

echo ""

case $choice in
    1)
        echo "Starting 3D Brain Model..."
        $PYTHON autopilot/visualize_3d.py --type brain
        ;;
    2)
        echo "Starting 3D Progress Towers..."
        $PYTHON autopilot/visualize_3d.py --type tower
        ;;
    3)
        echo "Starting 3D Research Landscape..."
        $PYTHON autopilot/visualize_3d.py --type landscape
        ;;
    4)
        echo "Starting 3D Network Graph..."
        $PYTHON autopilot/visualize_3d.py --type network
        ;;
    5)
        echo "Starting 3D Radar Chart..."
        $PYTHON autopilot/visualize_3d.py --type radar
        ;;
    6)
        echo "Starting ASCII Terminal Visualization..."
        $PYTHON autopilot/visualize.py
        ;;
    7)
        echo "Starting all 3D visualizations in sequence..."
        for type in brain tower landscape network radar; do
            echo "=== $type ==="
            $PYTHON autopilot/visualize_3d.py --type $type --static
            sleep 3
        done
        ;;
    8)
        echo "Goodbye!"
        exit 0
        ;;
    *)
        echo "Invalid choice. Please select 1-8."
        ;;
esac
