
// Fix Thebe cell detection by adding necessary attributes
document.addEventListener('DOMContentLoaded', function() {
    console.log("Running thebe cell fixer script");
    
    // Add attributes to code cells for Thebe detection
    const codeCells = document.querySelectorAll("div.cell, div.highlight pre, pre.highlight, pre, .thebe");
    console.log("Found " + codeCells.length + " potential code cells");
    
    codeCells.forEach(function(cell, index) {
        // Check if this is a code cell with content
        let cellContent = cell.textContent.trim();
        if (cellContent && cellContent.includes('import') || 
            cellContent.includes('print') || 
            cellContent.includes('=') || 
            cellContent.includes('def ')) {
            
            // Add attributes needed for Thebe
            cell.setAttribute('data-executable', 'true');
            cell.setAttribute('data-language', 'python');
            
            // Add a class for easy identification
            cell.classList.add('thebe-augmented');
            
            // Add a unique ID if not present
            if (!cell.id) {
                cell.id = 'cell-' + index;
            }
            
            console.log("Enhanced cell " + cell.id + " for Thebe compatibility");
        }
    });
    
    // Add identifiers to Python code blocks specifically
    document.querySelectorAll("div.highlight-python pre, pre.python").forEach(function(block, idx) {
        block.setAttribute('data-executable', 'true');
        block.setAttribute('data-language', 'python');
        block.classList.add('thebe-augmented', 'thebe');
        if (!block.id) {
            block.id = 'python-block-' + idx;
        }
    });
    
    // Attempt to find cells again after initialization
    setTimeout(function() {
        // Re-trigger Thebe initialization if available
        if (typeof initThebe === 'function') {
            console.log("Re-triggering Thebe initialization");
            initThebe();
        }
    }, 1000);
});
