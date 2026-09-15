"""Shared transcription-language validation."""

from __future__ import annotations

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"auto", "en", "zh"})


def normalize_language(value: object) -> str:
    """Return a supported SenseVoice language, defaulting to English."""
    if isinstance(value, str) and value in SUPPORTED_LANGUAGES:
        return value
    return DEFAULT_LANGUAGE
