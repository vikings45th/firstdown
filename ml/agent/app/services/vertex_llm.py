from __future__ import annotations

from pathlib import Path
from typing import Optional
import logging

from jinja2 import Environment, FileSystemLoader, TemplateNotFound
from langchain_core.exceptions import OutputParserException
from langchain_google_vertexai import ChatVertexAI

from app.schemas import DescriptionResponse, TitleResponse
from app.settings import settings

logger = logging.getLogger(__name__)

_PROMPT_DIR = Path(__file__).resolve().parent.parent / "prompts"
_PROMPT_ENV = Environment(
    loader=FileSystemLoader(str(_PROMPT_DIR)),
    autoescape=False,
    keep_trailing_newline=True,
)

_LLM_CACHE: dict[tuple[float, int], ChatVertexAI] = {}


def _get_llm(*, temperature: float, max_output_tokens: int) -> Optional[ChatVertexAI]:
    model_name = settings.VERTEX_TEXT_MODEL
    if not model_name or not settings.VERTEX_PROJECT or not settings.VERTEX_LOCATION:
        return None

    key = (temperature, max_output_tokens)
    if key in _LLM_CACHE:
        return _LLM_CACHE[key]

    llm = ChatVertexAI(
        project=settings.VERTEX_PROJECT,
        location=settings.VERTEX_LOCATION,
        model_name=model_name,
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        top_p=float(getattr(settings, "VERTEX_TOP_P", 0.95)),
        top_k=int(getattr(settings, "VERTEX_TOP_K", 40)),
    )
    _LLM_CACHE[key] = llm
    return llm


def _forbidden_words() -> list[str]:
    raw = str(getattr(settings, "VERTEX_FORBIDDEN_WORDS", "") or "")
    return [w.strip() for w in raw.split(",") if w.strip()]


def _contains_forbidden(text: str, forbidden_words: list[str]) -> Optional[str]:
    for w in forbidden_words:
        if w in text:
            return w
    return None


def _render_prompt(template_name: str, **context: object) -> str:
    try:
        template = _PROMPT_ENV.get_template(template_name)
    except TemplateNotFound:
        logger.error("[Vertex LLM] template not found: %s", template_name)
        return ""
    return template.render(**context).strip()


def _spot_names(spots: Optional[list]) -> list[str]:
    if not spots:
        return []
    names: list[str] = []
    for s in spots:
        name = None
        if isinstance(s, dict):
            name = s.get("name")
        else:
            name = getattr(s, "name", None)
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return names


def _fallback_summary(theme: str, distance_km: float, duration_min: float, spots: Optional[list]) -> str:
    theme_summaries = {
        "think": f"信号が少なく一定のリズムで歩ける約{distance_km:.1f}kmのルート。頭の中を整理するのに最適です。",
        "exercise": f"坂道や階段を多く含む約{distance_km:.1f}kmのルート。心拍数を上げてしっかり汗をかきましょう。",
        "refresh": f"賑やかな通りを歩く約{distance_km:.1f}kmのルート。エネルギーをチャージして気分転換できます。",
        "nature": f"緑豊かな公園をゆっくり抜ける約{distance_km:.1f}kmのルート。都会の喧騒から離れてリフレッシュできます。",
    }
    return theme_summaries.get(theme, f"約{distance_km:.1f}kmを{duration_min:.0f}分で歩ける散歩コースです。")


def _fallback_title(theme: str, distance_km: float, duration_min: float, spots: Optional[list]) -> str:
    theme_titles = {
        "think": "静けさの川沿い",
        "exercise": "アップダウン燃焼",
        "refresh": "街なかリフレッシュ",
        "nature": "木漏れ日の森歩き",
    }
    base = theme_titles.get(theme, "散歩")
    return f"{base}コース"


def fallback_title(theme: str, distance_km: float, duration_min: float, spots: Optional[list]) -> str:
    return _fallback_title(theme, distance_km, duration_min, spots)


def _theme_to_natural(theme: str) -> str:
    theme_map = {
        "exercise": "運動やエクササイズ",
        "think": "思考やリフレッシュ",
        "refresh": "気分転換やリフレッシュ",
        "nature": "自然や緑",
    }
    return theme_map.get(theme, theme)


async def _invoke_structured(prompt: str, *, temperature: float, max_output_tokens: int, schema: type) -> object:
    llm = _get_llm(temperature=temperature, max_output_tokens=max_output_tokens)
    if llm is None:
        raise RuntimeError("Vertex LLM is not configured")
    runnable = llm.with_structured_output(schema)
    return await runnable.ainvoke(prompt)


async def generate_summary(
    *,
    theme: str,
    distance_km: float,
    duration_min: float,
    spots: Optional[list] = None,
) -> Optional[str]:
    temperature = float(getattr(settings, "VERTEX_TEMPERATURE", 0.3))
    max_out = int(float(getattr(settings, "VERTEX_MAX_OUTPUT_TOKENS", 256)))
    forbidden_words = _forbidden_words()

    theme_desc = _theme_to_natural(theme)
    names = _spot_names(spots)
    spots_text = "、".join(names[:4]) if names else ""

    attempts = [
        {"strict": False, "min_chars": 80, "max_chars": 120, "temperature": temperature, "max_out": max_out},
        {"strict": True, "min_chars": 90, "max_chars": 120, "temperature": min(temperature, 0.2), "max_out": max(max_out, 192)},
    ]

    for attempt in attempts:
        prompt = _render_prompt(
            "description.jinja",
            strict=attempt["strict"],
            min_chars=attempt["min_chars"],
            max_chars=attempt["max_chars"],
            theme_desc=theme_desc,
            distance_km_str=f"{distance_km:.1f}km",
            duration_min_str=f"{duration_min:.0f}分",
            spots_text=spots_text,
            forbidden_words=forbidden_words,
        )
        try:
            result = await _invoke_structured(
                prompt,
                temperature=attempt["temperature"],
                max_output_tokens=attempt["max_out"],
                schema=DescriptionResponse,
            )
            parsed = result if isinstance(result, DescriptionResponse) else DescriptionResponse.model_validate(result)
            text = parsed.description
            banned = _contains_forbidden(text, forbidden_words)
            if banned:
                raise ValueError(f"forbidden word found: {banned}")
            return text
        except (OutputParserException, ValueError) as e:
            logger.warning("[Vertex LLM Summary Invalid] err=%r", e)
        except Exception as e:
            logger.exception("[Vertex LLM Summary Error] err=%r", e)

    return _fallback_summary(theme, distance_km, duration_min, spots)


async def generate_title(
    *,
    theme: str,
    distance_km: float,
    duration_min: float,
    spots: Optional[list] = None,
) -> Optional[str]:
    temperature = float(getattr(settings, "VERTEX_TEMPERATURE", 0.3))
    max_out = int(float(getattr(settings, "VERTEX_MAX_OUTPUT_TOKENS", 64)))
    forbidden_words = _forbidden_words()

    theme_desc = _theme_to_natural(theme)

    attempts = [
        {"strict": False, "min_chars": 8, "max_chars": 20, "temperature": min(temperature + 0.1, 0.6), "max_out": max_out},
        {"strict": True, "min_chars": 8, "max_chars": 18, "temperature": min(temperature, 0.2), "max_out": max(max_out, 96)},
    ]

    for attempt in attempts:
        prompt = _render_prompt(
            "title.jinja",
            strict=attempt["strict"],
            min_chars=attempt["min_chars"],
            max_chars=attempt["max_chars"],
            theme_desc=theme_desc,
            distance_km_str=f"{distance_km:.1f}km",
            duration_min_str=f"{duration_min:.0f}分",
            forbidden_words=forbidden_words,
        )
        try:
            result = await _invoke_structured(
                prompt,
                temperature=attempt["temperature"],
                max_output_tokens=attempt["max_out"],
                schema=TitleResponse,
            )
            parsed = result if isinstance(result, TitleResponse) else TitleResponse.model_validate(result)
            text = parsed.title
            banned = _contains_forbidden(text, forbidden_words)
            if banned:
                raise ValueError(f"forbidden word found: {banned}")
            return text
        except (OutputParserException, ValueError) as e:
            logger.warning("[Vertex LLM Title Invalid] err=%r", e)
        except Exception as e:
            logger.exception("[Vertex LLM Title Error] err=%r", e)

    return _fallback_title(theme, distance_km, duration_min, spots)
