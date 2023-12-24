from flask import Flask, request, jsonify, render_template
import re
from youtube_transcript_api import YouTubeTranscriptApi
from textwrap import fill

# Your existing Python functions
def extract_video_id(url):
    if "youtu.be" in url:
        id_pattern = r"youtu\.be\/([^?&]*)"
        match = re.search(id_pattern, url)
        return match.group(1) if match else None
    else:
        id_pattern = r"(?<=v=)[^&#]+"
        match = re.search(id_pattern, url)
        return match.group(0) if match else None

def parse_start_time_from_url(url):
    time_pattern = r"[?&]t=(\d+)s?"
    match = re.search(time_pattern, url)
    return int(match.group(1)) if match else 0

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

# Flask app setup
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript_route():
    data = request.json
    url = data['url']
    duration = int(data['duration'])

    video_id = extract_video_id(url)
    start_time = parse_start_time_from_url(url)
    transcript = get_transcript(video_id, start_time, duration)

    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
