"""Tests for utils/cache_key.py — normalization, hashes and cache key composition."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.cache_key import build_cache_key, normalize_input, params_signature, prompt_version_hash


class TestNormalizeInput(unittest.TestCase):
    def test_strips_leading_trailing_spaces(self):
        self.assertEqual(normalize_input("  hello  "), "hello")

    def test_collapses_internal_whitespace(self):
        self.assertEqual(normalize_input("foo   bar\t\nbaz"), "foo bar baz")

    def test_same_hash_for_equivalent_inputs(self):
        import hashlib

        a = hashlib.sha256(normalize_input("  my input  ").encode()).hexdigest()
        b = hashlib.sha256(normalize_input("my  input").encode()).hexdigest()
        self.assertEqual(a, b)

    def test_different_content_gives_different_result(self):
        self.assertNotEqual(normalize_input("foo"), normalize_input("bar"))


class TestPromptVersionHash(unittest.TestCase):
    def test_same_content_same_hash(self):
        self.assertEqual(prompt_version_hash("abc"), prompt_version_hash("abc"))

    def test_different_content_different_hash(self):
        self.assertNotEqual(prompt_version_hash("v1"), prompt_version_hash("v2"))

    def test_returns_16_chars(self):
        self.assertEqual(len(prompt_version_hash("any content")), 16)


class TestParamsSignature(unittest.TestCase):
    def test_key_order_independent(self):
        a = params_signature({"model": "gpt-4", "temperature": 0.3})
        b = params_signature({"temperature": 0.3, "model": "gpt-4"})
        self.assertEqual(a, b)

    def test_different_params_different_signature(self):
        a = params_signature({"temperature": 0.3})
        b = params_signature({"temperature": 0.7})
        self.assertNotEqual(a, b)

    def test_returns_16_chars(self):
        self.assertEqual(len(params_signature({"k": "v"})), 16)


class TestBuildCacheKey(unittest.TestCase):
    def _key(self, text="input", model="m", prompts="p", params=None):
        return build_cache_key(text, model, prompts, params or {})

    def test_same_inputs_same_key(self):
        self.assertEqual(self._key(), self._key())

    def test_whitespace_variants_same_key(self):
        k1 = build_cache_key("  my input  ", "m", "p", {})
        k2 = build_cache_key("my  input", "m", "p", {})
        self.assertEqual(k1, k2)

    def test_different_model_different_key(self):
        self.assertNotEqual(self._key(model="gpt-4"), self._key(model="gpt-3"))

    def test_different_prompts_different_key(self):
        self.assertNotEqual(self._key(prompts="v1"), self._key(prompts="v2"))

    def test_different_params_different_key(self):
        k1 = build_cache_key("x", "m", "p", {"temperature": 0.3})
        k2 = build_cache_key("x", "m", "p", {"temperature": 0.7})
        self.assertNotEqual(k1, k2)

    def test_key_format_has_four_parts(self):
        key = self._key()
        self.assertEqual(len(key.split(":")), 4)


if __name__ == "__main__":
    unittest.main()
