# Oscillatory Odyssey Repository Structure

This document outlines the essential files and directories needed for your GitHub repository to function correctly with interactive features.

## Critical Components

### Python Module Files (Required for Interactivity)
- `jupyter_book/oscillatory_odyssey/` - Contains all Python module files
  - Core simulation modules
  - Visualization utilities
  - Interactive components

### Built Jupyter Book (For GitHub Pages)
- `jupyter_book/_build/` - The built Jupyter Book content
  - HTML files and assets
  - Interactive elements (requires the Python module files)

### Supporting Media
- `jupyter_book/images/` - Images referenced in the notebooks
- `jupyter_book/videos/` - Video files for animations

### Configuration Files
- `jupyter_book/_config.yml` - Jupyter Book configuration with Thebe settings
- `jupyter_book/_toc.yml` - Table of contents structure
- `requirements.txt` - Python dependencies
- `.gitignore` - Files to exclude from the repository
- `README.md` - Project documentation

## Directory Structure Visualization

```
oscillatory-odyssey/
├── jupyter_book/
│   ├── _build/              # HTML content
│   │   ├── html/            # Web pages
│   │   ├── jupyter_execute/ # Execution cache
│   │   └── .doctrees/       # Documentation trees
│   │
│   ├── oscillatory_odyssey/ # Python module files (CRITICAL)
│   │   ├── animation.py
│   │   ├── foucault.py
│   │   ├── gyroscope.py
│   │   └── ... (all Python files)
│   │
│   ├── notebooks/           # Original Jupyter notebooks
│   ├── images/              # Image assets
│   ├── videos/              # Video assets
│   ├── _config.yml          # Configuration
│   └── _toc.yml             # Table of contents
│
├── requirements.txt         # Dependencies
├── .gitignore               # Git ignore file
└── README.md                # Repository documentation
```

## Why This Structure Matters

The notebooks use Python import statements that expect the `oscillatory_odyssey` module to be in a specific location. For example:

```python
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from oscillatory_odyssey.foucault import FoucaultPendulum
```

This import pattern means that:
1. The `oscillatory_odyssey` module must be in the same directory as the notebooks directory
2. This relative structure must be preserved in the GitHub repository
3. When using Thebe, the same structure must be available to the runtime environment

Maintaining this structure ensures that interactive components will work correctly when users click the "Live Code" button in your published Jupyter Book.
