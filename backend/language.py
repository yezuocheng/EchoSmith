"""Shared transcription-language validation."""

from __future__ import annotations

import asyncio
import threading
from typing import Any
from weakref import WeakKeyDictionary

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"auto", "en", "zh"})
_TRANSCRIPTION_LOCKS: WeakKeyDictionary[asyncio.AbstractEventLoop, asyncio.Lock] = WeakKeyDictionary()
_TRANSCRIPTION_LOCKS_GUARD = threading.Lock()


def _transcription_lock() -> asyncio.Lock:
    """Return a lock bound to the currently running event loop."""
    loop = asyncio.get_running_loop()
    with _TRANSCRIPTION_LOCKS_GUARD:
        lock = _TRANSCRIPTION_LOCKS.get(loop)
        if lock is None:
            lock = asyncio.Lock()
            _TRANSCRIPTION_LOCKS[loop] = lock
        return lock


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
    async with _transcription_lock():
        await engine.set_language(normalize_language(language))
        return await engine.transcribe(*args, **kwargs)
