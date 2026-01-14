# vertex_llm.py
from __future__ import annotations

from typing import Optional, Any
import asyncio
import time
import logging

from google import genai
from google.genai import types

from app.settings import settings

logger = logging.getLogger(__name__)

# Lazy-initialized, process-wide client.
# NOTE: google-genai client is synchronous; we call it via asyncio.to_thread() from async code.
_client: Optional[genai.Client] = None


def _get_client() -> Optional[genai.Client]:
    """
    Create a Google Gen AI SDK client configured for Vertex AI.
    Uses Application Default Credentials (ADC) in Cloud Run by default.
    """
    global _client

    project = settings.VERTEX_PROJECT
    location = settings.VERTEX_LOCATION
    if not project or not location:
        return None

    if _client is None:
        _client = genai.Client(
            vertexai=True,
            project=project,
            location=location,
        )
    return _client


def _extract_text(resp: Any) -> str:
    """
    Best-effort extraction.
    In google-genai, resp.text is the recommended surface, but keep it defensive.
    """
    text = getattr(resp, "text", None)
    if isinstance(text, str):
        return text.strip()

    # Fallback: try candidate parts (structure can vary by response type)
    candidates = getattr(resp, "candidates", None)
    if candidates:
        c0 = candidates[0]
        content = getattr(c0, "content", None)
        parts = getattr(content, "parts", None) if content else None
        if parts:
            out = []
            for p in parts:
                t = getattr(p, "text", None)
                if t:
                    out.append(t)
            return "".join(out).strip()

    return ""


def _fallback_summary(theme: str, distance_km: float, duration_min: float, spots: Optional[list]) -> str:
    spots_text = ""
    if spots:
        names = ", ".join(s.get("name") for s in spots if isinstance(s, dict) and s.get("name"))
        if names:
            spots_text = f"（見どころ: {names}）"
    return f"{theme}を楽しみながら約{distance_km:.1f}kmを{duration_min:.0f}分で歩ける、気軽な散歩コースです{spots_text}。"


async def generate_summary(
    *,
    theme: str,
    distance_km: float,
    duration_min: float,
    spots: Optional[list] = None,
) -> Optional[str]:
    """
    Generate a 1-sentence Japanese summary for a walking route using Google Gen AI SDK (google-genai).
    - Disables thinking to avoid "NO_PARTS + MAX_TOKENS" empty responses for short outputs.
    - Runs sync SDK call in a thread to keep async endpoint responsive.
    """
    model_name = settings.VERTEX_TEXT_MODEL  # e.g., "gemini-2.5-flash"
    if not model_name:
        return None

    client = _get_client()
    if client is None:
        return None

    spots_text = ""
    if spots:
        names = ", ".join(s.get("name") for s in spots if isinstance(s, dict) and s.get("name"))
        if names:
            spots_text = f" 見どころ: {names}。"

    # Keep it strict: 1 sentence, polite, concise, and a rough length hint.
    prompt = (
        "以下の散歩ルートの紹介文を日本語で1文だけ作成してください（40〜70文字程度、丁寧で簡潔）。"
        f" テーマ: {theme}。目安距離: {distance_km:.1f}km。"
        f" 所要時間: {duration_min:.0f}分。"
        f"{spots_text}"
    )

    temperature = getattr(settings, "VERTEX_TEMPERATURE", 0.4)
    max_output_tokens = getattr(settings, "VERTEX_MAX_OUTPUT_TOKENS", 128)

    # Key fix: disable thinking for this trivial generation to prevent "thinking eats tokens" empties.
    # Vertex AI thinking docs: thinking_budget=0 disables thinking.
    cfg = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    )

    logger.info("[GenAI SDK Call] model=%s", model_name)

    t0 = time.time()
    try:
        # google-genai is sync: call in thread
        resp = await asyncio.to_thread(
            client.models.generate_content,
            model=model_name,
            contents=prompt,
            config=cfg,
        )
    except Exception as e:
        dt = int((time.time() - t0) * 1000)
        logger.exception("[GenAI SDK Error] elapsed_ms=%s err=%r", dt, e)
        # Product-friendly fallback (optional): return a deterministic sentence instead of None.
        return _fallback_summary(theme, distance_km, duration_min, spots)

    dt = int((time.time() - t0) * 1000)

    text = _extract_text(resp)
    # Helpful metadata (best-effort; attribute names may vary)
    usage = getattr(resp, "usage_metadata", None)
    logger.info(
        "[GenAI SDK Done] elapsed_ms=%s text_len=%s usage=%s",
        dt,
        len(text) if text else 0,
        usage,
    )

    if text:
        return text

    # If empty, return a stable fallback to avoid flaky UX.
    logger.warning("[GenAI SDK Empty] model=%s usage=%s", model_name, usage)
    return _fallback_summary(theme, distance_km, duration_min, spots)
