from dotenv import load_dotenv
from transcript_fetcher import fetch_transcript
from summarizer import summarize_video

load_dotenv()  # loads ANTHROPIC_API_KEY from a .env file if present


def run(url: str) -> None:
    print("\nFetching transcript...")
    segments = fetch_transcript(url)
    print(f"Got {len(segments)} transcript segments ({sum(len(s['text'].split()) for s in segments)} words).")

    print("Running summarizer agent...\n")
    result = summarize_video(segments)

    print("=" * 60)
    print(f"Strategy used: {result['strategy_used']}")
    print("=" * 60)
    print("\nSUMMARY:\n")
    print(result["summary"])
    print("\nKEY TIMESTAMPS:\n")
    print(result["key_timestamps"])
    print()


if __name__ == "__main__":
    video_url = input("Paste a YouTube URL: ").strip()
    run(video_url)
