"""
Snapshot tests for config/prompts.yaml.

These tests are NOT about the *exact* wording — that should be free to evolve
through prompt-engineering iterations. They guard against:

1. Structural regressions (someone deletes a key the services depend on).
2. Loss of critical signals: the prompt-engineering refactor introduced
   role-based system prompts, closed taxonomies, chain-of-thought, few-shot
   examples and self-verification. If any of those signals quietly disappears
   from a future edit, we want CI to fail loudly so the change is intentional.
3. Placeholder integrity (services rely on `.format()` keys that must exist).

When a deliberate prompt change removes a signal we no longer care about,
update or relax the corresponding assertion explicitly — that's the audit
trail.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config import get_prompt, get_prompts_version, load_prompts

# ── Required taxonomy values (must match services/schemas.py Literals) ──────
EXPECTED_TAXONOMIES = {
    "tipo": ["funcionalidade", "processo", "produto", "estrategia"],
    "business_game": ["attention", "transaction", "productivity"],
    "objetivo": [
        "aquisicao",
        "ativacao",
        "retencao",
        "receita",
        "satisfacao",
        "engajamento",
    ],
    "etapa_funil": ["aquisicao", "ativacao", "retencao", "receita", "referencia"],
    "complexidade": ["baixa", "media", "alta"],
}


class TestPromptsStructure(unittest.TestCase):
    """Top-level structural keys expected by the services."""

    def test_top_level_keys(self):
        prompts = load_prompts()
        self.assertIn("mistral", prompts)
        self.assertIn("openai", prompts)

    def test_mistral_analyze_context_keys(self):
        self.assertTrue(get_prompt("mistral", "analyze_context", "system").strip())
        self.assertTrue(get_prompt("mistral", "analyze_context", "user").strip())

    def test_openai_generate_metrics_keys(self):
        self.assertTrue(get_prompt("openai", "generate_metrics", "system").strip())
        self.assertTrue(get_prompt("openai", "generate_metrics", "user").strip())

    def test_openai_executive_summary_keys(self):
        self.assertTrue(get_prompt("openai", "executive_summary", "system").strip())
        self.assertTrue(get_prompt("openai", "executive_summary", "user").strip())


class TestPromptPlaceholders(unittest.TestCase):
    """Placeholders consumed by .format() in the services."""

    def test_mistral_analyze_context_user_has_initiative_text(self):
        user = get_prompt("mistral", "analyze_context", "user")
        self.assertIn("{initiative_text}", user)

    def test_openai_generate_metrics_user_uses_full_context_json(self):
        """After P0.2 the user prompt must consume the full upstream context."""
        user = get_prompt("openai", "generate_metrics", "user")
        self.assertIn("{initiative_text}", user)
        self.assertIn("{context_json}", user)
        # Old cherry-picked placeholders MUST be gone — keeping them around
        # would silently re-introduce the partial-context bug.
        for stale in ("{context_tipo}", "{context_objetivo}", "{context_etapa_funil}"):
            self.assertNotIn(stale, user, f"stale placeholder still present: {stale}")

    def test_openai_executive_summary_user_placeholders(self):
        user = get_prompt("openai", "executive_summary", "user")
        for ph in ("{initiative_text}", "{context}", "{metrics}"):
            self.assertIn(ph, user)


class TestMistralAnalyzeContextSignals(unittest.TestCase):
    """Critical signals the analyze_context prompt is expected to carry."""

    def test_system_lists_all_closed_taxonomies(self):
        system = get_prompt("mistral", "analyze_context", "system")
        for field, values in EXPECTED_TAXONOMIES.items():
            for v in values:
                self.assertIn(
                    v,
                    system,
                    f"taxonomy value '{v}' for field '{field}' missing from system prompt",
                )

    def test_user_has_chain_of_thought_block(self):
        user = get_prompt("mistral", "analyze_context", "user")
        # Loose check — the wording can change, but the staged-reasoning
        # cue should remain.
        lowered = user.lower()
        self.assertTrue(
            ("raciocine" in lowered) or ("passo" in lowered) or ("step" in lowered),
            "no chain-of-thought cue found in analyze_context user prompt",
        )

    def test_user_has_few_shot_examples(self):
        user = get_prompt("mistral", "analyze_context", "user")
        self.assertIn("EXEMPLO 1", user)
        self.assertIn("EXEMPLO 2", user)

    def test_user_requests_confidence(self):
        user = get_prompt("mistral", "analyze_context", "user")
        self.assertIn("confidence", user.lower())


class TestOpenaiGenerateMetricsSignals(unittest.TestCase):
    """Framework grounding and self-verification on the metrics prompt."""

    def test_system_grounds_in_north_star_and_aarrr(self):
        system = get_prompt("openai", "generate_metrics", "system")
        for keyword in ("North Star", "AARRR", "OKR", "SMART"):
            self.assertIn(
                keyword,
                system,
                f"framework keyword '{keyword}' missing from generate_metrics system prompt",
            )

    def test_user_has_self_verification_checklist(self):
        user = get_prompt("openai", "generate_metrics", "user")
        # We use a checkmark glyph in the verification block.
        self.assertIn("✓", user, "self-verification checklist missing")

    def test_user_has_chain_of_thought_block(self):
        user = get_prompt("openai", "generate_metrics", "user")
        lowered = user.lower()
        self.assertTrue(
            "raciocine" in lowered or "antes de" in lowered,
            "no chain-of-thought cue in generate_metrics user prompt",
        )


class TestExecutiveSummarySignals(unittest.TestCase):
    """Format and tone constraints on the executive summary."""

    def test_user_has_fixed_4_block_structure(self):
        user = get_prompt("openai", "executive_summary", "user")
        for header in ("**Tese.**", "**Métricas-chave.**", "**OKRs"):
            self.assertIn(header, user, f"missing required block header: {header}")

    def test_system_has_banned_word_list(self):
        system = get_prompt("openai", "executive_summary", "system")
        # A sample from the banned list — full enforcement isn't possible
        # without grading the actual model output, but the *list* must exist.
        for banned in ("alavancar", "potencializar", "sinergia"):
            self.assertIn(
                banned,
                system,
                f"banned-word '{banned}' missing from executive_summary system prompt",
            )


class TestPromptsVersion(unittest.TestCase):
    """The hash function must return a stable 8-char fingerprint."""

    def test_version_is_8_hex_chars(self):
        v = get_prompts_version()
        self.assertEqual(len(v), 8)
        int(v, 16)  # raises ValueError if not hex

    def test_version_is_cached(self):
        # lru_cache => same call returns same value within process.
        self.assertEqual(get_prompts_version(), get_prompts_version())


if __name__ == "__main__":
    unittest.main()
