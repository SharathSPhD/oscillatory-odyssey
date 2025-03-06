#!/bin/bash
echo "Setting up virtual environment for Oscillatory Odyssey..."

# Parse command line arguments
INSTALL_TYPE="core"
if [ "$1" = "full" ]; then
    INSTALL_TYPE="full"
fi

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies based on install type
if [ "$INSTALL_TYPE" = "full" ]; then
    echo "Installing full dependencies including Jupyter Book support..."
    pip install -r requirements.txt
else
    echo "Installing core dependencies for notebook usage..."
    pip install -r requirements-core.txt
fi

# Register kernel
python -m ipykernel install --user --name=oscillatory-odyssey

echo ""
echo "Setup complete! You can now run:"
echo "jupyter notebook notebooks/parametric_swing_demo.ipynb"
echo ""
echo "Make sure to select the \"oscillatory-odyssey\" kernel in the notebook."

if [ "$INSTALL_TYPE" = "full" ]; then
    echo ""
    echo "You can also build the Jupyter Book with:"
    echo "jupyter-book build ."
fi
