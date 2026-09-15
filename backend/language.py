"""Shared transcription-language validation."""

from __future__ import annotations

import asyncio
import threading
from typing import Any
from weakref import WeakKeyDictionary

DEFAULT_LANGUAGE = "en"
SUPPORTED_LANGUAGES = frozenset({"auto", "en", "zh"})
_ENGINE_LOCKS: WeakKeyDictionary[Any, threading.Lock] = WeakKeyDictionary()
_ENGINE_LOCKS_GUARD = threading.Lock()


def _transcription_lock(engine: Any) -> threading.Lock:
    """Return a process-wide lock associated with the shared engine."""
    lock = getattr(engine, "_transcription_lock", None)
    if lock is not None:
        return lock
    with _ENGINE_LOCKS_GUARD:
        lock = _ENGINE_LOCKS.get(engine)
        if lock is None:
            lock = threading.Lock()
            _ENGINE_LOCKS[engine] = lock
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
    lock = _transcription_lock(engine)
    while not lock.acquire(blocking=False):
        await asyncio.sleep(0.001)
    try:
        await engine.set_language(normalize_language(language))
        return await engine.transcribe(*args, **kwargs)
    finally:
        lock.release()
