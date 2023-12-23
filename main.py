import re
from youtube_transcript_api import YouTubeTranscriptApi
from textwrap import fill

def extract_video_id(url):
    if "youtu.be" in url:
        # Extracting ID from the shortened format URL (https://youtu.be/VIDEO_ID)
        id_pattern = r"youtu\.be\/([^?&]*)"
        match = re.search(id_pattern, url)
        return match.group(1) if match else None
    else:
        # Extracting ID from the standard format URL (https://www.youtube.com/watch?v=VIDEO_ID)
        id_pattern = r"(?<=v=)[^&#]+"
        match = re.search(id_pattern, url)
        return match.group(0) if match else None

def parse_start_time_from_url(url):
    # Parsing the timestamp from the URL for both formats
    time_pattern = r"[?&]t=(\d+)s?"
    match = re.search(time_pattern, url)

    if match:
        return int(match.group(1))
    else:
        return 0

def format_transcript(transcript):
    formatted_text = ""
    previous_speaker = None

    for entry in transcript:
        speaker = entry.get('speaker')
        if speaker and speaker != previous_speaker:
            formatted_text += "\n"  # New line for a new speaker!
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

def save_transcript_to_file(transcript, filename="transcript.txt"):
    if transcript:
        with open(filename, "w") as file:
            file.write(transcript)
        print(f"The transcript has been saved to {filename}.")
    else:
        print("No transcript to save.")

def main():
    url = input("Enter the YouTube URL with timestamp: ")
    duration = int(input("Enter the duration for the transcript (in seconds): "))

    video_id = extract_video_id(url)
    start_time = parse_start_time_from_url(url)

    transcript = get_transcript(video_id, start_time, duration)

    if transcript:
        print("Transcript:", transcript)
    else:
        print("No transcript available for the provided URL and timestamp.")

    save_transcript_to_file(transcript)

if __name__ == "__main__":
    main()
