# Oscillatory Odyssey Jupyter Book

This directory contains the Jupyter Book version of the Oscillatory Odyssey series, which explores the physics of oscillations, rotations, and resonance through an engaging narrative.

## Directory Structure

- `notebooks/`: Contains the Jupyter notebooks (linked to original notebooks)
- `images/`: Contains images used in the notebooks
- `videos/`: Contains videos used in the notebooks
- `.github/workflows/`: Contains GitHub Actions workflow for deployment

## Building the Book

### Prerequisites

1. Install the required dependencies:
```
pip install -r requirements.txt
```

   If you encounter dependency errors (especially related to myst-parser and myst-nb), run the fix script:
   ```
   fix_dependencies.bat
   ```
   This will install compatible versions of the required packages.

2. Set up the symbolic links and copy required media files (Windows):
```
setup_links.bat
```

3. Modify notebook paths for Jupyter Book:
```
python modify_notebook_paths.py
```

### Build Command

To build the book locally:
```
jupyter-book build .
```

The built book will be in the `_build/html/` directory.

## Deployment

The book is automatically deployed to GitHub Pages when changes are pushed to the main branch.

To deploy manually:
1. Build the book: `jupyter-book build .`
2. Install ghp-import: `pip install ghp-import`
3. Deploy: `ghp-import -n -p -f _build/html`

## Interactive Features

This Jupyter Book uses Thebe to enable code execution directly in the browser. This means you can interact with the code cells and run them without leaving the book.

## Credits

- Original content by [Your Name]
- Built with [Jupyter Book](https://jupyterbook.org/)
