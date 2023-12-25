let storedURL = '';

function fetchAndCopyTranscript() {
    const duration = document.getElementById('duration').value;
    const captureBefore = document.getElementById('capture-before').checked;

    if (!duration) {
        showNotification('Add Duration', true);
        return;
    }

    if (!storedURL) {
        navigator.clipboard.readText().then(clipboardContent => {
            if (clipboardContent && clipboardContent.includes('youtube.com')) {
                storedURL = clipboardContent;
            }
            fetchTranscript(storedURL, duration, captureBefore);
        }).catch(err => {
            console.error('Failed to read clipboard contents:', err);
            showNotification('Error reading clipboard', true);
        });
    } else {
        fetchTranscript(storedURL, duration, captureBefore);
    }
}

function fetchTranscript(url, duration, captureBefore) {
    if (!url) {
        showNotification('No URL found', true);
        return;
    }

    fetch('/get_transcript', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, duration, captureBefore }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.transcript) {
            document.getElementById('transcript').value = data.transcript;
        } else {
            showNotification('No transcript found', true);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('Error fetching transcript', true);
    });
}

function showNotification(message, isError) {
    // ... (existing notification code)
}
