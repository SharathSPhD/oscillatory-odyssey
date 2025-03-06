
// Enhanced helper functions for ThebeLab config with error handling and debugging
function initThebeSBT() {
    console.log("Initializing Thebe with enhanced helper...");
    
    try {
        // Load the Thebe library
        const THEBE_JS_URL = "../_static/thebe_versions/thebe-0.8.2.js";
        const FALLBACK_THEBE_JS_URL = "https://unpkg.com/thebe@0.8.2/lib/index.js";
        
        // Remove any existing thebe script to avoid duplicates
        const existingScript = document.querySelector('script[src="' + THEBE_JS_URL + '"]');
        if (existingScript) {
            console.log("Removing existing Thebe script");
            existingScript.remove();
        }
        
        // Add the script with error handling
        const thebeScript = document.createElement('script');
        thebeScript.src = THEBE_JS_URL;
        
        // Add error handling for the script loading
        thebeScript.onerror = function() {
            console.warn("Failed to load Thebe from local path, trying CDN fallback");
            const fallbackScript = document.createElement('script');
            fallbackScript.src = FALLBACK_THEBE_JS_URL;
            
            fallbackScript.onload = initThebeAfterLoad;
            fallbackScript.onerror = function() {
                console.error("Failed to load Thebe from both local and CDN paths");
                document.body.insertAdjacentHTML('afterbegin', 
                    '<div style="background: #ffebee; color: #c62828; padding: 10px; margin: 10px 0; border-left: 3px solid #c62828;">' +
                    '<strong>Error:</strong> Failed to load Thebe JavaScript library. Interactive code execution is not available.' +
                    '</div>');
            };
            document.head.appendChild(fallbackScript);
        };
        
        thebeScript.onload = initThebeAfterLoad;
        document.head.appendChild(thebeScript);
        
        // Add classes to identify cells for Thebe
        document.querySelectorAll('div.cell').forEach(cell => {
            cell.classList.add('thebe');
        });
        
        console.log("Thebe initialization script added to page");
    } catch (error) {
        console.error("Error in initThebeSBT:", error);
    }
}

function initThebeAfterLoad() {
    console.log("Thebe library loaded, bootstrapping...");
    try {
        // Get configuration from data attributes
        const binderOptions = {
            repo: "binder-examples/jupyter-stacks-datascience",
            ref: "master"
        };
        
        console.log("Initializing thebe with options:", {
            binderOptions: binderOptions,
            kernelOptions: {
                name: "python3",
                path: "./notebooks"
            },
            selector: ".thebe, .cell, .jp-Cell, .jupyter-cell, .tag_thebe-init",
            requestKernel: true,
            mountActivateWidget: true,
            predefinedOutput: true,
            stripPrompts: true,
            debug: true
        });
        
        // Initialize Thebe with robust error handling
        try {
            thebelab.bootstrap({
                binderOptions: binderOptions,
                kernelOptions: {
                    name: "python3",
                    path: "./notebooks"
                },
                selector: ".thebe, .cell, .jp-Cell, .jupyter-cell, .tag_thebe-init",
                requestKernel: true,
                mountActivateWidget: true,
                predefinedOutput: true,
                stripPrompts: true,
                debug: true
            });
            console.log("Thebe bootstrap called successfully");
        } catch (bootstrapError) {
            console.error("Error bootstrapping Thebe:", bootstrapError);
        }
    } catch (error) {
        console.error("Error in initThebeAfterLoad:", error);
    }
}

// Create a diagnostic button in the corner to help with debugging
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Create diagnostic button
        const diagButton = document.createElement('button');
        diagButton.innerHTML = 'Thebe Diagnostics';
        diagButton.style.cssText = 'position: fixed; bottom: 10px; right: 10px; z-index: 1000; padding: 5px;';
        diagButton.onclick = function() {
            const diagInfo = {
                'Thebe Loaded': typeof thebelab !== 'undefined',
                'jQuery Loaded': typeof jQuery !== 'undefined',
                'Window Size': window.innerWidth + 'x' + window.innerHeight,
                'User Agent': navigator.userAgent,
                'Thebe Elements': document.querySelectorAll('.thebe, .cell').length,
                'Thebe Buttons': document.querySelectorAll('.thebelab-button').length
            };
            
            console.log('Thebe Diagnostics:', diagInfo);
            alert('Thebe Diagnostics: Check browser console for details');
        };
        document.body.appendChild(diagButton);
    } catch (error) {
        console.error("Error adding diagnostic button:", error);
    }
});
