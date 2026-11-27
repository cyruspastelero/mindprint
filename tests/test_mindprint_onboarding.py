"""Tests for friction a new user hit building a quick-tier skill from the README."""
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from test_mindprint import SkillTestCase, edit, fail_lines, mindprint, run

HOLDOUT = "references/research/holdout.md"


def fix_after(output, needle):
    """The fix: line printed under the first FAIL line containing needle."""
    lines = output.splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith("FAIL") and needle in line)
    return lines[index + 1]


class QuickTierTests(SkillTestCase):
    def test_quick_tier_critic_logged_on_critics_track_needs_no_04_file(self):
        ledger = self.out / "references/sources.jsonl"
        edit(ledger, '"track": "decisions", "tier": "secondary", "critical": true',
             '"track": "critics", "tier": "secondary", "critical": true')
        self.assertFalse((self.out / "references/research/04-critics.md").exists())
        output = self.assert_passes("status")
        self.assertIn("PASS critics: 1 critical sources", output)

    def test_quick_tier_without_conversations_file_passes_status(self):
        (self.out / "references/research/02-conversations.md").unlink()
        edit(self.out / "references/research/05-decisions.md", "- [deepen] finding 1 [S01]",
             "- [deepen] finding 1 [S01]\n- [new] finding 2 [S01]\n- [new] finding 3 [S01]")
        self.assert_passes("status")


class UnsealedHoldoutTests(SkillTestCase):
    def scaffold_holdout(self):
        root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, root)
        run("init", root / "x", "--name", "Ada Lovelace", "--tier", "quick")
        (self.out / HOLDOUT).write_text((root / "x" / HOLDOUT).read_text(encoding="utf-8"),
                                        encoding="utf-8")

    def test_status_warns_when_holdout_is_still_the_scaffold(self):
        self.scaffold_holdout()
        output = self.assert_passes("status")
        self.assertIn("WARN holdout:", output)
        self.assertIn("not sealed yet", output)

    def test_status_fails_on_partly_filled_holdout(self):
        self.scaffold_holdout()
        edit(self.out / HOLDOUT, f"Source: {mindprint.TODO_MARK} TODO:", "Source: [S04]")
        output = self.assert_fails("status", "still has placeholder markers")
        self.assertNotIn("not sealed yet", output)

    def test_check_still_fails_on_unsealed_holdout_with_ten_sources(self):
        self.scaffold_holdout()
        output = self.assert_fails("check", "holdout")
        self.assertNotIn("not sealed yet", output)


class FixLineTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.out = self.root / "ada-lovelace-mind"
        run("init", self.out, "--name", "Ada Lovelace", "--tier", "quick")

    def test_placeholder_research_fail_has_its_own_fix(self):
        _, output = run("status", self.out)
        fix = fix_after(output, "still has placeholder markers")
        self.assertNotIn("Differs from prior", fix)
        self.assertIn("placeholder", fix)

    def test_missing_track_and_bad_prefix_have_their_own_fixes(self):
        research = self.out / "references/research"
        (research / "05-decisions.md").unlink()
        (research / "01-writings.md").write_text(
            "# Writings\n\nNotes.\n\n## Differs from prior\n\n- [maybe] x\n", encoding="utf-8")
        _, output = run("status", self.out)
        self.assertIn("track file", fix_after(output, "05-decisions.md is missing"))
        self.assertIn("[overturn]", fix_after(output, "item must start with"))


class ScaffoldTemplateTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.out = self.root / "ada-lovelace-mind"
        run("init", self.out, "--name", "Ada Lovelace", "--tier", "quick")
        self.skill = (self.out / "SKILL.md").read_text(encoding="utf-8")

    def test_scaffold_has_runtime_rules_and_template_labels(self):
        for needle in ("**I speak as myself.**", "**I stay in voice.**", "I do:", "Example:",
                       "In one line:", "Use for:", "**People assume:**", "Ada Lovelace's public"):
            self.assertIn(needle, self.skill)

    def test_scaffold_voice_tag_follows_blockquote_and_boundaries_are_paragraphs(self):
        lines = self.skill.splitlines()
        self.assertFalse([line for line in lines if line.startswith(">") and "[S" in line])
        for label in mindprint.BOUNDARY_LABELS:
            self.assertTrue(any(line.startswith(label) for line in lines), label)

    def test_scaffold_keeps_heading_order_but_fails_check(self):
        code, output = run("check", self.out)
        self.assertEqual(code, 1)
        self.assertFalse([line for line in fail_lines(output) if "headings" in line], output)
        self.assertIn("FAIL placeholders", output)


class AllowLowPrimaryTests(SkillTestCase):
    def lower_primary(self):
        ledger = self.out / "references/sources.jsonl"
        text = ledger.read_text(encoding="utf-8")
        ledger.write_text(text.replace('"tier": "primary"', '"tier": "secondary"', 3),
                          encoding="utf-8")

    def test_allow_low_primary_turns_fail_into_warn_with_reason(self):
        self.lower_primary()
        output = self.assert_passes("status", "--allow-low-primary", "one main work")
        self.assertIn("WARN primary-share:", output)
        self.assertIn("one main work", output)

    def test_allow_low_primary_needs_a_reason(self):
        self.lower_primary()
        self.assert_fails("status", "need >= 50%", "--allow-low-primary", " ")

    def test_json_reports_allowed_primary_share(self):
        self.lower_primary()
        _, output = run("status", self.out, "--allow-low-primary", "one work", "--json")
        found = [f for f in json.loads(output)["findings"] if f["name"] == "primary-share"]
        self.assertEqual(found[0]["level"], "WARN")


if __name__ == "__main__":
    unittest.main()
