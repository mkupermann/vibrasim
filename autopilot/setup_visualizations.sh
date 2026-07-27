#!/bin/bash
# Setup script for 3D visualizations
# Installs all dependencies and configures the environment

set -e

echo "=========================================="
echo "Setting up 3D Visualizations for VIBRASIM"
echo "=========================================="
echo ""

# Step 1: Install system dependencies
echo "[1/4] Installing system dependencies..."
if ! brew list python-tk &>/dev/null; then
    brew install python-tk
    echo "  ✓ python-tk installed"
else
    echo "  ✓ python-tk already installed"
fi

# Step 2: Install Python packages in system Python
echo ""
echo "[2/4] Installing Python packages..."
python3 -m pip install --break-system-packages matplotlib numpy 2>/dev/null || \
    python3 -m pip install --user matplotlib numpy 2>/dev/null || \
    echo "  ⚠ Could not install to system Python, using venv instead"

# Verify installation
echo ""
echo "[3/4] Verifying installations..."

# Check system Python
if python3 -c "import matplotlib; import _tkinter; print('OK')" 2>/dev/null; then
    echo "  ✓ System Python: matplotlib + Tkinter available"
    PYTHON_CMD="python3"
else
    echo "  ⚠ System Python: missing dependencies, trying venv..."
    VENV_PYTHON="/Users/mkupermann/Documents/GitHub/vibrasim/.venv/bin/python3"
    if $VENV_PYTHON -c "import matplotlib; import _tkinter; print('OK')" 2>/dev/null; then
        echo "  ✓ Venv Python: matplotlib + Tkinter available"
        PYTHON_CMD="$VENV_PYTHON"
    else
        echo "  ❌ No working Python environment found"
        exit 1
    fi
fi

# Step 4: Create convenience scripts
echo ""
echo "[4/4] Creating convenience scripts..."

# Create run_3d.sh wrapper
cat > /tmp/run_3d.sh << 'WRAPPER'
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
WRAPPER

chmod +x /tmp/run_3d.sh
cp /tmp/run_3d.sh autopilot/run_3d.sh 2>/dev/null || true

# Create aliases
cat >> ~/.zshrc << 'ALIASES'

# VIBRASIM 3D Visualizations
alias vibrasim-3d="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py"
alias vibrasim-3d-brain="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py --type brain"
alias vibrasim-3d-tower="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py --type tower"
alias vibrasim-3d-landscape="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py --type landscape"
alias vibrasim-3d-network="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py --type network"
alias vibrasim-3d-radar="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize_3d.py --type radar"
alias vibrasim-ascii="cd /Users/mkupermann/Documents/GitHub/vibrasim && python3 autopilot/visualize.py"
ALIASES

echo "  ✓ Convenience scripts created"
echo "  ✓ Aliases added to ~/.zshrc"

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "To use the 3D visualizations:"
echo ""
echo "  # Brain model (rotating)"
echo "  python3 autopilot/visualize_3d.py --type brain"
echo ""
echo "  # Progress towers"
echo "  python3 autopilot/visualize_3d.py --type tower"
echo ""
echo "  # Research landscape"
echo "  python3 autopilot/visualize_3d.py --type landscape"
echo ""
echo "  # Network graph"
echo "  python3 autopilot/visualize_3d.py --type network"
echo ""
echo "  # Radar chart"
echo "  python3 autopilot/visualize_3d.py --type radar"
echo ""
echo "  # ASCII visualization (no dependencies)"
echo "  python3 autopilot/visualize.py"
echo ""
echo "Or use the aliases (after restarting terminal):"
echo "  vibrasim-3d --type brain"
echo "  vibrasim-ascii"
echo ""
echo "=========================================="
