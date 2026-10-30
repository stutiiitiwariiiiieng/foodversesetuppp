"""Shared LLM helper: sends text/images to Claude and returns parsed JSON."""
import base64, json, os, re
from anthropic import Anthropic, APIError
from fastapi import HTTPException
from dotenv import load_dotenv

load_dotenv()
MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")
_client = None


def client() -> Anthropic:
    global _client
    if _client is None:
        _client = Anthropic(max_retries=3, timeout=90)  # reads ANTHROPIC_API_KEY
    return _client


def image_block(data: bytes, media_type: str = "image/jpeg") -> dict:
    return {
        "type": "image",
        "source": {"type": "base64", "media_type": media_type,
                   "data": base64.b64encode(data).decode()},
    }


def _parse_json(text: str) -> dict:
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.M).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("Model did not return JSON")
    return json.loads(text[start:end + 1])


def ask_json(system: str, content: list, max_tokens: int = 1500) -> dict:
    system += "\nRespond with ONLY a single valid JSON object. No markdown, no prose."
    last = None
    for _ in range(2):  # one retry if the model returns malformed JSON
        try:
            resp = client().messages.create(
                model=MODEL, max_tokens=max_tokens, system=system,
                messages=[{"role": "user", "content": content}],
            )
        except APIError as e:
            raise HTTPException(502, f"AI service error: {getattr(e, 'message', str(e))}") from e
        try:
            return _parse_json("".join(b.text for b in resp.content if b.type == "text"))
        except ValueError as e:  # includes json.JSONDecodeError
            last = e
    raise HTTPException(502, f"AI returned an unreadable response: {last}")
