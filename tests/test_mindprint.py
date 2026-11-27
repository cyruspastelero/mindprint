"""Behaviour tests for skills/mindprint/scripts/mindprint.py (stdlib unittest only)."""
import contextlib
import importlib.util
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "mindprint" / "scripts" / "mindprint.py"
_spec = importlib.util.spec_from_file_location("mindprint", SCRIPT)
mindprint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mindprint)

NAME = "test-person-mind"
ARCHIVES = {
    "S01": "Well done is better than well said. An investment in knowledge pays the best "
           "interest. Lost time is never found again, and what we call time enough always "
           "proves little enough.",
    "S02": "Never leave that till tomorrow which you can do today. Early to bed and early to "
           "rise makes a man healthy, wealthy and wise.",
    "S03": "I made it a rule to forbear all direct contradiction to the sentiments of others, "
           "and all positive assertion of my own.",
}
# id, track, tier, critical
SOURCES = [
    ("S01", "writings", "primary", False), ("S02", "writings", "primary", False),
    ("S03", "conversations", "primary", False), ("S04", "decisions", "primary", False),
    ("S05", "decisions", "secondary", True), ("S06", "writings", "primary", False),
    ("S07", "conversations", "secondary", False), ("S08", "decisions", "primary", False),
    ("S09", "writings", "tertiary", False), ("S10", "decisions", "secondary", False),
]
HOLDOUT_EVENTS = [
    "He sold the printing shop in the spring and moved his savings into a quiet partnership.",
    "She turned down the appointment because the committee would not publish its minutes.",
    "They rebuilt the library from donated crates after the flood wrecked the reading room.",
]


def skill_md(tier="quick"):
    moves = "\n".join(f"### Move {i}\nWhen: a choice must be made fast [S0{i}]\nAct, then "
                      "review.\n" for i in range(1, 6))
    models = "\n".join(f"### Model {i}\nEvidence: seen across the letters [S02]\nBreaks when: "
                       "the stakes are new.\n" for i in range(1, 4))
    heuristics = "\n".join(f"- Heuristic number {i} [S04]" for i in range(1, 6))
    cases = "\n".join(f"- C0{i} · Case {i}" for i in range(1, 7))
    boundaries = "\n".join(f"- {label} described here." for label in mindprint.BOUNDARY_LABELS)
    return f"""---
name: {NAME}
description: Thinks in trade-offs and plain sayings. Use when the user asks for Test Person's perspective, "what would Test Person do", or to switch to Test Person. Do not trigger on general questions.
metadata:
  mindprint: "0.1.0"
  researched: "2026-11-28"
  tier: {tier}
---

# Test Person

## How to use me

**Disclaimer:** This is a model of the public record of Test Person, not the person. Research cutoff 2026-11-28.

## Who I am

A printer who wrote a great deal [S01].

## Moves

{moves}
## Mental models

{models}
## Heuristics

{heuristics}

## Common misreadings

- People think the sayings were sincere advice [S05]
- People think the thrift was natural to him [S07]

## Voice

- Short, concrete, wry.

> Well done is better than well said.
[S01]

> Never leave that till tomorrow which you can do today. [S02]

More in references/voice.md.

## Casebook index

{cases}

Full cards in references/casebook.md.

## Tensions

- Preached thrift, spent freely.
- Praised humility, sought credit.

## Boundaries

{boundaries}

## Sources

Ledger: references/sources.jsonl. 6 primary, 3 secondary, 1 tertiary.
"""


def casebook_md(count=6):
    cards = []
    for i in range(1, count + 1):
        cards.append(
            f"## C{i:02d} · Case {i}\nSituation: a dispute at the club.\nWhat they did: asked a "
            f"question instead.\nIn their words: \"I made it a rule to forbear all direct "
            f"contradiction\" [S03]\nOutcome: the club agreed.\nUse for: arguments.\n"
            f"Sources: [S03, S04]\n")
    return "# Casebook\n\n" + "\n".join(cards)


def track_md(title, items):
    body = "\n".join(f"- [{kind}] finding {n} [S01]" for n, kind in enumerate(items, 1))
    return f"# {title}\n\nNotes with sources [S01].\n\n## Differs from prior\n\n{body}\n"


def holdout_md():
    items = [f"## H{i} · Event {i}\nSource: [S0{i + 3}]\nQuestion: What would you do in case "
             f"{i}?\nWhat happened: {event}\n" for i, event in enumerate(HOLDOUT_EVENTS, 1)]
    return "# Holdout\n\n" + "\n".join(items)


def ledger_lines():
    lines = []
    for sid, track, tier, critical in SOURCES:
        archive = f"sources/{sid}.txt" if sid in ARCHIVES else ""
        lines.append(json.dumps({"id": sid, "title": f"Title {sid}", "by": "Someone",
                                 "date": "1757", "url": "", "track": track, "tier": tier,
                                 "critical": critical, "archive": archive}))
    return "\n".join(lines) + "\n"


def build_skill(root, tier="quick"):
    """Write a complete, valid quick-tier output skill and return its path."""
    out = Path(root) / NAME
    files = {
        "SKILL.md": skill_md(tier),
        "FIDELITY.md": "# Fidelity\n\nBlind test: the skill arm won 3 of 3 questions.\n",
        "references/casebook.md": casebook_md(),
        "references/voice.md": "# Voice\n\n> An investment in knowledge pays the best interest. "
                               "[S01]\n\nOn time: \"Lost time is never found again ... proves "
                               "little enough\" [S01]\n",
        "references/sources.jsonl": ledger_lines(),
        "references/research/00-prior.md": "# Prior\n\nI expected a cheerful moralist.\n",
        "references/research/01-writings.md": track_md("Writings", ["new", "deepen"]),
        "references/research/02-conversations.md": track_md("Conversations", ["overturn", "new"]),
        "references/research/05-decisions.md": track_md("Decisions", ["deepen"]),
        "references/research/holdout.md": holdout_md(),
    }
    files.update({f"references/sources/{sid}.txt": text for sid, text in ARCHIVES.items()})
    for rel, text in files.items():
        (out / rel).parent.mkdir(parents=True, exist_ok=True)
        (out / rel).write_text(text, encoding="utf-8")
    return out


def run(*argv):
    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        code = mindprint.main([str(a) for a in argv])
    return code, buffer.getvalue()


def edit(path, old, new):
    text = Path(path).read_text(encoding="utf-8")
    if old not in text:
        raise AssertionError(f"{old!r} not in {path}")
    Path(path).write_text(text.replace(old, new), encoding="utf-8")


def fail_lines(output):
    return [line for line in output.splitlines() if line.startswith("FAIL")]


class SkillTestCase(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        self.out = build_skill(self.root)

    def assert_fails(self, command, needle, *extra):
        code, output = run(command, self.out, *extra)
        self.assertEqual(code, 1, output)
        self.assertTrue(any(needle in line for line in fail_lines(output)),
                        f"no FAIL containing {needle!r}:\n{output}")
        return output

    def assert_passes(self, command, *extra):
        code, output = run(command, self.out, *extra)
        self.assertEqual(code, 0, output)
        return output


class FixtureTests(SkillTestCase):
    def test_complete_fixture_passes_check(self):
        output = self.assert_passes("check")
        self.assertNotIn("WARN", output)

    def test_complete_fixture_passes_status(self):
        self.assert_passes("status")

    def test_complete_fixture_passes_strict_quotes(self):
        output = self.assert_passes("quotes", "--strict")
        self.assertGreaterEqual(output.count("PASS quote:"), 5)

    def test_fail_lines_have_indented_fix(self):
        edit(self.out / "SKILL.md", "## Tensions", "## Tension")
        _, output = run("check", self.out)
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if line.startswith("FAIL"):
                self.assertTrue(lines[i + 1].startswith("  fix: "), output)

    def test_json_output_lists_findings(self):
        code, output = run("check", self.out, "--json")
        payload = json.loads(output)
        self.assertEqual(code, 0)
        self.assertTrue(payload["ok"])
        self.assertEqual({f["level"] for f in payload["findings"]}, {"PASS"})

    def test_missing_out_dir_fails_with_path(self):
        code, output = run("check", self.root / "nope")
        self.assertEqual(code, 1)
        self.assertIn("not a directory", output)


class InitTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)

    def test_fresh_init_scaffold_fails_check(self):
        out = self.root / "ada-lovelace-mind"
        self.assertEqual(run("init", out, "--name", "Ada Lovelace")[0], 0)
        code, output = run("check", out)
        self.assertEqual(code, 1)
        self.assertIn("FAIL placeholders", output)
        for name in ("01-writings.md", "06-timeline.md", "holdout.md", "00-prior.md"):
            self.assertTrue((out / "references/research" / name).is_file())

    def test_fresh_init_scaffold_fails_status(self):
        out = self.root / "ada-lovelace-mind"
        run("init", out, "--name", "Ada Lovelace", "--tier", "quick")
        code, output = run("status", out)
        self.assertEqual(code, 1)
        self.assertIn("FAIL prior", output)
        self.assertIn("still has placeholder markers", output)
        self.assertFalse((out / "references/research/03-fragments.md").exists())

    def test_init_writes_name_tier_and_markers(self):
        out = self.root / "x"
        run("init", out, "--name", "Ada Lovelace", "--tier", "deep")
        text = (out / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("name: ada-lovelace-mind", text)
        self.assertIn("tier: deep", text)
        self.assertIn(mindprint.TODO_MARK, text)
        self.assertEqual((out / "references/sources.jsonl").read_text(), "")

    def test_init_topic_names_field_skill(self):
        out = self.root / "stoicism-field"
        run("init", out, "--name", "Stoicism", "--topic")
        self.assertIn("name: stoicism-field", (out / "SKILL.md").read_text(encoding="utf-8"))

    def test_init_refuses_non_empty_dir(self):
        out = self.root / "full"
        out.mkdir()
        (out / "keep.txt").write_text("x")
        code, output = run("init", out, "--name", "Ada")
        self.assertEqual(code, 1)
        self.assertIn("not empty", output)
        self.assertEqual(sorted(p.name for p in out.iterdir()), ["keep.txt"])


class FrontmatterTests(SkillTestCase):
    def test_description_over_1024_chars_fails(self):
        edit(self.out / "SKILL.md", "Thinks in trade-offs", "x" * 1100)
        self.assert_fails("check", "max 1024")

    def test_description_over_400_chars_warns(self):
        edit(self.out / "SKILL.md", "Thinks in trade-offs", "x" * 300)
        output = self.assert_passes("check")
        self.assertIn("WARN description", output)

    def test_description_without_trigger_guard_fails(self):
        edit(self.out / "SKILL.md", "Do not trigger on general questions.", "")
        self.assert_fails("check", "Do not trigger on general questions")

    def test_bad_name_fails(self):
        edit(self.out / "SKILL.md", f"name: {NAME}", "name: Test Person")
        self.assert_fails("check", "must be <slug>-mind")

    def test_bad_tier_fails(self):
        edit(self.out / "SKILL.md", "tier: quick", "tier: huge")
        self.assert_fails("check", "metadata.tier")

    def test_missing_frontmatter_fails(self):
        edit(self.out / "SKILL.md", "---\nname:", "name:")
        self.assert_fails("check", "frontmatter")


class SkillBodyTests(SkillTestCase):
    def test_missing_heading_fails(self):
        edit(self.out / "SKILL.md", "## Tensions\n", "")
        self.assert_fails("check", "missing '## Tensions'")

    def test_headings_out_of_order_fail(self):
        edit(self.out / "SKILL.md", "## Who I am", "## Placeholder")
        edit(self.out / "SKILL.md", "## Sources\n", "## Sources\n\n## Who I am\n\nLate. [S01]\n")
        self.assert_fails("check", "out of order")

    def test_skill_over_300_lines_fails(self):
        edit(self.out / "SKILL.md", "A printer who", "\n" * 300 + "A printer who")
        self.assert_fails("check", "max 300")

    def test_missing_disclaimer_fails(self):
        edit(self.out / "SKILL.md", "**Disclaimer:**", "Note:")
        self.assert_fails("check", "**Disclaimer:**")

    def test_disclaimer_without_cutoff_date_fails(self):
        edit(self.out / "SKILL.md", " Research cutoff 2026-11-28.", "")
        self.assert_fails("check", "research cutoff")

    def test_too_few_moves_fails(self):
        edit(self.out / "SKILL.md", "### Move 5\n", "Move five is folded in.\n")
        self.assert_fails("check", "need 5-8")

    def test_move_without_when_fails(self):
        edit(self.out / "SKILL.md", "When: a choice must be made fast [S03]",
             "If a choice must be made fast [S03]")
        self.assert_fails("check", "no line starting 'When:'")

    def test_model_without_breaks_when_fails(self):
        edit(self.out / "SKILL.md", "Breaks when: the stakes are new.\n\n### Model 2",
             "\n### Model 2")
        self.assert_fails("check", "'Breaks when:'")

    def test_heuristic_without_tag_fails(self):
        edit(self.out / "SKILL.md", "- Heuristic number 3 [S04]", "- Heuristic number 3")
        self.assert_fails("check", "list item has no [Sxx] tag")

    def test_too_many_heuristics_fail(self):
        extra = "\n".join(f"- More {i} [S04]" for i in range(6))
        edit(self.out / "SKILL.md", "- Heuristic number 5 [S04]", "- Heuristic number 5 [S04]\n" + extra)
        self.assert_fails("check", "need 5-10")

    def test_one_tension_fails(self):
        edit(self.out / "SKILL.md", "- Praised humility, sought credit.\n", "")
        self.assert_fails("check", "need >= 2")

    def test_voice_with_one_blockquote_fails(self):
        edit(self.out / "SKILL.md", "> Never leave that till tomorrow which you can do today. [S02]",
             "Plain line.")
        self.assert_fails("check", "cited blockquotes")

    def test_missing_boundary_label_fails(self):
        edit(self.out / "SKILL.md", "**Prior bias**", "Prior bias")
        self.assert_fails("check", "missing **Prior bias**")

    def test_casebook_index_unknown_card_fails(self):
        edit(self.out / "SKILL.md", "- C06 · Case 6", "- C06 · Case 6\n- C42 · Ghost")
        self.assert_fails("check", "C42 is not a card")

    def test_sources_section_without_counts_fails(self):
        edit(self.out / "SKILL.md", "6 primary, 3 secondary", "many sources")
        self.assert_fails("check", "needs the ledger's primary count")


class CasebookTests(SkillTestCase):
    def test_casebook_below_tier_minimum_fails(self):
        edit(self.out / "SKILL.md", "tier: quick", "tier: standard")
        self.assert_fails("check", "standard tier needs >= 12")

    def test_casebook_card_missing_field_fails(self):
        path = self.out / "references/casebook.md"
        text = path.read_text(encoding="utf-8")
        path.write_text(text.replace("Outcome: the club agreed.\n", "", 1), encoding="utf-8")
        self.assert_fails("check", "C01 has no 'Outcome:' line")

    def test_duplicate_card_id_fails(self):
        edit(self.out / "references/casebook.md", "## C06 · Case 6", "## C05 · Case 6")
        self.assert_fails("check", "is a duplicate id")


class TagAndTextTests(SkillTestCase):
    def test_unknown_source_tag_fails(self):
        edit(self.out / "SKILL.md", "wrote a great deal [S01]", "wrote a great deal [S99]")
        self.assert_fails("check", "tag S99 is unknown source")

    def test_malformed_tag_fails(self):
        edit(self.out / "SKILL.md", "wrote a great deal [S01]", "wrote a great deal [S1]")
        self.assert_fails("check", "tag S1 is malformed")

    def test_multi_id_tag_resolves_each_id(self):
        edit(self.out / "SKILL.md", "wrote a great deal [S01]", "wrote a great deal [S01, S77]")
        self.assert_fails("check", "tag S77 is unknown source")

    def test_absolute_path_fails(self):
        edit(self.out / "SKILL.md", "A printer who", "See /Users/someone/notes. A printer who")
        self.assert_fails("check", "absolute path")

    def test_windows_path_fails(self):
        edit(self.out / "references/voice.md", "# Voice", "# Voice\n\nC:\\notes\\x.txt")
        self.assert_fails("check", "absolute path")

    def test_leftover_todo_fails(self):
        edit(self.out / "FIDELITY.md", "Blind test", "TODO blind test")
        self.assert_fails("check", "FIDELITY.md:3: TODO")

    def test_placeholder_marker_fails(self):
        edit(self.out / "references/voice.md", "# Voice", "# Voice\n" + mindprint.TODO_MARK)
        self.assert_fails("check", "placeholder marker")

    def test_angle_placeholder_in_skill_fails(self):
        edit(self.out / "SKILL.md", "A printer who", "<one line about them> A printer who")
        self.assert_fails("check", "template placeholder <one line about them>")

    def test_angle_placeholder_in_casebook_and_fidelity_fails(self):
        edit(self.out / "references/casebook.md", "a dispute at the club", "<Name> argued")
        edit(self.out / "FIDELITY.md", "Blind test", "<quote> Blind test")
        output = self.assert_fails("check", "references/casebook.md:4: template placeholder <Name>")
        self.assertIn("FIDELITY.md:3: template placeholder <quote>", output)

    def test_html_tags_comments_and_code_spans_are_not_placeholders(self):
        edit(self.out / "FIDELITY.md", "Blind test", "Line<br>two<sup>1</sup> `<quote>` "
             "<!-- a <note> -->\n<details><summary>More</summary>x</details>\n"
             "<https://example.com>\n```\n<Name>\n```\nBlind test")
        self.assert_passes("check")

    def test_code_fence_tags_are_ignored(self):
        edit(self.out / "FIDELITY.md", "Blind test", "```\n[S99]\n```\nBlind test")
        self.assert_passes("check")


class LedgerTests(SkillTestCase):
    def ledger(self):
        return self.out / "references/sources.jsonl"

    def test_ledger_invalid_json_names_line(self):
        with self.ledger().open("a", encoding="utf-8") as handle:
            handle.write("{not json\n")
        self.assert_fails("check", "sources.jsonl:11: invalid JSON")

    def test_ledger_bad_track_fails(self):
        edit(self.ledger(), '"track": "decisions"',
             '"track": "gossip"')
        self.assert_fails("status", "track 'gossip'")

    def test_ledger_missing_field_fails(self):
        edit(self.ledger(), '"by": "Someone", ', "")
        self.assert_fails("check", "missing field 'by'")

    def test_ledger_critical_must_be_bool(self):
        edit(self.ledger(), '"critical": true', '"critical": "yes"')
        self.assert_fails("check", "'critical' must be a bool")

    def test_ledger_bad_id_and_date_fail(self):
        edit(self.ledger(), '"id": "S10"', '"id": "X10"')
        edit(self.ledger(), '"date": "1757"', '"date": "57"')
        output = self.assert_fails("check", "must be S plus 2-3 digits")
        self.assertIn("date '57'", output)

    def test_ledger_duplicate_id_fails(self):
        edit(self.ledger(), '"id": "S10"', '"id": "S09"')
        self.assert_fails("check", "duplicate id S09")

    def test_missing_archive_file_fails(self):
        (self.out / "references/sources/S02.txt").unlink()
        self.assert_fails("check", "references/sources/S02.txt does not exist")

    def test_archive_outside_references_fails(self):
        edit(self.ledger(), '"archive": "sources/S03.txt"', '"archive": "../S03.txt"')
        self.assert_fails("check", "must be a path inside references/")


class QuoteTests(SkillTestCase):
    def test_quote_missing_from_archive_fails(self):
        edit(self.out / "SKILL.md", "> Well done is better than well said.",
             "> Well said is better than well done.")
        self.assert_fails("quotes", "not found in sources/S01.txt")

    def test_check_runs_quotes(self):
        edit(self.out / "SKILL.md", "> Well done is better than well said.", "> Invented words.")
        self.assert_fails("check", "not found in sources/S01.txt")

    def test_inline_quote_missing_from_archive_fails(self):
        edit(self.out / "references/casebook.md", "forbear all direct contradiction",
             "forbid all direct contradiction")
        self.assert_fails("quotes", "casebook.md:")

    def test_ellipsis_quote_matches_fragments_in_order(self):
        output = self.assert_passes("quotes")
        self.assertIn("PASS quote: references/voice.md:5", output)

    def test_unicode_ellipsis_and_out_of_order_fragments_fail(self):
        edit(self.out / "references/voice.md", "Lost time is never found again ... proves little enough",
             "proves little enough … Lost time is never found again")
        self.assert_fails("quotes", "voice.md:5")

    def test_curly_quotes_dashes_and_case_normalise(self):
        edit(self.out / "references/sources/S02.txt", "Never leave that", "NEVER — leave that")
        edit(self.out / "SKILL.md", "> Never leave that till tomorrow",
             "> “Never leave—that till tomorrow")
        edit(self.out / "SKILL.md", "do today. [S02]", "do today.” [S02]")
        self.assert_passes("quotes", "--strict")

    def test_bracket_insertion_ignored(self):
        edit(self.out / "SKILL.md", "> Never leave that till tomorrow",
             "> Never leave [the work] that till tomorrow")
        self.assert_passes("quotes", "--strict")

    def test_check_strict_fails_unarchived_quote(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe said \"one two three "
             "four five six seven\" in print [S04].\n")
        self.assert_passes("check")
        self.assert_fails("check", "has no archive", "--strict")

    def test_check_help_lists_strict(self):
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer), self.assertRaises(SystemExit):
            mindprint.main(["check", "--help"])
        self.assertIn("--strict", buffer.getvalue())
        self.assertIn("unarchived quotes FAIL", buffer.getvalue())

    def test_unarchived_quote_warns_and_strict_fails(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe said \"one two three "
             "four five six seven\" in print [S04].\n")
        output = self.assert_passes("quotes")
        self.assertIn("WARN quote: SKILL.md:", output)
        self.assert_fails("quotes", "has no archive", "--strict")

    def test_short_double_quotes_are_not_quotes(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe said \"not a quote\" "
             "[S01].\n")
        self.assert_passes("quotes", "--strict")

    def test_quote_tag_on_next_line_counts(self):
        edit(self.out / "SKILL.md", "## Who I am\n", "## Who I am\n\nHe wrote \"An investment in "
             "knowledge pays the worst interest\"\n[S01]\n")
        self.assert_fails("quotes", "SKILL.md:")

    def test_blockquote_attribution_line_is_ignored(self):
        edit(self.out / "SKILL.md", "> Well done is better than well said.\n",
             "> Well done is better than well said.\n> — Test Person\n")
        self.assert_passes("quotes", "--strict")

    def test_normalise_and_fragments_helpers(self):
        source = mindprint.normalise("It's “Done” — well, done!")
        self.assertEqual(source, "it's done well done")
        frags = mindprint.quote_fragments("It’s done … done [sic] [S01]")
        self.assertEqual(frags, ["it's done", "done"])
        self.assertTrue(mindprint.fragments_in_order(frags, source))
        self.assertFalse(mindprint.fragments_in_order(["well", "it's"], source))


class HoldoutLeakTests(SkillTestCase):
    def test_holdout_sentence_in_casebook_fails(self):
        edit(self.out / "references/casebook.md", "Situation: a dispute at the club.",
             "Situation: " + HOLDOUT_EVENTS[1])
        self.assert_fails("check", "H2 'What happened' leaks into references/casebook.md")

    def test_holdout_shingle_in_skill_fails(self):
        edit(self.out / "SKILL.md", "A printer who", "He refused because the committee would "
             "not publish its minutes. A printer who")
        self.assert_fails("check", "leaks into SKILL.md")

    def test_holdout_seven_words_do_not_leak(self):
        edit(self.out / "SKILL.md", "A printer who", "the committee would not publish its "
             "papers. A printer who")
        self.assert_passes("check")


class StatusTests(SkillTestCase):
    def ledger(self):
        return self.out / "references/sources.jsonl"

    def test_status_low_primary_share_fails(self):
        text = self.ledger().read_text(encoding="utf-8").replace('"tier": "primary"',
                                                                  '"tier": "secondary"', 3)
        self.ledger().write_text(text, encoding="utf-8")
        self.assert_fails("status", "need >= 50%")

    def test_status_standard_needs_two_critical(self):
        edit(self.out / "SKILL.md", "tier: quick", "tier: standard")
        self.assert_fails("status", "standard tier needs >= 2")

    def test_status_standard_needs_all_tracks(self):
        edit(self.out / "SKILL.md", "tier: quick", "tier: standard")
        self.assert_fails("status", "03-fragments.md is missing")

    def test_status_no_critical_source_fails(self):
        edit(self.ledger(), '"critical": true', '"critical": false')
        self.assert_fails("status", "0 critical sources")

    def test_status_small_ledger_warns_no_holdout(self):
        lines = self.ledger().read_text(encoding="utf-8").splitlines()
        self.ledger().write_text("\n".join(lines[:9]) + "\n", encoding="utf-8")
        edit(self.out / "references/research/holdout.md", "## H3", "## H3 extra\n## H4 · x\n## H5")
        output = self.assert_passes("status")
        self.assertIn("WARN holdout: no holdout test", output)

    def test_status_holdout_too_few_items_fails(self):
        path = self.out / "references/research/holdout.md"
        path.write_text(path.read_text(encoding="utf-8").split("## H3")[0], encoding="utf-8")
        self.assert_fails("status", "2 items, need 3-5")

    def test_status_holdout_item_without_source_tag_fails(self):
        edit(self.out / "references/research/holdout.md", "Source: [S04]", "Source: a letter")
        self.assert_fails("status", "H1 Source has no [Sxx] tag")

    def test_status_bad_differs_prefix_fails(self):
        edit(self.out / "references/research/05-decisions.md", "- [deepen]", "- [maybe]")
        self.assert_fails("status", "must start with [overturn], [deepen] or [new]")

    def test_status_too_few_differs_items_fails(self):
        edit(self.out / "references/research/05-decisions.md", "- [deepen] finding 1 [S01]", "")
        self.assert_fails("status", "4 items, quick tier needs >= 5")

    def test_status_track_without_closing_section_fails(self):
        edit(self.out / "references/research/01-writings.md", "## Differs from prior",
             "## Other")
        self.assert_fails("status", "does not end with '## Differs from prior'")

    def test_status_placeholder_prior_fails(self):
        (self.out / "references/research/00-prior.md").write_text(
            f"# Prior\n\n{mindprint.TODO_MARK} TODO: write it\n", encoding="utf-8")
        self.assert_fails("status", "00-prior.md:3")

    def test_status_missing_prior_fails(self):
        (self.out / "references/research/00-prior.md").unlink()
        self.assert_fails("status", "00-prior.md is missing")


class BlindTests(SkillTestCase):
    def answers(self):
        skill = self.root / "skill.md"
        skill.write_text("Answer from the persona.\nUsing the skill, I say save.\nSee C03.\n"
                         f"Built by {NAME}.\nKeep the tag [S01].\n", encoding="utf-8")
        base = self.root / "base.md"
        base.write_text("A plain answer.\nAs an AI, I cannot know.\nThe baseline view.\n",
                        encoding="utf-8")
        return [f"--arm=skill={skill}", f"--arm=baseline={base}"]

    def blind(self, question, seed=1, date="2026-11-28"):
        return run("blind", self.out, "--question", question, *self.answers(), "--seed", seed,
                   "--date", date)

    def vdir(self):
        return self.out / "references/validation/2026-11-28"

    def packets(self, question="Q1"):
        return "\n".join(p.read_text(encoding="utf-8")
                         for p in sorted((self.vdir() / question).iterdir()))

    def blind_text(self, text):
        answer, other = self.root / "one.md", self.root / "two.md"
        answer.write_text(text, encoding="utf-8")
        other.write_text("Other answer.\n", encoding="utf-8")
        code, output = run("blind", self.out, "--question", "Q9", f"--arm=skill={answer}",
                           f"--arm=baseline={other}", "--seed", 1, "--date", "2026-11-28")
        self.assertEqual(code, 0, output)
        return self.packets("Q9")

    def test_blind_drops_meta_lines_and_keeps_tags(self):
        self.assertEqual(self.blind("Q1")[0], 0)
        self.assertEqual(sorted(p.name for p in (self.vdir() / "Q1").iterdir()), ["A.md", "B.md"])
        joined = self.packets()
        for banned in ("Using the skill", "As an AI", "C03", NAME):
            self.assertNotIn(banned, joined)
        for kept in ("Keep the tag [S01].", "A plain answer.", "See.", "Built by the person's."):
            self.assertIn(kept, joined)

    def test_blind_drops_access_and_arm_label_lines(self):
        text = self.blind_text("Arm: skill\nI don't have access to his diaries.\nReal point.\n")
        self.assertNotIn("Arm:", text)
        self.assertNotIn("access to", text)
        self.assertIn("Real point.", text)

    def test_blind_keeps_lines_that_mention_skill_in_prose(self):
        text = self.blind_text("Negotiation is a skill he practised.\nThe baseline was low.\n")
        self.assertIn("Negotiation is a skill he practised.", text)
        self.assertIn("The baseline was low.", text)

    def test_blind_scrubs_case_ids_inline(self):
        text = self.blind_text("As in C05 · The kite, he waited (C07).\nSee C12, then act.\n")
        self.assertIn("As in The kite, he waited.", text)
        self.assertIn("See, then act.", text)
        self.assertNotRegex(text, r"C\d+")

    def test_blind_replaces_skill_slug_inline(self):
        text = self.blind_text("This is test-person thinking.\n")
        self.assertIn("This is the person's thinking.", text)

    def test_blind_seed_is_deterministic(self):
        self.blind("Q1", seed=7)
        self.blind("Q2", seed=7)
        key = json.loads((self.vdir() / "key.json").read_text(encoding="utf-8"))
        self.assertEqual(key["Q1"], key["Q2"])
        self.assertEqual(sorted(key["Q1"].values()), ["baseline", "skill"])

    def test_blind_output_does_not_reveal_mapping(self):
        _, output = self.blind("Q1")
        self.assertNotIn("A=", output)
        self.assertNotIn("skill", output.split("mapping")[0].split("answers to")[0])

    def test_blind_refuses_repeat_question(self):
        self.blind("Q1")
        code, output = self.blind("Q1")
        self.assertEqual(code, 1)
        self.assertIn("already blinded", output)

    def test_blind_needs_two_arms(self):
        code, output = run("blind", self.out, "--question", "Q1", self.answers()[0])
        self.assertEqual(code, 1)
        self.assertIn("need >= 2", output)

    def test_blind_missing_answer_file_names_it(self):
        code, output = run("blind", self.out, "--question", "Q1", "--arm", "skill=nope.md",
                           "--arm", "baseline=nope2.md")
        self.assertEqual(code, 1)
        self.assertIn("nope.md: cannot read file", output)

    def grade(self, grades):
        letters = json.loads((self.vdir() / "key.json").read_text(encoding="utf-8"))
        path = self.root / "grades.json"
        resolved = {q: {letter: grades[q][arm] for letter, arm in letters[q].items()}
                    for q in grades}
        path.write_text(json.dumps({**resolved, "max": 10}), encoding="utf-8")
        return run("unblind", self.out, "--grades", path)

    def test_blind_then_unblind_totals_per_arm(self):
        self.blind("Q1", seed=3)
        self.blind("H1", seed=4)
        code, output = self.grade({"Q1": {"skill": 8, "baseline": 5},
                                   "H1": {"skill": 9, "baseline": 4}})
        self.assertEqual(code, 0, output)
        self.assertIn("| Question | skill | baseline | Flag |", output)
        self.assertIn("| **Total** | **17** | **9** | |", output)
        results = (self.vdir() / "results.md").read_text(encoding="utf-8")
        self.assertIn("| Q1 | 8 | 5 |  |", results)

    def test_unblind_flags_holdout_tie_within_two(self):
        self.blind("H1")
        self.blind("Q1")
        code, output = self.grade({"H1": {"skill": 7, "baseline": 6},
                                   "Q1": {"skill": 7, "baseline": 6}})
        self.assertEqual(code, 0)
        self.assertIn("| H1 | 7 | 6 | tie (within 2 points) |", output)
        self.assertIn("| Q1 | 7 | 6 |  |", output)
        self.assertIn("WARN tie: H1", output)

    def test_unblind_unknown_letter_fails(self):
        self.blind("Q1")
        path = self.root / "grades.json"
        path.write_text(json.dumps({"Q1": {"A": 5, "Z": 3}}), encoding="utf-8")
        code, output = run("unblind", self.out, "--grades", path, "--date", "2026-11-28")
        self.assertEqual(code, 1)
        self.assertIn("Q1.Z is not in key.json", output)
        self.assertFalse((self.vdir() / "results.md").exists())

    def test_unblind_score_above_max_fails(self):
        self.blind("Q1")
        path = self.root / "grades.json"
        path.write_text(json.dumps({"Q1": {"A": 11, "B": 3}, "max": 10}), encoding="utf-8")
        code, output = run("unblind", self.out, "--grades", path)
        self.assertEqual(code, 1)
        self.assertIn("must be 0-10", output)

    def test_unblind_without_key_fails(self):
        path = self.root / "grades.json"
        path.write_text("{}", encoding="utf-8")
        code, output = run("unblind", self.out, "--grades", path)
        self.assertEqual(code, 1)
        self.assertIn("run blind first", output)

    def test_unblind_bad_grades_json_names_file_and_line(self):
        self.blind("Q1")
        path = self.root / "grades.json"
        path.write_text("{\n  bad\n}", encoding="utf-8")
        code, output = run("unblind", self.out, "--grades", path)
        self.assertEqual(code, 1)
        self.assertIn("grades.json:2: invalid JSON", output)


if __name__ == "__main__":
    unittest.main()
