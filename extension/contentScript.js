// contentScript.js
let labelDiv;

// Function to inject CSS styles into the document
function injectStyles() {
    const style = document.createElement('style');
    style.textContent = `
        /* Style for the button container */
        .glow-on-hover {
            width: 220px;
            height: 50px;
            border: none;
            outline: none;
            color: #fff;
            background: #111;
            cursor: pointer;
            position: relative;
            z-index: 0;
            border-radius: 10px;
            font-size: medium;
        }
        
        .glow-on-hover:before {
            content: '';
            background: linear-gradient(45deg, #ff0000, #ff7300, #fffb00, #48ff00, #00ffd5, #002bff, #7a00ff, #ff00c8, #ff0000);
            position: absolute;
            top: -2px;
            left:-2px;
            background-size: 400%;
            z-index: -1;
            filter: blur(5px);
            width: calc(100% + 4px);
            height: calc(100% + 4px);
            animation: glowing 20s linear infinite;
            opacity: 0;
            transition: opacity .3s ease-in-out;
            border-radius: 10px;
        }
        
        .glow-on-hover:active {
            color: #000
        }
        
        .glow-on-hover:active:after {
            background: transparent;
        }
        
        .glow-on-hover:hover:before {
            opacity: 1;
        }
        
        .glow-on-hover:after {
            z-index: -1;
            content: '';
            position: absolute;
            width: 100%;
            height: 100%;
            background: #111;
            left: 0;
            top: 0;
            border-radius: 10px;
        }
        
        @keyframes glowing {
            0% { background-position: 0 0; }
            50% { background-position: 400% 0; }
            100% { background-position: 0 0; }
        }
    `;
    document.head.appendChild(style);
}

// Call the function to inject styles
injectStyles();

// Function to create and display a label below the selected text
function showLabel(selection) {
    // Remove existing label if any
    if (labelDiv) labelDiv.remove();

    // Create a new div for the label
    labelDiv = document.createElement('div');
    labelDiv.style.position = 'absolute';
    
    labelDiv.style.zIndex = '9999';  // Ensure it's on top

    // Create the button element
    const button = document.createElement('button');
    button.textContent = 'Remember Me';
    button.style.cursor = 'pointer';
    button.classList.add('glow-on-hover');
    
    // Add the button to the labelDiv
    labelDiv.appendChild(button);

    // Append the label to the body
    document.body.appendChild(labelDiv);

    // Get the position of the selected text
    const range = selection.getRangeAt(0);
    const rect = range.getBoundingClientRect();

    // Set the position of the label below the selected text
    labelDiv.style.top = `${window.scrollY + rect.bottom + 5}px`;  // Add a little padding below
    labelDiv.style.left = `${window.scrollX + rect.left}px`;

    // Add click event listener to the button
    button.addEventListener('click', (e) => {
        e.stopPropagation();  // Prevent mouseup event from being triggered
        const selectedText = selection.toString();
        console.log(`Sending selected text: ${selectedText}`);

        // Send the selected text to the background script
        chrome.runtime.sendMessage({ 
            type: 'selectedText', 
            text: {
                content: selectedText, 
                source: window.location.toString()
            }
        });
        
        // Remove the label after sending the data
        labelDiv.remove();
    });
}

// Listen for mouseup event to detect selection and show the label
document.addEventListener('mouseup', (e) => {
    // Ignore mouseup events on the label or button to prevent unintended behavior
    if (e.target.tagName === 'BUTTON' || e.target.closest('div') === labelDiv) return;


    console.log("test")
    const selection = window.getSelection();

    if (selection.toString()) {
        // Show the label if there's selected text
        showLabel(selection);
    } else if (labelDiv) {
        // Remove the label if there's no selection
        labelDiv.remove();
    }
});

// Optionally, hide the label when the user presses the Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && labelDiv) {
        labelDiv.remove();
    }
});
