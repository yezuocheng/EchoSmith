"""Shared transcription-language validation."""

from __future__ import annotations

import asyncio
from typing import Any

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"auto", "en", "zh"})
_TRANSCRIPTION_LOCK = asyncio.Lock()


def normalize_language(value: object) -> str:
    """Return a supported SenseVoice language, defaulting to English."""
    if isinstance(value, str) and value in SUPPORTED_LANGUAGES:
        return value
    return DEFAULT_LANGUAGE


async def transcribe_in_language(
    engine: Any,
    language: object,
    *args: Any,
    **kwargs: Any,
) -> Any:
    """Keep language selection stable for the complete shared-engine decode."""
    async with _TRANSCRIPTION_LOCK:
        await engine.set_language(normalize_language(language))
        return await engine.transcribe(*args, **kwargs)
