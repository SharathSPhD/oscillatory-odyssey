
// Custom Thebe loader with error-handling and patched initialization
(function() {
    // Global initialization flag
    window.thebeInitializing = false;
    
    // Configuration
    const THEBE_VERSION = "0.8.2";
    const UNPKG_URL = "https://unpkg.com/thebe@" + THEBE_VERSION + "/lib/index.js";
    const LOCAL_URL = "../_static/thebe_versions/thebe-" + THEBE_VERSION + ".js";
    
    function initializeThebe() {
        console.log("Initializing Thebe with patched loader...");
        
        if (window.thebeInitializing) {
            console.log("Thebe initialization already in progress, skipping duplicate call");
            return;
        }
        
        window.thebeInitializing = true;
        
        // Function to attempt Thebe initialization with resilience
        function attemptThebeInit() {
            if (typeof thebelab === 'undefined') {
                console.warn("Thebe not loaded yet, will retry in 500ms");
                setTimeout(attemptThebeInit, 500);
                return;
            }
            
            try {
                console.log("Detected cells:", document.querySelectorAll('.thebe-augmented, pre[data-executable="true"]').length);
                
                // Patch to handle 'Host is not attached' error
                const originalAttach = thebelab.session.SessionManager.prototype.attach;
                if (originalAttach) {
                    thebelab.session.SessionManager.prototype.attach = function() {
                        try {
                            return originalAttach.apply(this, arguments);
                        } catch (e) {
                            console.warn("Handled Thebe attachment error:", e);
                            // Create a fake host object if needed
                            if (e.message && e.message.includes("Host is not attached")) {
                                this.host = {
                                    resolve: function(session) { return session; }
                                };
                                return originalAttach.apply(this, arguments);
                            }
                            throw e;
                        }
                    };
                }
                
                // Configure Thebe with resilient settings
                const config = {
                    binderOptions: {
                        repo: "binder-examples/jupyter-stacks-datascience",
                        ref: "master",
                    },
                    kernelOptions: {
                        name: "python3",
                        path: "./notebooks"
                    },
                    // Use a very broad selector to find all possible code cells
                    selector: ".thebe-augmented, .thebe, .cell, pre[data-executable='true'], .jp-Cell, div.highlight pre",
                    requestKernel: true,
                    mountActivateWidget: true,
                    predefinedOutput: true,
                    stripPrompts: true
                };
                
                // Bootstrap with error handling
                try {
                    thebelab.bootstrap(config);
                    console.log("Thebe bootstrap successful");
                    
                    // Update status messages
                    const statusElements = document.querySelectorAll('.thebe-status, .loading-text');
                    statusElements.forEach(el => {
                        el.textContent = "Ready";
                    });
                    
                    // Add success indicator
                    const indicator = document.createElement('div');
                    indicator.style.cssText = 'position:fixed; bottom:10px; right:10px; background:#4CAF50; color:white; padding:5px 10px; border-radius:3px; z-index:1000;';
                    indicator.textContent = 'Thebe Ready';
                    document.body.appendChild(indicator);
                    setTimeout(() => indicator.remove(), 5000);
                    
                } catch (bootstrapError) {
                    console.error("Error in Thebe bootstrap:", bootstrapError);
                    
                    // Try a simpler configuration as fallback
                    try {
                        console.log("Attempting fallback configuration...");
                        thebelab.bootstrap({
                            binderOptions: {
                                repo: "binder-examples/jupyter-stacks-datascience",
                                ref: "master",
                            },
                            kernelOptions: {
                                name: "python3"
                            },
                            selector: "pre[data-executable='true']",
                            requestKernel: true
                        });
                    } catch (fallbackError) {
                        console.error("Fallback configuration also failed:", fallbackError);
                    }
                }
            } catch (e) {
                console.error("Error during Thebe patched initialization:", e);
            } finally {
                window.thebeInitializing = false;
            }
        }
        
        // First ensure all code cells have the right attributes
        prepareCodeCells();
        
        // Then attempt to initialize Thebe
        attemptThebeInit();
    }
    
    function prepareCodeCells() {
        console.log("Preparing code cells for Thebe...");
        
        // Find all potential code cells
        const selectors = [
            "pre", 
            "div.highlight pre", 
            ".cell pre", 
            "pre.highlight", 
            "div.cell",
            "div.jp-Cell",
            "div.jp-CodeCell",
            "div.highlight-python pre"
        ];
        
        const codeCells = document.querySelectorAll(selectors.join(", "));
        console.log("Found " + codeCells.length + " potential code cells");
        
        // Process each cell
        codeCells.forEach(function(cell, index) {
            // Check if this looks like a Python code cell
            const textContent = cell.textContent.trim();
            const looksLikePython = 
                textContent.includes('import ') || 
                textContent.includes('print(') || 
                textContent.includes('def ') || 
                textContent.includes('plt.') ||
                textContent.includes('np.') ||
                textContent.includes('=') ||
                cell.classList.contains('python') ||
                cell.parentElement.classList.contains('highlight-python');
            
            if (looksLikePython && textContent.length > 5) {
                // Make sure it has needed attributes
                cell.setAttribute('data-executable', 'true');
                cell.setAttribute('data-language', 'python');
                
                // Add our custom class for tracking
                cell.classList.add('thebe-augmented');
                
                // Give it an ID if it doesn't have one
                if (!cell.id) {
                    cell.id = 'thebe-cell-' + index;
                }
                
                console.log("Enhanced cell " + cell.id + " for Thebe compatibility");
            }
        });
    }
    
    // Load Thebe from the best available source
    function loadThebeLibrary() {
        console.log("Loading Thebe library...");
        
        let scriptLoaded = false;
        
        // Try loading from local path first
        function tryLocalThebe() {
            const script = document.createElement('script');
            script.src = LOCAL_URL;
            script.async = true;
            
            script.onload = function() {
                console.log("Loaded Thebe from local path");
                scriptLoaded = true;
                initializeThebe();
            };
            
            script.onerror = function() {
                console.warn("Failed to load Thebe from local path, trying CDN...");
                if (!scriptLoaded) {
                    tryCdnThebe();
                }
            };
            
            document.head.appendChild(script);
        }
        
        // Fall back to CDN if local fails
        function tryCdnThebe() {
            const script = document.createElement('script');
            script.src = UNPKG_URL;
            script.async = true;
            
            script.onload = function() {
                console.log("Loaded Thebe from CDN");
                scriptLoaded = true;
                initializeThebe();
            };
            
            script.onerror = function() {
                console.error("Failed to load Thebe from CDN");
            };
            
            document.head.appendChild(script);
        }
        
        // Check if Thebe is already loaded
        if (typeof thebelab !== 'undefined') {
            console.log("Thebe already loaded, proceeding to initialization");
            initializeThebe();
        } else {
            // Try to load it
            tryLocalThebe();
        }
    }
    
    // Initialize when the page is ready
    if (document.readyState === 'complete') {
        loadThebeLibrary();
    } else {
        window.addEventListener('DOMContentLoaded', loadThebeLibrary);
    }
})();
