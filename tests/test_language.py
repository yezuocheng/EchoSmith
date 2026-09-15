import asyncio
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor


class NormalizeLanguageTests(unittest.TestCase):
    def _normalizer(self):
        try:
            from backend.language import normalize_language
        except ModuleNotFoundError:
            self.fail("backend.language.normalize_language is missing")
        return normalize_language

    def test_preserves_supported_languages(self):
        normalize_language = self._normalizer()

        for language in ("auto", "en", "zh"):
            with self.subTest(language=language):
                self.assertEqual(normalize_language(language), language)

    def test_defaults_missing_or_invalid_values_to_english(self):
        normalize_language = self._normalizer()

        for language in (None, "", "de", 123):
            with self.subTest(language=language):
                self.assertEqual(normalize_language(language), "en")
class TranscriptionLanguageIsolationTests(unittest.IsolatedAsyncioTestCase):
    async def test_overlapping_tasks_keep_their_selected_language(self):
        try:
            from backend.language import transcribe_in_language
        except ImportError:
            self.fail("backend.language.transcribe_in_language is missing")

        class FakeEngine:
            def __init__(self):
                self.language = "en"

            async def set_language(self, language):
                self.language = language

            async def transcribe(self, task_name):
                language_at_start = self.language
                await asyncio.sleep(0.01)
                return task_name, language_at_start, self.language

        engine = FakeEngine()
        results = await asyncio.gather(
            transcribe_in_language(engine, "en", "english-task"),
            transcribe_in_language(engine, "zh", "chinese-task"),
        )

        self.assertEqual(
            results,
            [
                ("english-task", "en", "en"),
                ("chinese-task", "zh", "zh"),
            ],
        )


class TranscriptionLanguageEventLoopTests(unittest.TestCase):
    def test_helper_can_be_reused_by_separate_event_loops(self):
        try:
            from backend.language import transcribe_in_language
        except ImportError:
            self.fail("backend.language.transcribe_in_language is missing")

        class FakeEngine:
            def __init__(self):
                self.language = "en"

            async def set_language(self, language):
                self.language = language

            async def transcribe(self):
                return self.language

        async def run_once(language):
            return await transcribe_in_language(FakeEngine(), language)

        self.assertEqual(asyncio.run(run_once("en")), "en")
        self.assertEqual(asyncio.run(run_once("zh")), "zh")

    def test_shared_engine_is_serialized_across_event_loops(self):
        try:
            from backend.language import transcribe_in_language
        except ImportError:
            self.fail("backend.language.transcribe_in_language is missing")

        class FakeEngine:
            def __init__(self):
                self.language = "en"
                self.active = 0
                self.overlap = False
                self.state_lock = threading.Lock()

            async def set_language(self, language):
                self.language = language

            async def transcribe(self):
                with self.state_lock:
                    self.active += 1
                    self.overlap = self.overlap or self.active > 1
                language = self.language
                await asyncio.sleep(0.02)
                with self.state_lock:
                    self.active -= 1
                return language

        engine = FakeEngine()
        start = threading.Barrier(2)

        def run(language):
            async def transcribe():
                await asyncio.to_thread(start.wait, 1)
                return await transcribe_in_language(engine, language)

            return asyncio.run(transcribe())

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(run, ("en", "zh")))

        self.assertCountEqual(results, ["en", "zh"])
        self.assertFalse(engine.overlap)


if __name__ == "__main__":
    unittest.main()
