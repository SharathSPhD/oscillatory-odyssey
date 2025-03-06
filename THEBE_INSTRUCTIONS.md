# Thebe Instructions

## Fixed Thebe Configuration

The Thebe configuration has been updated to use a Binder repository that includes Plotly. This should fix the "ModuleNotFoundError: No module named 'plotly'" error.

## Using Thebe

1. Start the web server to avoid CORS issues:
   ```
   python -m http.server 8000
   ```

2. Open your Jupyter Book at http://localhost:8000

3. Click the "Launch Thebe" button on any page to start an interactive session.

## Troubleshooting

If you still encounter issues:

1. Check the browser console (F12) for errors
2. Try clearing your browser cache
3. Make sure you're accessing the pages through the web server, not directly as files
4. If you see module import errors, check the console for which modules are missing

## Technical Details

The fix changes the Binder repository from:
- Original: "binder-examples/jupyter-stacks-datascience"
- New: "pythondecal/plotly-dash-binder"

The new repository includes additional packages like Plotly that are required by your notebooks.
