# Thebe Troubleshooting Guide

## Diagnostic Tools Created

1. **Debug Page**: Open `debug/index.html` to test Thebe in a minimal environment
2. **Direct Tester**: Open `thebe_tester.html` to test Thebe without Sphinx integration
3. **Console Logging**: Enhanced debug messages in browser console (press F12 to view)
4. **Diagnostic Button**: Look for "Thebe Diagnostics" button in the bottom-right corner

## Common Issues and Solutions

### JavaScript Console Errors

If you see errors in the browser console:

- **CORS Errors**: Indicates cross-origin issues. Try running from a web server instead of file:// URLs
- **404 Errors for Thebe**: Indicates the CDN or local path is incorrect
- **Undefined Function Errors**: May indicate loading order issues

### Binder Connection Issues

If Thebe initializes but can't connect to Binder:

1. Check your network connection and firewall settings
2. Try a different Binder repository in the configuration
3. Verify if mybinder.org is accessible from your network

### Cell Detection Issues

If Thebe loads but can't find code cells:

1. Check the HTML structure to see if cells have the expected classes
2. Try adding the 'thebe' class manually to cells
3. Verify the selectors match your document structure

## Alternative Solutions

1. **Use Local Kernel**: Configure Thebe to use a local Jupyter kernel instead of Binder
2. **Simplify Content**: Reduce complexity of pages to isolate the issue
3. **Try Different Versions**: Test with older versions of Thebe (0.7.1, 0.5.1)

## Getting Help

If problems persist:
- Check the log file: `thebe_fix_log_*.txt` in this directory
- Visit [Thebe GitHub Issues](https://github.com/executablebooks/thebe/issues)
- Check [Jupyter Book Documentation](https://jupyterbook.org/interactive/thebe.html)
