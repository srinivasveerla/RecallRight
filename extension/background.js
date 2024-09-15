chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'selectedText') {
        const selectedText = message.text;
        console.log("Received selected text:", selectedText);

        // Example: Send data to a server (you can replace this with any API call)
        fetch('http://localhost:8000/data', {
            method: 'POST',
            headers: {
                'Content-Type': "application/json",
            },
            body: JSON.stringify({"content": selectedText.content, "source": selectedText.source}),
        })
        .then(response => response.json())
        .then(data => console.log('Data sent successfully:', data))
        .catch(error => console.error('Error sending data:', error));
    }
});