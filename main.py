from flask import Flask, request, jsonify, render_template
import re
import os
import openai
from youtube_transcript_api import YouTubeTranscriptApi
from textwrap import fill

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to extract video ID from URL
def extract_video_id(url):
    if "youtu.be" in url:
        id_pattern = r"youtu\.be\/([^?&]*)"
        match = re.search(id_pattern, url)
        return match.group(1) if match else None
    else:
        id_pattern = r"(?<=v=)[^&#]+"
        match = re.search(id_pattern, url)
        return match.group(0) if match else None

# Function to parse start time from URL
def parse_start_time_from_url(url):
    time_pattern = r"[?&]t=(\d+)s?"
    match = re.search(time_pattern, url)
    return int(match.group(1)) if match else 0

# Function to format the transcript
def format_transcript(transcript):
    formatted_text = ""
    previous_speaker = None

    for entry in transcript:
        speaker = entry.get('speaker')
        if speaker and speaker != previous_speaker:
            formatted_text += "\n"
            previous_speaker = speaker
        text = entry['text']
        formatted_text += fill(text, width=80) + "\n"

    return formatted_text

# Function to get transcript from YouTube
def get_transcript(video_id, start_time, duration):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

    end_time = start_time + duration
    relevant_transcript = []
    is_capturing = False

    for entry in transcript:
        current_start = entry['start']
        current_end = current_start + entry['duration']

        if not is_capturing and current_start <= start_time < current_end:
            is_capturing = True

        if is_capturing and current_start > end_time:
            break

        if is_capturing:
            relevant_transcript.append(entry)

    return format_transcript(relevant_transcript)



# Function to clean up transcript using GPT
def get_cleaned_transcript(raw_transcript):
    if not raw_transcript:
        print("Empty transcript; skipping GPT cleanup.")
        return raw_transcript

    print("Raw Transcript for Cleanup:", raw_transcript)  # Debug print to confirm raw transcript

    try:
        # OpenAI API Call for transcript cleanup
        response = openai.Completion.create(
            engine="text-davinci-003",  # Choose your preferred model
            prompt=(f"Clean the following transcript and ensure it has "
                    "punctuations and proper capitalizations:\n\n"
                    f"{raw_transcript}\n\n###\n\n"),
            max_tokens=2048  # Adjust based on your requirement
        )

        cleaned_transcript = response.choices[0].text.strip()
        print("Cleaned Transcript:", cleaned_transcript)  # Debug print to confirm cleaned transcript

        return cleaned_transcript
    except Exception as e:
        print(f"Error in GPT-based cleanup: {e}")
        return raw_transcript






# Flask route for serving the front-end# Flask route for serving the front-end
@app.route('/')
def index():
    return render_template('index.html')


# Flask route for processing transcript requests
@app.route('/get_transcript', methods=['POST'])
def get_transcript_route():
    data = request.json
    url = data['url']
    duration = int(data['duration'])

    print("Received data for processing:", data)  # Debug print to confirm data is received
    
    video_id = extract_video_id(url)
    start_time = parse_start_time_from_url(url)

    if not video_id:
        print("Invalid URL or unable to extract video ID.")  # Debug print for invalid URL
        return jsonify({'error': 'Invalid URL or unable to extract video ID.'}), 400

    transcript = get_transcript(video_id, start_time, duration)
    
    if not transcript:
        print("Transcript is empty, skipping GPT cleanup.")  # Debug print if transcript is empty
        return jsonify({'transcript': ""}), 200

    # Clean up transcript using GPT
    cleaned_transcript = get_cleaned_transcript(transcript)

    print("Cleaned Transcript:", cleaned_transcript)  # Debug print to confirm the cleaned transcript

    return jsonify({'transcript': cleaned_transcript})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)


