# YouTube Video Summarizer Agent

A simple agentic Python project: give it a YouTube link, it pulls the
transcript, decides how to summarize it based on length, and returns a
summary plus key timestamps.

## Why this counts as "agentic" (not just a script)

Most beginner tutorials call something "agentic" just because it uses an
LLM API. The actual agent behavior here is one decision point:

- If the transcript is short, it summarizes it in a single LLM call.
- If the transcript is long, it **chunks the transcript, summarizes each
  chunk, then combines those summaries** (a map-reduce pattern) — because
  a single call would either truncate the video or produce a shallow
  summary.

That branch — the agent observing the state (transcript length) and
choosing a different action based on it — is the core of the "observe →
decide → act" loop every agent framework is built around, just written
out by hand so you can see exactly what's happening.

The key-timestamp extraction is also agentic in a small way: instead of
grabbing a timestamp every N minutes, the LLM is asked to *identify*
information-dense moments — a decision, not a fixed rule.

## Files

| File | Purpose |
|---|---|
| `transcript_fetcher.py` | Pulls the transcript from YouTube, extracts video ID, formats timestamps |
| `summarizer.py` | The agent: decides single-pass vs. chunked summarization, calls the LLM |
| `main.py` | CLI entry point — run this |
| `requirements.txt` | Dependencies |
| `.env.example` | Copy to `.env` and add your API key |

## Setup

\`\`\`bash
pip install -r requirements.txt
cp .env.example .env
# edit .env and paste in your Anthropic API key
\`\`\`

## Run

\`\`\`bash
python main.py
\`\`\`

Paste a YouTube URL when prompted. Works best on videos that have
captions/transcripts available (most do).

## Ideas to extend it (good next commits)

- Cache transcripts locally so you don't re-fetch on repeat runs.
- Swap the CLI for a small FastAPI endpoint + Next.js frontend (deployable
  on Vercel) so it's a shareable web app instead of a script.
- Add a second agent step that checks its own summary against the
  transcript for factual accuracy before returning it — a tiny
  self-verification loop.
- Support playlists: loop over videos and produce one combined report.

## Notes

- If a video has no captions, `youtube-transcript-api` will raise a clear
  error — this is handled in `transcript_fetcher.py`.
- Model name in `summarizer.py` (`MODEL = "claude-sonnet-4-5"`) — change
  it to whichever Claude model your API key has access to.
