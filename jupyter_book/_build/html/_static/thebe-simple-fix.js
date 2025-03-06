
// Simple, direct Thebe fix without reliance on internal structures
(function() {
    console.log("Simple Thebe Fix Loaded");
    
    // Wait for page to be ready
    document.addEventListener('DOMContentLoaded', function() {
        // Enhance all code cells that look like Python
        prepareCodeCells();
        
        // Wait a moment for everything to settle
        setTimeout(initThebeDirectly, 500);
    });
    
    function prepareCodeCells() {
        // Target python code blocks
        const pythonCells = document.querySelectorAll(
            "div.highlight-python pre, pre.python, .cell pre, div.highlight pre"
        );
        
        pythonCells.forEach(function(cell, index) {
            // Make sure it has the right attributes
            cell.setAttribute('data-executable', 'true');
            cell.setAttribute('data-language', 'python');
            cell.classList.add('thebe');
            
            // Give it an ID if needed
            if (!cell.id) {
                cell.id = 'cell-' + index;
            }
            
            console.log("Enhanced cell for Thebe:", cell.id);
        });
    }
    
    function initThebeDirectly() {
        console.log("Initializing Thebe directly...");
        
        // Only proceed if Thebe is loaded
        if (typeof thebelab === 'undefined') {
            console.error("Thebe not loaded, can't initialize");
            return;
        }
        
        // Apply simple, direct configuration
        const config = {
            binderOptions: {
                repo: "binder-examples/jupyter-stacks-datascience",
                ref: "master",
            },
            kernelOptions: {
                name: "python3",
                path: "./notebooks"
            },
            selector: "pre[data-executable='true'], .thebe, pre.python, div.highlight-python pre",
            requestKernel: true,
            mountActivateWidget: true,
            predefinedOutput: true
        };
        
        // Try to bootstrap with error handling
        try {
            thebelab.bootstrap(config);
            console.log("Thebe initialized successfully");
            
            // Add a visual indicator
            const indicator = document.createElement('div');
            indicator.style.cssText = 'position:fixed; bottom:10px; right:10px; background:#4CAF50; color:white; padding:5px 10px; border-radius:3px; z-index:1000;';
            indicator.textContent = 'Thebe Ready';
            document.body.appendChild(indicator);
            setTimeout(() => indicator.remove(), 3000);
        } catch (error) {
            console.error("Error initializing Thebe:", error);
            
            // Add error indicator
            const errorIndicator = document.createElement('div');
            errorIndicator.style.cssText = 'position:fixed; bottom:10px; right:10px; background:#f44336; color:white; padding:5px 10px; border-radius:3px; z-index:1000;';
            errorIndicator.textContent = 'Thebe Error: Check Console';
            document.body.appendChild(errorIndicator);
            setTimeout(() => errorIndicator.remove(), 5000);
        }
    }
})();
