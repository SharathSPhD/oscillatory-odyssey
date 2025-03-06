# GitHub Repository Setup for Oscillatory Odyssey

The following instructions will help you set up your GitHub repository correctly to ensure the interactive components work with Thebe.

## Files to Include

For your repository to work correctly with Thebe and interactive Jupyter notebooks, you need to include these essential components:

1. **The built Jupyter Book content**:
   - `jupyter_book/_build/` directory

2. **The Python module files**:
   - `jupyter_book/oscillatory_odyssey/` directory with all Python files

3. **Supporting media and content**:
   - `jupyter_book/images/` directory
   - `jupyter_book/videos/` directory
   - Original notebooks in `jupyter_book/notebooks/` (recommended)

4. **Configuration and dependencies**:
   - `jupyter_book/_config.yml` (already updated with Thebe settings)
   - `requirements.txt` at the root level
   - `.gitignore` (to exclude unnecessary files)
   - `README.md` (project documentation)

## Git Commands

```bash
# Navigate to your project directory
cd E:\Development\oscillatory-odyssey

# Initialize git repository
git init

# Add the Python module files (essential for interactive functionality)
git add jupyter_book/oscillatory_odyssey/

# Add the built Jupyter Book
git add jupyter_book/_build/

# Add supporting content
git add jupyter_book/images/
git add jupyter_book/videos/
git add jupyter_book/notebooks/
git add jupyter_book/_config.yml
git add jupyter_book/_toc.yml

# Add project files
git add requirements.txt
git add README.md
git add .gitignore

# Commit the changes
git commit -m "Initial commit of Oscillatory Odyssey with interactive components"

# Add the remote repository
git remote add origin https://github.com/SharathSPhD/oscillatory-odyssey.git

# Push to GitHub
git push -u origin main
```

## Important Note About Structure

The repository structure is critical for interactive functionality. The notebooks import the `oscillatory_odyssey` module using relative paths:

```python
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

# Import our custom modules
from oscillatory_odyssey.foucault import FoucaultPendulum
```

This means the `oscillatory_odyssey` module must be in the parent directory of the notebooks in the same relative location as in your local setup.

## After Deployment

Once your repository is set up on GitHub:

1. Verify that all files have been pushed correctly
2. Test the Thebe integration by accessing your published Jupyter Book
3. Ensure interactive elements work as expected

If you encounter any issues with the interactive components, check that:
- The directory structure matches what's described above
- All Python module files are present in the correct location
- The `_config.yml` has the proper Thebe configuration pointing to your repository
