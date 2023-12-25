let storedURL = '';

function fetchAndCopyTranscript() {
    const duration = document.getElementById('duration').value;
    const captureBefore = document.getElementById('capture-before').checked;

    if (!duration) {
        showNotification('Add Duration', true);
        return;
    }

    // Use the stored URL if it exists; otherwise, read from the clipboard
    const urlPromise = storedURL ? Promise.resolve(storedURL) : navigator.clipboard.readText();

    urlPromise.then(url => {
        // Check if the URL is different from the stored one
        if (url !== storedURL) {
            storedURL = url; // Update the stored URL if it's a new one
        }
        fetch('/get_transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url: storedURL, duration, captureBefore }),
        })
        .then(response => response.json())
        .then(data => {
            const transcript = data.transcript || 'No transcript found.';
            document.getElementById('transcript').value = transcript;
            showNotification('Transcript Ready', false);
        })
        .catch(error => {
            console.error('Error:', error);
            showNotification('Error fetching transcript', true);
        });
    }).catch(err => {
        console.error('Failed to read clipboard contents:', err);
        showNotification('Error reading clipboard', true);
    });
}
