"""Regression tests for defects found in review (fixture builder lives in test_mindprint.py)."""
import json
import unittest

from test_mindprint import NAME, SkillTestCase, edit, run

VOICE = "references/voice.md"


class QuoteParsingTests(SkillTestCase):
    def add_voice(self, text):
        edit(self.out / VOICE, "# Voice\n", "# Voice\n\n" + text + "\n")

    def test_quote_of_only_editorial_brackets_fails(self):
        self.add_voice("> [invented words]\n[S01]")
        self.assert_fails("quotes", "no checkable words")

    def test_quote_of_only_ellipsis_fails(self):
        self.add_voice("> ... [S01]")
        self.assert_fails("quotes", "no checkable words")

    def test_blockquote_span_with_invented_framing_fails(self):
        self.add_voice('> He said "Well done is better than well said" and then he invented '
                       "a great many other words [S01]")
        self.assert_fails("quotes", "voice.md:3")

    def test_blockquote_span_with_short_framing_warns(self):
        self.add_voice('> He said "Well done is better than well said." [S01]')
        code, output = run("quotes", self.out, "--strict")
        self.assertEqual(code, 0, output)
        self.assertIn("WARN quote-framing: references/voice.md:3", output)

    def test_inline_quote_wrapped_across_lines_is_verified(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe wrote \"An investment in "
             "knowledge\npays the worst interest\" [S01]\n")
        self.assert_fails("quotes", "SKILL.md:")

    def test_inline_quote_wrapped_across_lines_passes_when_real(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe wrote \"An investment in "
             "knowledge\npays the best interest\" [S01]\n")
        output = self.assert_passes("quotes", "--strict")
        self.assertIn('"An investment in knowledge pays the best interest" found', output)

    def test_odd_straight_quotes_in_tagged_paragraph_warn(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe cut a 5\" board and "
             "wrote \"Lost time is never found again\" [S01]\n")
        code, output = run("quotes", self.out)
        self.assertEqual(code, 0, output)
        self.assertIn("WARN quote-unparsed: SKILL.md:", output)


class HoldoutCheckTests(SkillTestCase):
    def holdout(self):
        return self.out / "references/research/holdout.md"

    def test_check_fails_when_holdout_has_no_items(self):
        self.holdout().write_text("# Holdout\n\nNothing sealed yet.\n", encoding="utf-8")
        self.assert_fails("check", "0 items, need 3-5")

    def test_check_fails_on_malformed_holdout_heading(self):
        edit(self.holdout(), "## H2 · Event 2", "## H2 - Event 2")
        self.assert_fails("check", "malformed holdout heading")

    def test_check_fails_on_empty_what_happened(self):
        text = self.holdout().read_text(encoding="utf-8").split("\n")
        text = [line if not line.startswith("What happened") or "printing" not in line
                else "What happened:" for line in text]
        self.holdout().write_text("\n".join(text), encoding="utf-8")
        self.assert_fails("check", "H1 has no 'What happened:' line")


class EncodingAndPathTests(SkillTestCase):
    def test_bom_does_not_break_frontmatter_or_ledger(self):
        for name in ("SKILL.md", "references/sources.jsonl"):
            path = self.out / name
            path.write_text("﻿" + path.read_text(encoding="utf-8"), encoding="utf-8")
        self.assert_passes("check")

    def test_url_with_home_segment_is_not_an_absolute_path(self):
        edit(self.out / "FIDELITY.md", "Blind test", "See https://www.bbc.com/home/news and "
             "<https://example.com/Users/x>. Blind test")
        self.assert_passes("check")

    def test_absolute_path_after_url_still_fails(self):
        edit(self.out / "FIDELITY.md", "Blind test", "See https://x.org then /home/me/x. Blind")
        self.assert_fails("check", "absolute path")


class BlindReviewTests(SkillTestCase):
    def vdir(self):
        return self.out / "references/validation/2026-11-28"

    def blind(self, question, text="Answer.\n"):
        one, two = self.root / "one.md", self.root / "two.md"
        one.write_text(text, encoding="utf-8")
        two.write_text("Other answer.\n", encoding="utf-8")
        return run("blind", self.out, "--question", question, f"--arm=skill={one}",
                   f"--arm=baseline={two}", "--seed", 1, "--date", "2026-11-28")

    def grade(self, grades):
        path = self.root / "grades.json"
        path.write_text(json.dumps(grades), encoding="utf-8")
        return run("unblind", self.out, "--grades", path, "--date", "2026-11-28")

    def test_blind_keeps_long_line_that_mentions_as_an_ai(self):
        line = ("Writing to a friend he once mocked anyone who spoke as an AI might, all hedges "
                "and no wit, and he said so plainly in the letter.")
        self.blind("Q1", f"{line}\nAs an AI, I cannot know.\n")
        text = "\n".join(p.read_text(encoding="utf-8") for p in (self.vdir() / "Q1").iterdir())
        self.assertIn(line, text)
        self.assertNotIn("As an AI, I cannot know.", text)

    def test_blind_rejects_question_named_max(self):
        code, output = self.blind("max")
        self.assertEqual(code, 1)
        self.assertIn("'max' is reserved", output)

    def test_unblind_warns_when_an_arm_has_no_grade(self):
        self.blind("Q1")
        code, output = self.grade({"Q1": {"A": 7}})
        self.assertEqual(code, 0, output)
        self.assertIn("WARN grades: Q1.B has no grade", output)

    def test_unblind_float_tie_uses_epsilon(self):
        self.blind("H1")
        code, output = self.grade({"H1": {"A": 4.4, "B": 2.4}})
        self.assertEqual(code, 0, output)
        self.assertIn("tie (within 2 points)", output)


if __name__ == "__main__":
    unittest.main()
