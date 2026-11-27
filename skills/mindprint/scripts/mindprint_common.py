"""Shared constants and helpers for the mindprint CLI; mindprint.py is the entry point."""
from __future__ import annotations

import json
import re
from pathlib import Path

VERSION = "0.1.0"
TRACKS = ("writings", "conversations", "fragments", "critics", "decisions", "timeline")
TRACK_FILES = {t: f"0{i}-{t}.md" for i, t in enumerate(TRACKS, 1)}
QUICK_TRACKS, QUICK_REQUIRED = ("writings", "conversations", "decisions"), ("writings", "decisions")
TIERS = ("quick", "standard", "deep")
SOURCE_TIERS = ("primary", "secondary", "tertiary")
MIN_CARDS = {"quick": 6, "standard": 12, "deep": 20}
SKILL_HEADINGS = tuple("## " + h for h in (
    "How to use me", "Who I am", "Moves", "Mental models", "Heuristics", "Common misreadings",
    "Voice", "Casebook index", "Tensions", "Boundaries", "Sources"))
BOUNDARY_LABELS = ("**Known ground**", "**Inferred ground**", "**Silent or wrong**",
                   "**Blind spots**", "**Prior bias**", "**What would change this**")
CARD_FIELDS = ("Situation", "What they did", "In their words", "Outcome", "Use for", "Sources")
HOLDOUT_FIELDS = ("Source", "Question", "What happened")
LEDGER_FIELDS = {"id": str, "title": str, "by": str, "date": str, "url": str,
                 "track": str, "tier": str, "critical": bool, "archive": str}
LEDGER = "references/sources.jsonl"
CASEBOOK, VOICE = "references/casebook.md", "references/voice.md"
HOLDOUT, PRIOR = "references/research/holdout.md", "references/research/00-prior.md"
REQUIRED_FILES = ("SKILL.md", "FIDELITY.md", CASEBOOK, VOICE, LEDGER)
LEAK_TARGETS = ("SKILL.md", CASEBOOK, VOICE)
SKILL_MAX_LINES = 300

TODO_MARK = "<!-- mindprint:todo -->"
TODO_RE = re.compile(r"<!--\s*mindprint:todo\s*-->|\bTODO\b")
ABS_RE = re.compile(r"/Users/|/home/|\b[A-Za-z]:\\")
TAG_RE = re.compile(r"\[(S\d+(?:\s*,\s*S\d+)*)\]")
ID_RE = re.compile(r"S\d{2,3}")
DATE_RE = re.compile(r"(\d{4}(-\d{2}(-\d{2})?)?)?")
DAY_RE = re.compile(r"\d{4}-\d{2}-\d{2}")
NAME_RE = re.compile(r"[a-z0-9]+(-[a-z0-9]+)*-(mind|field)")
LIST_RE = re.compile(r"^([-*+]|\d+[.)])\s+(.*)$")
BQ_RE = re.compile(r"^\s*>\s?")
ATTRIB_RE = re.compile(r"^\s*(—|–|--)\s")
INLINE_RE = re.compile(r'"([^"]+)"|“([^”]+)”')
DIFF_RE = re.compile(r"^\[(overturn|deepen|new)\]")
CARD_RE = re.compile(r"^## (C\d+)\s*·\s*(\S.*)$")
HOLD_RE = re.compile(r"^## (H\d+)\s*·\s*(\S.*)$")
INDEX_RE = re.compile(r"\b(C\d+)\s*·\s*\S")
QID_RE = re.compile(r"[A-Za-z0-9_-]+")
PUNCT_MAP = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "‚": "'",
                           "–": "-", "—": "-", "‒": "-", "―": "-", "−": "-"})

FIXES = {  # default fix line per finding name; a call can pass its own
    "error": "fix the file or argument named above and rerun",
    "files": "create it (init scaffolds every file)",
    "ledger": "fields: id, title, by, date, url, track, tier, critical, archive (see SPEC)",
    "sources": "research and add sources to references/sources.jsonl",
    "primary-share": "find more of their own words or first-hand records",
    "critics": "add sources that criticise or dispute them, with critical: true",
    "research": "end each track with '## Differs from prior' ([overturn]/[deepen]/[new] items)",
    "differs-from-prior": "record what each track overturned, deepened or added versus the prior",
    "holdout": "seal 3-5 items: '## H1 · title', Source: [Sxx], Question:, What happened:",
    "prior": "write what you believed before research, then remove the TODO markers",
    "frontmatter": "start SKILL.md with a '---' block: name, description, metadata",
    "description": "one line, <= 1024 chars, ending 'Do not trigger on general questions.'",
    "headings": "order: " + ", ".join(h[3:] for h in SKILL_HEADINGS),
    "length": "move detail into references/",
    "disclaimer": "'**Disclaimer:** a model of the public record, not the person; cutoff <date>.'",
    "section": "see the 'Output SKILL.md' rules in docs/SPEC.md",
    "casebook": "each card: '## C01 · title' plus " + ", ".join(CARD_FIELDS) + " lines",
    "tags": "fix the tag or add the source to references/sources.jsonl",
    "paths": "use paths relative to the skill folder",
    "placeholders": "replace placeholder text with real content",
    "holdout-leak": "rephrase or remove it; holdout answers must stay out of the skill",
    "quote": "copy the exact wording from the archive, mark cuts with ..., or drop the quote",
    "grades": "grades.json: {\"Q1\": {\"A\": 7, \"B\": 5}, \"max\": 10}",
}


class MindprintError(Exception):
    """A problem that stops a command; the message names the file involved."""


class Report:
    """Collects PASS/WARN/FAIL findings."""

    def __init__(self):
        self.findings = []

    def add(self, level, name, message, fix=""):
        self.findings.append({"level": level, "name": name, "message": message, "fix": fix})

    def ok(self, name, message):
        self.add("PASS", name, message)

    def warn(self, name, message):
        self.add("WARN", name, message)

    def fail(self, name, message, fix=None):
        self.add("FAIL", name, message, fix or FIXES.get(name, FIXES["section"]))

    def check(self, passed, name, ok_message, fail_message, fix=None):
        return self.ok(name, ok_message) if passed else self.fail(name, fail_message, fix)

    @property
    def failed(self):
        return any(f["level"] == "FAIL" for f in self.findings)

    def render(self):
        return "\n".join(f"{f['level']} {f['name']}: {f['message']}"
                         + (f"\n  fix: {f['fix']}" if f["level"] == "FAIL" else "")
                         for f in self.findings)


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError) as exc:
        raise MindprintError(f"{path}: cannot read file ({exc})") from exc


def write_text(path, text):
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    except OSError as exc:
        raise MindprintError(f"{path}: cannot write file ({exc})") from exc


def load_json(path):
    try:
        return json.loads(read_text(path))
    except json.JSONDecodeError as exc:
        raise MindprintError(f"{path}:{exc.lineno}: invalid JSON ({exc.msg})") from exc


def resolve_out(path):
    if not Path(path).is_dir():
        raise MindprintError(f"{path}: not a directory")
    return Path(path).resolve()


def numbered(text):
    """(line_no, line) pairs with fenced code blanked out, so line numbers stay true."""
    lines, fenced = [], False
    for no, line in enumerate(text.splitlines(), 1):
        fence = line.lstrip().startswith("```")
        fenced = fenced != fence
        lines.append((no, "" if fenced or fence else line))
    return lines


def relative(out, path):
    return path.relative_to(out).as_posix()


def parse_frontmatter(lines):
    """(dict or None, index of first body line). Flat keys plus one nested level."""
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if not lines or lines[0].strip() != "---" or end is None:
        return None, 0
    data, parent = {}, None
    for match in filter(None, (re.match(r"^(\s*)([A-Za-z_][\w-]*):\s*(.*?)\s*$", raw)
                               for raw in lines[1:end])):
        indent, key, value = match.groups()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
            value = value[1:-1].replace('\\"', '"')
        if indent and isinstance(data.get(parent), dict):
            data[parent][key] = value
        else:
            data[key], parent = (value, None) if value else ({}, key)
    return data, end + 1


def skill_meta(out):
    """(frontmatter dict, tier) of out/SKILL.md; tier falls back to standard."""
    path = out / "SKILL.md"
    fm = (parse_frontmatter(read_text(path).splitlines())[0] if path.is_file() else None) or {}
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    return fm, meta.get("tier") if meta.get("tier") in TIERS else "standard"


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool)
