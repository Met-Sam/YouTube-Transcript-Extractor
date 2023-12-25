// Function to send a request to the Flask server to get the transcript
function fetchTranscript() {
    const url = document.getElementById('youtube-url').value;
    const duration = document.getElementById('duration').value;

    fetch('/get_transcript', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url, duration }),
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('transcript').textContent = data.transcript;
    })
    .catch(error => {
        console.error('Error fetching transcript:', error);
    });
}

// Function to copy the transcript text to the clipboard
function copyToClipboard() {
    const transcriptText = document.getElementById('transcript').textContent;
    navigator.clipboard.writeText(transcriptText).then(() => {
        alert('Transcript copied to clipboard!');
    }).catch(err => {
        console.error('Could not copy text:', err);
    });
}
