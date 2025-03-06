
// Fix for Thebe launch button
(function() {
    console.log("Thebe button fix loaded");
    
    // Function to override the button's click handler
    function fixThebeButtons() {
        // Find all Thebe launch buttons
        const buttons = document.querySelectorAll('.thebe-launch-button');
        console.log("Found", buttons.length, "Thebe launch buttons");
        
        buttons.forEach(function(button) {
            // Clear existing click handlers by cloning the button
            const newButton = button.cloneNode(true);
            button.parentNode.replaceChild(newButton, button);
            
            // Add our own click handler
            newButton.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                console.log("Thebe launch button clicked, using direct initialization");
                
                // Update button appearance
                newButton.innerHTML = `
                    <div class="spinner">
                        <div class="rect1"></div>
                        <div class="rect2"></div>
                        <div class="rect3"></div>
                        <div class="rect4"></div>
                    </div>
                    <span class="loading-text">Connecting to Binder...</span>`;
                
                // Use direct Thebe initialization
                if (typeof thebelab === 'undefined') {
                    console.error("Thebe library not loaded");
                    newButton.innerHTML = '<span class="loading-text">Error: Thebe not available</span>';
                    return;
                }
                
                // Listen for status changes
                thebelab.on('status', function(_, data) {
                    console.log("Thebe status:", data.status);
                    newButton.classList.remove('thebe-status-waiting', 'thebe-status-starting', 'thebe-status-ready', 'thebe-status-failed');
                    newButton.classList.add('thebe-status-' + data.status);
                    
                    const loadingText = newButton.querySelector('.loading-text');
                    if (loadingText) {
                        loadingText.textContent = data.status === 'ready' 
                            ? 'Ready!' 
                            : 'Status: ' + data.status;
                    }
                });
                
                // Initialize Thebe with direct bootstrap
                thebelab.bootstrap({
                    binderOptions: {
                        repo: "binder-examples/jupyter-stacks-datascience",
                        ref: "master",
                    },
                    kernelOptions: {
                        name: "python3",
                        path: "./notebooks"
                    },
                    // Use a broad selector to find cells
                    selector: "pre[data-executable='true'], .thebe, .thebe-augmented, div.highlight-python pre",
                    requestKernel: true,
                    mountActivateWidget: true,
                    predefinedOutput: true
                });
            });
            
            console.log("Fixed Thebe launch button:", newButton.textContent.trim());
        });
    }
    
    // Make sure cells have the right attributes
    function prepareCells() {
        // Find Python code blocks
        const codeBlocks = document.querySelectorAll('div.highlight-python pre, pre.python, div.highlight pre');
        console.log("Found", codeBlocks.length, "potential code blocks");
        
        codeBlocks.forEach(function(block, idx) {
            // Add needed attributes
            block.setAttribute('data-executable', 'true');
            block.setAttribute('data-language', 'python');
            block.classList.add('thebe-augmented');
            
            if (!block.id) {
                block.id = 'code-block-' + idx;
            }
            
            console.log("Enhanced code block:", block.id);
        });
    }
    
    // Run our fixes when the page is ready
    document.addEventListener('DOMContentLoaded', function() {
        // First prepare cells
        prepareCells();
        
        // Then fix the buttons
        fixThebeButtons();
    });
})();
