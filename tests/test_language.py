import asyncio
import unittest


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


if __name__ == "__main__":
    unittest.main()
