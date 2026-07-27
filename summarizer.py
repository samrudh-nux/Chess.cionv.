"""
summarizer.py
yooooo it also picks "key timestamps" itself, by asking the LLM to identify the
most information-dense moments — not just every N minutes.
"""

import os
from anthropic import Anthropic
from transcript_fetcher import format_timestamp

MODEL = "claude-sonnet-4-5"         
CHUNK_TOKEN_LIMIT = 3000          


def _client() -> Anthropic:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise RuntimeError(
            "Set your ANTHROPIC_API_KEY environment variable before running this."
        )
    return Anthropic(api_key=api_key)


def _segments_to_text(segments: list[dict]) -> str:
    """Flatten transcript segments into plain text with inline timestamp markers."""
    lines = []
    for seg in segments:
        ts = format_timestamp(seg["start"])
        lines.append(f"[{ts}] {seg['text']}")
    return "\n".join(lines)


def _chunk_segments(segments: list[dict], words_per_chunk: int = 1500) -> list[list[dict]]:
    """Split segments into chunks of roughly `words_per_chunk` words each."""
    chunks, current, word_count = [], [], 0
    for seg in segments:
        current.append(seg)
        word_count += len(seg["text"].split())
        if word_count >= words_per_chunk:
            chunks.append(current)
            current, word_count = [], 0
    if current:
        chunks.append(current)
    return chunks


def _call_llm(client: Anthropic, prompt: str) -> str:
    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text


def _summarize_chunk(client: Anthropic, chunk_text: str) -> str:
    prompt = f"""Summarize this segment of a video transcript in 3-5 sentences.
Keep any strong opinions, numbers, or claims intact — don't smooth them away.

Transcript segment (includes [MM:SS] timestamps):
{chunk_text}

Summary:"""
    return _call_llm(client, prompt)


def _combine_summaries(client: Anthropic, chunk_summaries: list[str]) -> str:
    joined = "\n\n".join(f"Part {i+1}: {s}" for i, s in enumerate(chunk_summaries))
    prompt = f"""These are summaries of consecutive parts of one video, in order.
Combine them into a single coherent overall summary (one short paragraph),
followed by 3-5 bullet point key takeaways.

{joined}

Overall summary:"""
    return _call_llm(client, prompt)


def _extract_key_timestamps(client: Anthropic, full_text: str, n: int = 5) -> str:
    prompt = f"""Below is a video transcript with [MM:SS] timestamps.
Identify the {n} most information-dense or important moments — points where
a key claim, decision, number, or conclusion is stated. For each, output:
[timestamp] - one line description of what happens there.

Transcript:
{full_text}

Key moments:"""
    return _call_llm(client, prompt)


def summarize_video(segments: list[dict]) -> dict:
    """
    The main agentic entry point.
    Returns: {"summary": str, "key_timestamps": str, "strategy_used": str}
    """
    client = _client()
    full_text = _segments_to_text(segments)
    total_words = sum(len(seg["text"].split()) for seg in segments)

    # --- DECISION POINT: this is the "agentic" branch ---
    if total_words <= CHUNK_TOKEN_LIMIT:
        strategy = "single-pass (short video)"
        summary = _summarize_chunk(client, full_text)
    else:
        strategy = "map-reduce (long video, chunked)"
        chunks = _chunk_segments(segments)
        chunk_summaries = [
            _summarize_chunk(client, _segments_to_text(chunk)) for chunk in chunks
        ]
        summary = _combine_summaries(client, chunk_summaries)

    key_timestamps = _extract_key_timestamps(client, full_text)

    return {
        "summary": summary,
        "key_timestamps": key_timestamps,
        "strategy_used": strategy,
        "word_count": total_words,
    }
