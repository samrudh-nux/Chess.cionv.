## yo this is where the agetn thinks###

import re
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


def extract_video_id(url: str) -> str:
    """Pull the 11-character video ID out of common YouTube URL formats."""
    patterns = [
        r"(?:v=|\/)([0-9A-Za-z_-]{11}).*",   # watch?v=..., /embed/..., etc.
        r"youtu\.be\/([0-9A-Za-z_-]{11})",   # youtu.be short links
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    raise ValueError(f"Could not extract a video ID from URL: {url}")


def fetch_transcript(url: str) -> list[dict]:
    """
    Returns a list of segments like:
        [{"text": "hello everyone", "start": 0.5, "duration": 2.1}, ...]
    Raises a clear error if the video has no transcript available.
    """
    video_id = extract_video_id(url)
    try:
        segments = YouTubeTranscriptApi.get_transcript(video_id)
    except TranscriptsDisabled:
        raise RuntimeError("This video has transcripts disabled — can't summarize it.")
    except NoTranscriptFound:
        raise RuntimeError("No transcript found for this video (maybe wrong language).")
    return segments


def format_timestamp(seconds: float) -> str:
    """Convert raw seconds into MM:SS or HH:MM:SS for display."""
    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    if hours:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


if __name__ == "__main__":
    # quick manual test
    test_url = input("Paste a YouTube URL to test transcript fetching: ")
    segs = fetch_transcript(test_url)
    print(f"Fetched {len(segs)} segments. First 3:")
    for s in segs[:3]:
        print(f"  [{format_timestamp(s['start'])}] {s['text']}")
