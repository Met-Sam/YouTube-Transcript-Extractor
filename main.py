from flask import Flask, request, jsonify, render_template
import re
from youtube_transcript_api import YouTubeTranscriptApi
from nltk.tokenize import sent_tokenize
import nltk

nltk.download('punkt')

app = Flask(__name__)

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

def get_transcript(video_id, start_time, duration, capture_before):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return ""

    start_context = start_time - duration if capture_before else start_time
    end_time = start_time + duration if not capture_before else start_time

    relevant_transcript = []
    for entry in transcript:
        current_start = entry['start']
        current_end = current_start + entry['duration']
        if start_context <= current_end and current_start <= end_time:
            relevant_transcript.append(entry)

    full_text = ' '.join([entry['text'] for entry in relevant_transcript])
    sentences = sent_tokenize(full_text)

    if capture_before:
        end_sentence = next((s for s in sentences if full_text.find(s) >= end_time), sentences[-1])
        end_index = sentences.index(end_sentence) + 1
        trimmed_text = ' '.join(sentences[:end_index])
    else:
        start_sentence = next((s for s in sentences if full_text.find(s) >= start_context), sentences[0])
        start_index = sentences.index(start_sentence)
        trimmed_text = ' '.join(sentences[start_index:])

    return trimmed_text

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_transcript', methods=['POST'])
def get_transcript_route():
    data = request.json
    video_id = extract_video_id(data['url'])
    start_time = parse_start_time_from_url(data['url'])
    capture_before = data.get('captureBefore', False)
    transcript = get_transcript(video_id, start_time, int(data['duration']), capture_before)
    return jsonify({'transcript': transcript})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
