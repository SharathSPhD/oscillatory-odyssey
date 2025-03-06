# Virtual Environment Setup

This document explains how to set up a Python virtual environment for the Oscillatory Odyssey project.

## Requirements

- Python 3.8 recommended (compatible with Python 3.7-3.9)
- pip (latest version)

## Setting Up the Virtual Environment

### 1. Create a virtual environment

```bash
# Navigate to the project directory
cd oscillatory-odyssey

# Create a virtual environment
python -m venv venv
```

### 2. Activate the virtual environment

#### On Windows:
```bash
venv\Scripts\activate
```

#### On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
pip list
```

## Jupyter Notebook Configuration

### 1. Register the virtual environment as a Jupyter kernel

```bash
python -m ipykernel install --user --name=oscillatory-odyssey
```

### 2. Enable Jupyter extensions (for interactive features)

```bash
# Enable widget extensions
jupyter nbextension enable --py widgetsnbextension

# For JupyterLab users
jupyter labextension install jupyterlab-plotly
```

## Running the Notebook

```bash
# Start Jupyter Notebook
jupyter notebook notebooks/parametric_swing_demo.ipynb
```

When the notebook opens, select the "oscillatory-odyssey" kernel from the kernel menu to ensure all dependencies are available.

## Troubleshooting

### Missing interactive widgets

If the interactive widgets don't display properly:

```bash
# Ensure ipywidgets is properly installed
pip install ipywidgets>=7.6.0

# Reinstall and enable the extension
jupyter nbextension install --py widgetsnbextension
jupyter nbextension enable --py widgetsnbextension
```

### Plotly figures not showing

For issues with Plotly visualizations:

```bash
# Reinstall Plotly with complete dependencies
pip install plotly>=5.3.0 --force-reinstall
```

### Version conflicts

If you encounter package version conflicts:

```bash
# Create a fresh virtual environment
deactivate
rm -rf venv
python -m venv venv
# Activate and reinstall
```

## Building the Jupyter Book

```bash
# Install jupyter-book if not already installed
pip install jupyter-book

# Build the book
jupyter-book build .

# The output will be in _build/html/
```

## Deactivating the Virtual Environment

When you're done working with the project:

```bash
deactivate
```
