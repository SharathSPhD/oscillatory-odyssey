# Installation Guide

This guide explains how to set up the Oscillatory Odyssey project with Jupyter notebook functionality.

## Requirements

- Python 3.7-3.9 (Python 3.8 recommended)
- pip (latest version)

## Installation Options

Two installation options are available:

1. **Core** (default): Includes only dependencies needed for running the Jupyter notebook simulations
2. **Full**: Includes all dependencies including Jupyter Book for publishing

## Quick Installation

### Windows

1. Run the setup script with the appropriate option:
   ```
   # Core installation (default)
   setup-env.bat
   
   # Full installation with Jupyter Book
   setup-env.bat full
   ```

2. After installation completes, start Jupyter notebook:
   ```
   jupyter notebook notebooks\parametric_swing_demo.ipynb
   ```

### macOS/Linux

1. Run the setup script with the appropriate option:
   ```bash
   chmod +x setup-env.sh
   
   # Core installation (default)
   ./setup-env.sh
   
   # Full installation with Jupyter Book
   ./setup-env.sh full
   ```

2. After installation completes, start Jupyter notebook:
   ```bash
   jupyter notebook notebooks/parametric_swing_demo.ipynb
   ```

## Manual Installation

If the setup script doesn't work, you can manually install the components:

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

2. Upgrade pip:
   ```bash
   python -m pip install --upgrade pip
   ```

3. Install dependencies:
   ```bash
   # Core dependencies only
   pip install -r requirements-core.txt
   
   # Or full dependencies including Jupyter Book
   pip install -r requirements.txt
   ```

4. Register the kernel:
   ```bash
   python -m ipykernel install --user --name=oscillatory-odyssey
   ```

## Building the Jupyter Book

After installing the full dependencies, you can build the Jupyter Book:

```bash
jupyter-book build .
```

The built book will be available in the `_build/html` directory.

## Troubleshooting

### Windows Dependency Issues

If you encounter issues with `pywinpty` during installation:

1. Try installing a pre-built wheel:
   ```bash
   pip install --only-binary=:all: pywinpty==1.0.1
   ```

2. If that doesn't work, you can install Rust and try again:
   ```bash
   # Install Rust from https://rustup.rs/
   pip install pywinpty
   ```

### Jupyter Kernel Not Found

If the Jupyter kernel isn't available:

```bash
python -m ipykernel install --user --name=oscillatory-odyssey
```

### Version Conflicts

If you see package version conflicts, try installing the core packages first:

```bash
pip install numpy==1.22.4 scipy==1.8.1 matplotlib==3.5.3 plotly==5.10.0
pip install notebook==6.4.12 ipywidgets==7.6.5 ipykernel==6.9.1
```
