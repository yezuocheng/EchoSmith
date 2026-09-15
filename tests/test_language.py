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


if __name__ == "__main__":
    unittest.main()
