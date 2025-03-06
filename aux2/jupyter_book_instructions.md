# Jupyter Book Conversion Instructions

This document outlines the steps to complete the conversion of Oscillatory Odyssey into a Jupyter Book with interactive content.

## What Has Been Set Up

1. **Directory Structure**:
   - `jupyter_book/`: Main directory for the Jupyter Book
   - `jupyter_book/images/`: Directory for images
   - `jupyter_book/videos/`: Directory for videos
   - `jupyter_book/notebooks/`: Directory for notebook copies with modified paths
   - `jupyter_book/.github/workflows/`: GitHub Actions workflow directory

2. **Configuration Files**:
   - `_config.yml`: Main configuration file with Thebe integration enabled
   - `_toc.yml`: Table of contents structure
   - `intro.md`: Landing page for the book
   - `requirements.txt`: Required dependencies
   - `.gitignore`: Git ignore patterns
   - `setup_links.bat`: Script to set up symbolic links (Windows)
   - `modify_notebook_paths.py`: Script to update media paths in notebooks
   - `README.md`: Instructions for using the Jupyter Book

3. **GitHub Actions**:
   - `deploy-book.yml`: Workflow for automatic deployment to GitHub Pages

4. **Media Files**:
   - Images copied to `jupyter_book/images/`
   - Videos copied to `jupyter_book/videos/`

5. **Package Installation**:
   - `setup.py`: Setup file for installing the oscillatory_odyssey module

## Next Steps to Complete

1. **Run the Path Modification Script**:
   ```
   python jupyter_book/modify_notebook_paths.py
   ```
   This will create modified copies of the notebooks with updated paths for images, videos, and linked notebooks.

2. **Test Build Locally**:
   ```
   cd jupyter_book
   jupyter-book build .
   ```
   Check the `_build/html/` directory to verify the book builds correctly.

3. **Set Up GitHub Repository**:
   - Create a new GitHub repository for the project
   - Push the entire directory structure to GitHub
   - Configure GitHub Pages in the repository settings

4. **Test Interactive Features**:
   - Open the built book in a browser
   - Verify that Thebe integration works by executing code cells
   - Check that images and videos display correctly
   - Ensure navigation between notebooks works properly

## Troubleshooting

### Dependency Compatibility Issues

If you encounter dependency errors with Jupyter Book, it's important to install compatible versions. I've provided two ways to fix this:

1. **Using the fix script:**
   ```
   fix_dependencies.bat
   ```

2. **Manual installation:**
   ```
   pip uninstall -y myst-parser myst-nb jupyter-book sphinx
   pip install jupyter-book==0.13.1
   pip install sphinx==4.5.0
   pip install myst-parser==0.16.1
   pip install myst-nb==0.13.2 --no-deps
   ```

3. **Using conda environment:**
   ```
   conda env create -f environment.yml
   conda activate oscillatory-odyssey
   ```

### Other Common Issues

If you encounter other issues with the Jupyter Book build:

1. **Path Issues**: Verify that paths in notebooks are correctly updated. You might need to adjust the `modify_notebook_paths.py` script.

2. **Module Import Errors**: Make sure the oscillatory_odyssey module is properly installed with `pip install -e .` at the repository root.

3. **Media Files Not Displaying**: Check that all required media files are copied to the correct directories.

4. **Thebe Integration Issues**: Verify the Thebe configuration in `_config.yml` and ensure the required JavaScript dependencies are loaded.

## Additional Resources

- [Jupyter Book Documentation](https://jupyterbook.org/)
- [MyST Markdown Reference](https://myst-parser.readthedocs.io/en/latest/)
- [Thebe Documentation](https://thebe.readthedocs.io/en/latest/)
- [GitHub Pages Documentation](https://docs.github.com/en/pages)