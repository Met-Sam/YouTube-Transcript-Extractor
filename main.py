from flask import Flask, request, jsonify, render_template
import re
import os
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi
from textwrap import fill

# Initialize Flask app
app = Flask(__name__)

# Initialize the OpenAI client with your API key
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

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
            formatted_text += "\n" if previous_speaker is not None else ""
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

    for entry in transcript:
        current_start = entry['start']
        current_end = current_start + entry['duration']

        if current_start <= start_time < current_end or (current_start < end_time and current_end >= start_time):
            relevant_transcript.append(entry)

    return format_transcript(relevant_transcript)

# Flask route for serving the front-end
@app.route('/')
def index():
    return render_template('index.html')

# Flask route for processing transcript requests
@app.route('/get_transcript', methods=['POST'])
def get_transcript_route():
    data = request.json
    url = data['url']
    duration = int(data['duration'])

    video_id = extract_video_id(url)
    start_time = parse_start_time_from_url(url)
    transcript = get_transcript(video_id, start_time, duration)

    return jsonify({'transcript': transcript})

# Run the Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
