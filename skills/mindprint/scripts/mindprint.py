#!/usr/bin/env python3
"""mindprint CLI: scaffold, gate and verify a perspective skill (contract: docs/SPEC.md).

  mindprint.py init <out-dir> --name "Full Name" [--tier standard] [--topic]
  mindprint.py status <out> [--allow-low-primary REASON]   research gate
  mindprint.py check <out> [--strict]   output skill rules, then quotes
  mindprint.py quotes <out> [--strict]  every cited quote against its archived source
  mindprint.py blind <out> --question Q1 --arm skill=a.md --arm baseline=b.md [--seed N] [--date D]
  mindprint.py unblind <out> --grades grades.json [--date YYYY-MM-DD]

Findings print as "PASS|WARN|FAIL name: message", a "fix:" line under each FAIL (--json for
JSON); exit 1 on any FAIL. Shared helpers live in mindprint_common.py, init in
mindprint_scaffold.py, blind/unblind in mindprint_eval.py (scrubbing rules: scrub_answer).
"""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mindprint_common import (ABS_RE, ATTRIB_RE, BOUNDARY_LABELS, BQ_RE, CARD_FIELDS, CARD_RE,
                              CASEBOOK, DATE_RE, DAY_RE, DIFF_RE, FIXES, HOLDOUT, HOLDOUT_FIELDS,
                              HOLD_RE, ID_RE, INDEX_RE, INLINE_RE, LEAK_TARGETS, LEDGER,
                              LEDGER_FIELDS, LIST_RE, MIN_CARDS, MindprintError, NAME_RE, PRIOR,
                              PUNCT_MAP, QUICK_REQUIRED, REQUIRED_FILES, Report, SKILL_HEADINGS,
                              SKILL_MAX_LINES, SOURCE_TIERS, TAG_RE, TIERS, TODO_MARK, TODO_RE,
                              TRACKS, TRACK_FILES, VERSION, VOICE, numbered, parse_frontmatter,
                              read_text, relative, resolve_out, skill_meta)  # noqa: E402
from mindprint_eval import cmd_blind, cmd_unblind  # noqa: E402
from mindprint_scaffold import cmd_init  # noqa: E402


def split_sections(body, prefix="## "):
    """[(heading, line_no, [(no, line)])] for each line starting with prefix."""
    sections = []
    for no, line in body:
        if line.startswith(prefix):
            sections.append((line.strip(), no, []))
        elif sections:
            sections[-1][2].append((no, line))
    return sections


def list_items(body):
    """Top-level list items as [no, text], with indented continuation lines joined in."""
    items, is_open = [], False
    for no, line in body:
        match = LIST_RE.match(line)
        if match:
            items.append([no, match.group(2)])
        elif is_open and line[:1] in (" ", "\t") and line.strip():
            items[-1][1] += " " + line.strip()
        is_open = bool(match) or (is_open and (not line.strip() or line[:1] in (" ", "\t")))
    return items


def strip_marker(line):
    return re.sub(r"^\s*(?:[-*+]\s+|>\s*)?", "", line).strip()


def tag_ids(text, first_only=False):
    matches = list(TAG_RE.finditer(text))[:1] if first_only else TAG_RE.finditer(text)
    return [part.strip() for m in matches for part in m.group(1).split(",")]


def word_count(text):
    return len(re.findall(r"[\w']+", TAG_RE.sub(" ", text)))


def normalise(text):
    """Casefold, unify quotes and dashes, drop punctuation but apostrophes, collapse space."""
    return " ".join(re.sub(r"[^\w\s']|_", " ", text.translate(PUNCT_MAP).casefold()).split())


def todo_lines(text):
    return [no for no, line in enumerate(text.splitlines(), 1) if TODO_RE.search(line)]


def parse_blocks(text, head_re, fields):
    """Casebook cards or holdout items: a heading, then 'Field: value' lines."""
    field_re = re.compile(r"^(%s):\s*(.*)$" % "|".join(map(re.escape, fields)))
    blocks, field = [], None
    for no, line in numbered(text):
        head, match = head_re.match(line), field_re.match(line)
        if head:
            blocks.append({"id": head.group(1), "no": no, "fields": {}})
            field = None
        elif blocks and match:
            field = match.group(1)
            blocks[-1]["fields"][field] = match.group(2).strip()
        elif line.startswith("#"):
            field = None
        elif blocks and field and line.strip():
            blocks[-1]["fields"][field] += " " + line.strip()
    return blocks


def validate_blocks(blocks, fields, tag_field, where, name, rep):
    """Unique ids, every field present, a tag on tag_field. Returns the id set."""
    ids = set()
    for block in blocks:
        at = f"{where}:{block['no']}: {block['id']}"
        if block["id"] in ids:
            rep.fail(name, f"{at} is a duplicate id")
        ids.add(block["id"])
        for field in (f for f in fields if not block["fields"].get(f)):
            rep.fail(name, f"{at} has no '{field}:' line")
        source = block["fields"].get(tag_field, "")
        if source and not TAG_RE.search(source):
            rep.fail(name, f"{at} {tag_field} has no [Sxx] tag")
    return ids


def md_files(out):
    """SKILL.md, FIDELITY.md and references/**/*.md except validation/ and sources/."""
    files = [p for p in (out / "SKILL.md", out / "FIDELITY.md") if p.is_file()]
    refs = out / "references"
    return files + ([p for p in sorted(refs.rglob("*.md"))
                     if p.relative_to(refs).parts[0] not in ("validation", "sources")]
                    if refs.is_dir() else [])


# Ledger
def load_ledger(out, rep):
    if not (out / LEDGER).is_file():
        rep.fail("ledger", f"{LEDGER} is missing", FIXES["files"])
        return {}
    ledger, bad = {}, 0
    for no, line in enumerate(read_text(out / LEDGER).splitlines(), 1):
        try:
            entry = json.loads(line) if line.strip() else None
        except json.JSONDecodeError as exc:
            entry, problems = None, [f"invalid JSON ({exc.msg})"]
        else:
            problems = ledger_problems(entry, out) if entry is not None else []
        sid = entry.get("id") if isinstance(entry, dict) else None
        if isinstance(sid, str) and sid in ledger:
            problems.append(f"duplicate id {sid}")
        elif isinstance(sid, str):
            ledger[sid] = entry
        for problem in problems:
            rep.fail("ledger", f"{LEDGER}:{no}: {problem}")
        bad += bool(problems)
    if not bad:
        rep.ok("ledger", f"{len(ledger)} sources, all entries valid")
    return ledger


def ledger_problems(entry, out):
    if not isinstance(entry, dict):
        return ["entry is not a JSON object"]
    problems = [f"missing field '{f}'" if f not in entry else f"'{f}' must be a {kind.__name__}"
                for f, kind in LEDGER_FIELDS.items() if not isinstance(entry.get(f), kind)]
    if problems:
        return problems
    rules = [
        (ID_RE.fullmatch(entry["id"]), f"id '{entry['id']}' must be S plus 2-3 digits"),
        (entry["title"].strip(), "title is empty"),
        (DATE_RE.fullmatch(entry["date"]), f"date '{entry['date']}' must be YYYY[-MM[-DD]] or ''"),
        (entry["track"] in TRACKS, f"track '{entry['track']}' must be one of {', '.join(TRACKS)}"),
        (entry["tier"] in SOURCE_TIERS, f"tier '{entry['tier']}' must be {'/'.join(SOURCE_TIERS)}"),
    ]
    archive = entry["archive"]
    rules += [(not archive or not (Path(archive).is_absolute() or ABS_RE.search(archive)
                                   or ".." in Path(archive).parts),
               f"archive '{archive}' must be a path inside references/, e.g. sources/S01.txt")]
    problems = [message for passed, message in rules if not passed]
    if archive and not problems and not (out / "references" / archive).is_file():
        problems.append(f"archive file references/{archive} does not exist")
    return problems


# Quotes
CURLY_RE = re.compile(r"“([^”]+)”")
FRAMING_WORDS = 6  # a blockquote span may carry up to this many framing words ("He said")


def group_blockquotes(lines):
    """Contiguous '>' passages: {no, lines, after}, where after is the following line."""
    groups, current = [], None
    for no, line in lines:
        if BQ_RE.match(line):
            if current is None:
                current = {"no": no, "lines": [], "after": ""}
                groups.append(current)
            current["lines"].append(BQ_RE.sub("", line, count=1))
        elif current is not None:
            current["after"], current = line, None
    return groups


def passage_ids(group):
    return tag_ids("\n".join(group["lines"])) or tag_ids(group["after"], first_only=True)


def blockquote_quote(group):
    """The whole passage (minus attribution lines) is the quote; inner quoted spans are kept
    so a passage that is only framing around a real span can WARN instead of FAIL."""
    text = " ".join(line for line in group["lines"] if not ATTRIB_RE.match(line))
    spans = [m.group(1) or m.group(2) for m in INLINE_RE.finditer(text)]
    return {"no": group["no"], "text": text, "ids": passage_ids(group),
            "spans": [s for s in spans if word_count(s) >= 6]}


def paragraphs(lines):
    """Runs of prose lines; blank lines, headings and blockquotes end a run, a list item
    starts a new one."""
    runs, current = [], []
    for no, line in lines:
        ends = not line.strip() or line.startswith("#") or BQ_RE.match(line)
        if ends or LIST_RE.match(line):
            runs += [current] if current else []
            current = [] if ends else [(no, line)]
        else:
            current.append((no, line))
    return runs + ([current] if current else [])


def paragraph_quotes(run):
    """(quotes, unparsed) for one paragraph. A quote may wrap across lines; its tag must
    follow on the line of the closing quote or the next line. With an odd number of straight
    quotes in a cited paragraph, only curly quotes are parsed and unparsed is True."""
    starts, text = [], ""
    for _, line in run:
        starts.append(len(text))
        text += line + "\n"
    unparsed = bool(TAG_RE.search(text)) and text.count('"') % 2 == 1
    quotes = []
    for match in (CURLY_RE if unparsed else INLINE_RE).finditer(text):
        body = " ".join((match.group(1) or match.group(match.lastindex)).split())
        end_line = bisect.bisect_right(starts, match.end() - 1) - 1
        limit = starts[end_line + 2] if end_line + 2 < len(starts) else len(text)
        ids = tag_ids(text[match.end():limit], first_only=True)
        if ids and word_count(body) >= 6:
            line_no = run[bisect.bisect_right(starts, match.start()) - 1][0]
            quotes.append({"no": line_no, "text": body, "ids": ids, "spans": []})
    return quotes, unparsed


def find_quotes(lines):
    """(quotes, unparsed paragraph line numbers): cited blockquotes, and >= 6-word
    double-quoted text followed by a citation tag."""
    quotes = [blockquote_quote(g) for g in group_blockquotes(lines) if passage_ids(g)]
    unparsed = []
    for run in paragraphs(lines):
        found, odd = paragraph_quotes(run)
        quotes += found
        unparsed += [run[0][0]] if odd else []
    return sorted(quotes, key=lambda q: q["no"]), unparsed


def quote_fragments(text):
    text = re.sub(r"\[[^\]]*\]", " ", TAG_RE.sub(" ", text))
    return [frag for frag in (normalise(p) for p in re.split(r"\.\.\.|…", text)) if frag]


def fragments_in_order(fragments, source):
    haystack, pos = f" {source} ", 0
    for frag in fragments:
        found = haystack.find(f" {frag} ", pos)
        if found < 0:
            return False
        pos = found + len(frag) + 1
    return True


def verify_quote(out, ledger, quote, where, strict, cache, rep):
    short = " ".join(TAG_RE.sub("", quote["text"]).split())
    where = f"{where}: \"{short[:60]}{'…' if len(short) > 60 else ''}\""
    unknown = [sid for sid in quote["ids"] if sid not in ledger]
    if unknown:
        return rep.fail("quote", f"{where} cites unknown source {', '.join(unknown)}",
                        FIXES["tags"])
    archives = [ledger[sid]["archive"] for sid in quote["ids"] if ledger[sid].get("archive")]
    if not archives:
        message = f"{where} cites {', '.join(quote['ids'])}, which has no archive"
        fix = "save the source text under references/sources/ and set its archive field"
        return rep.fail("quote", message, fix) if strict else rep.warn("quote", message)
    sources = []
    for archive in archives:
        if archive not in cache:
            cache[archive] = normalise(read_text(out / "references" / archive))
        sources.append((archive, cache[archive]))
    match_quote(quote, where, sources, rep)


def match_quote(quote, where, sources, rep):
    fragments = quote_fragments(quote["text"])
    if not fragments:
        return rep.fail("quote", f"{where} has no checkable words once tags, [editorial "
                        "insertions] and ... are removed", "quote the source's actual words")
    hit = next((name for name, text in sources if fragments_in_order(fragments, text)), None)
    if hit:
        return rep.ok("quote", f"{where} found in {hit}")
    spans_found = quote["spans"] and all(
        any(fragments_in_order(quote_fragments(span), text) for _, text in sources)
        for span in quote["spans"])
    framing = quote["text"]
    for span in quote["spans"]:
        framing = framing.replace(span, " ")
    if spans_found and word_count(re.sub(r"\[[^\]]*\]", " ", framing)) <= FRAMING_WORDS:
        return rep.warn("quote-framing", f"{where}: the quoted span is in the source; the "
                        f"framing words around it are not")
    rep.fail("quote", f"{where} not found in {', '.join(name for name, _ in sources)}")


def run_quotes(out, ledger, strict, rep):
    cache, count = {}, 0
    for path in md_files(out):
        quotes, unparsed = find_quotes(numbered(read_text(path)))
        for no in unparsed:
            rep.warn("quote-unparsed", f"{relative(out, path)}:{no}: cited paragraph has an odd "
                     "number of straight double quotes; use curly quotes or fix the pairing")
        for quote in quotes:
            count += 1
            where = f"{relative(out, path)}:{quote['no']}"
            verify_quote(out, ledger, quote, where, strict, cache, rep)
    if not count:
        rep.warn("quotes", "no cited quotes found")


def cmd_quotes(args, rep):
    out = resolve_out(args.out)
    run_quotes(out, load_ledger(out, rep), args.strict, rep)


# Status
def status_sources(ledger, tier, rep, allow_low_primary=None):
    if not ledger:
        return rep.fail("sources", "the ledger has no sources")
    counts = {t: sum(1 for e in ledger.values() if e.get("track") == t) for t in TRACKS}
    rep.ok("tracks", ", ".join(f"{t} {n}" for t, n in counts.items()))
    primary = sum(1 for e in ledger.values() if e.get("tier") == "primary")
    share = f"{primary}/{len(ledger)} primary ({primary / len(ledger):.0%})"
    reason = (allow_low_primary or "").strip()
    if primary * 2 < len(ledger) and reason:
        rep.warn("primary-share", f"{share}, below 50%; allowed: {reason}")
    else:
        rep.check(primary * 2 >= len(ledger), "primary-share", share, f"{share}, need >= 50%")
    critical = sum(1 for e in ledger.values() if e.get("critical") is True)
    need = 1 if tier == "quick" else 2
    rep.check(critical >= need, "critics", f"{critical} critical sources",
              f"{critical} critical sources, {tier} tier needs >= {need}")


def research_items(out, path, rep):
    """Validate one track file; return its count of valid 'Differs from prior' items."""
    name, text = relative(out, path), read_text(path)
    if todo_lines(text):
        rep.fail("research", f"{name}:{todo_lines(text)[0]}: still has placeholder markers",
                 "replace the placeholder lines with findings and [Sxx] tags")
    sections = split_sections(numbered(text))
    if not sections or sections[-1][0] != "## Differs from prior":
        rep.fail("research", f"{name}: does not end with '## Differs from prior'")
        return 0
    items = list_items(sections[-1][2])
    for no, _ in (item for item in items if not DIFF_RE.match(item[1])):
        rep.fail("research", f"{name}:{no}: item must start with [overturn], [deepen] or [new]",
                 "start the item with [overturn], [deepen] or [new]")
    return sum(1 for _, text in items if DIFF_RE.match(text))


def status_research(out, tier, rep):
    required, total = QUICK_REQUIRED if tier == "quick" else TRACKS, 0
    for track in TRACKS:
        path = out / "references/research" / TRACK_FILES[track]
        if path.is_file():
            total += research_items(out, path, rep)
        elif track in required:
            rep.fail("research", f"{relative(out, path)} is missing ({tier} tier needs {track})",
                     "write the track file (init scaffolds it)")
    need = 5 if tier == "quick" else 8
    rep.check(total >= need, "differs-from-prior", f"{total} items",
              f"{total} items, {tier} tier needs >= {need}")


def holdout_unsealed(text):
    """True while holdout.md is still init's placeholder: markers and no filled-in field."""
    values = [v for item in parse_blocks(text, HOLD_RE, HOLDOUT_FIELDS)
              for v in item["fields"].values()]
    return bool(TODO_RE.search(text)) and all(TODO_RE.search(v) for v in values)


def status_holdout(out, ledger, rep, sealed=False):
    """sealed=True (check) fails on init's placeholder; status only WARNs on it."""
    if len(ledger) < 10:
        return rep.warn("holdout", f"no holdout test: ledger has {len(ledger)} sources (< 10)")
    if not (out / HOLDOUT).is_file():
        return rep.fail("holdout", f"{HOLDOUT} is missing")
    text = read_text(out / HOLDOUT)
    if not sealed and holdout_unsealed(text):
        return rep.warn("holdout", f"{HOLDOUT}: not sealed yet (still the init placeholder); "
                        "seal it in step 3")
    if todo_lines(text):
        rep.fail("holdout", f"{HOLDOUT}:{todo_lines(text)[0]}: still has placeholder markers",
                 "finish every item and remove the TODO markers")
    for no, line in numbered(text):
        if re.match(r"##\s*H\d", line) and not HOLD_RE.match(line):
            rep.fail("holdout", f"{HOLDOUT}:{no}: malformed holdout heading '{line.strip()}'")
    items = parse_blocks(text, HOLD_RE, HOLDOUT_FIELDS)
    validate_blocks(items, HOLDOUT_FIELDS, "Source", HOLDOUT, "holdout", rep)
    rep.check(3 <= len(items) <= 5, "holdout", f"{len(items)} sealed items",
              f"{len(items)} items, need 3-5")


def status_prior(out, rep):
    if not (out / PRIOR).is_file():
        return rep.fail("prior", f"{PRIOR} is missing")
    text, todos = read_text(out / PRIOR), todo_lines(read_text(out / PRIOR))
    written = any(line.strip() and not line.startswith("#") for line in text.splitlines())
    rep.check(written and not todos, "prior", "00-prior.md written",
              f"{PRIOR}:{todos[0] if todos else 1}: still a placeholder")


def cmd_status(args, rep):
    out = resolve_out(args.out)
    ledger, tier = load_ledger(out, rep), skill_meta(out)[1]
    status_sources(ledger, tier, rep, args.allow_low_primary)
    status_research(out, tier, rep)
    status_holdout(out, ledger, rep)
    status_prior(out, rep)


# Check: SKILL.md
def check_frontmatter(fm, out, rep):
    if fm is None:
        return rep.fail("frontmatter", "SKILL.md:1: no '---' frontmatter block")
    name = fm.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name):
        rep.fail("frontmatter", f"SKILL.md: name '{name}' must be <slug>-mind or <slug>-field")
    elif name != out.name:
        rep.warn("frontmatter", f"SKILL.md: name '{name}' differs from folder '{out.name}'")
    check_description(fm.get("description"), rep)
    meta = fm.get("metadata") if isinstance(fm.get("metadata"), dict) else {}
    rules = (("mindprint", meta.get("mindprint") == VERSION, f'"{VERSION}"'),
             ("researched", DAY_RE.fullmatch(str(meta.get("researched"))), "YYYY-MM-DD"),
             ("tier", meta.get("tier") in TIERS, " | ".join(TIERS)))
    for key, valid, rule in rules:
        if not valid:
            rep.fail("frontmatter", f"SKILL.md: metadata.{key} must be {rule}")


def check_description(desc, rep):
    if not isinstance(desc, str) or not desc.strip() or desc in (">", "|", ">-", "|-"):
        return rep.fail("description", "SKILL.md: description must be a one-line string")
    if len(desc) > 1024:
        rep.fail("description", f"SKILL.md: description is {len(desc)} chars (max 1024)")
    elif len(desc) > 400:
        rep.warn("description", f"SKILL.md: description is {len(desc)} chars (400 recommended)")
    rep.check("Do not trigger on general questions" in desc, "description", f"{len(desc)} chars",
              "SKILL.md: description lacks 'Do not trigger on general questions'")


def check_heading_order(sections, rep):
    found = [heading for heading, _, _ in sections]
    present = [h for h in found if h in SKILL_HEADINGS]
    missing = [h for h in SKILL_HEADINGS if h not in found]
    for heading in missing:
        rep.fail("headings", f"SKILL.md: missing '{heading}'")
    ordered = present == [h for h in SKILL_HEADINGS if h in present]
    rep.check(ordered, "headings", "all required headings in order",
              "SKILL.md: required headings are out of order or repeated")


def check_disclaimer(sec, ctx, rep):
    found = [(no, strip_marker(line)) for no, line in sec[1]
             if strip_marker(line).startswith("**Disclaimer:**")]
    if not found:
        return rep.fail("disclaimer", f"SKILL.md:{sec[0]}: no line starting '**Disclaimer:**'")
    no, line = found[0]
    rep.check("public record" in line.casefold() and re.search(r"\b\d{4}\b", line), "disclaimer",
              "present", f"SKILL.md:{no}: disclaimer must name the public record and the "
              "research cutoff date")


def check_subsections(sec, label, bounds, prefixes, rep):
    subs, (low, high) = split_sections(sec[1], "### "), bounds
    if not low <= len(subs) <= high:
        rep.fail(label, f"SKILL.md:{sec[0]}: {len(subs)} '### ' subsections, need {low}-{high}")
    for title, no, body in subs:
        lines = [strip_marker(line) for _, line in body]
        for prefix in (p for p in prefixes if not any(line.startswith(p) for line in lines)):
            rep.fail(label, f"SKILL.md:{no}: '{title[4:]}' has no line starting '{prefix}'")
        if not TAG_RE.search(title + "\n".join(lines)):
            rep.fail(label, f"SKILL.md:{no}: '{title[4:]}' has no [Sxx] tag")


def check_list(sec, label, bounds, need_tag, rep):
    items, (low, high) = list_items(sec[1]), bounds
    if len(items) < low or (high and len(items) > high):
        need = f"{low}-{high}" if high else f">= {low}"
        rep.fail(label, f"SKILL.md:{sec[0]}: {len(items)} list items, need {need}")
    for no, _ in (i for i in items if need_tag and not TAG_RE.search(i[1])):
        rep.fail(label, f"SKILL.md:{no}: list item has no [Sxx] tag")


def check_contains(sec, label, needles, rep):
    text = "\n".join(line for _, line in sec[1])
    for needle in (n for n in needles if n not in text):
        rep.fail(label, f"SKILL.md:{sec[0]}: missing {needle}")
    return text


def check_voice(sec, ctx, rep):
    cited = [g for g in group_blockquotes(sec[1]) if passage_ids(g)]
    if len(cited) < 2:
        rep.fail("voice", f"SKILL.md:{sec[0]}: {len(cited)} cited blockquotes, need >= 2")
    check_contains(sec, "voice", ["references/voice.md"], rep)


def check_case_index(sec, ctx, rep):
    ids = [m.group(1) for _, line in sec[1] for m in [INDEX_RE.search(line)] if m]
    needles = ["references/casebook.md"] + ([] if ids else ["'C01 · title' lines"])
    check_contains(sec, "casebook-index", needles, rep)
    for case_id in (i for i in ids if i not in ctx["cards"]):
        rep.fail("casebook-index", f"SKILL.md: {case_id} is not a card in casebook.md")
    for case_id in sorted(set(ctx["cards"]) - set(ids)):
        rep.warn("casebook-index", f"SKILL.md: card {case_id} is not in the index")


def check_sources_section(sec, ctx, rep):
    text = check_contains(sec, "sources-section", ["references/sources.jsonl"], rep)
    for tier in ("primary", "secondary"):
        actual = sum(1 for e in ctx["ledger"].values() if e.get("tier") == tier)
        match = re.search(rf"(\d+)\s+{tier}", text, re.I)
        if not match or int(match.group(1)) != actual:
            rep.fail("sources-section", f"SKILL.md:{sec[0]}: needs the ledger's {tier} count",
                     f"state it as '{actual} {tier}'")

SECTION_CHECKS = {
    "## How to use me": check_disclaimer,
    "## Moves": lambda s, c, r: check_subsections(s, "moves", (5, 8), ("When:",), r),
    "## Mental models": lambda s, c, r: check_subsections(
        s, "mental-models", (3, 7), ("Evidence:", "Breaks when:"), r),
    "## Heuristics": lambda s, c, r: check_list(s, "heuristics", (5, 10), True, r),
    "## Common misreadings": lambda s, c, r: check_list(s, "misreadings", (2, 0), True, r),
    "## Voice": check_voice,
    "## Casebook index": check_case_index,
    "## Tensions": lambda s, c, r: check_list(s, "tensions", (2, 0), False, r),
    "## Boundaries": lambda s, c, r: check_contains(s, "boundaries", BOUNDARY_LABELS, r),
    "## Sources": check_sources_section,
}


def check_skill(out, ctx, rep):
    if not (out / "SKILL.md").is_file():
        return
    text = read_text(out / "SKILL.md")
    lines = text.splitlines()
    rep.check(len(lines) <= SKILL_MAX_LINES, "length", f"SKILL.md {len(lines)} lines",
              f"SKILL.md: {len(lines)} lines (max {SKILL_MAX_LINES})")
    fm, start = parse_frontmatter(lines)
    check_frontmatter(fm, out, rep)
    sections = split_sections(numbered(text)[start:])
    check_heading_order(sections, rep)
    found = {heading: (no, body) for heading, no, body in sections}
    for heading in (h for h in SECTION_CHECKS if h in found):
        SECTION_CHECKS[heading](found[heading], ctx, rep)


# Check: other files
def check_casebook(out, tier, rep):
    if not (out / CASEBOOK).is_file():
        return set()
    cards = parse_blocks(read_text(out / CASEBOOK), CARD_RE, CARD_FIELDS)
    ids = validate_blocks(cards, CARD_FIELDS, "Sources", CASEBOOK, "casebook", rep)
    need = MIN_CARDS[tier]
    rep.check(len(ids) >= need, "casebook", f"{len(ids)} cards ({tier} needs {need})",
              f"{len(ids)} cards, {tier} tier needs >= {need}")
    return ids


def check_tags(out, ledger, rep):
    bad = total = 0
    for path in md_files(out):
        for no, line in numbered(read_text(path)):
            for sid in tag_ids(line):
                total += 1
                if sid not in ledger:
                    bad += 1
                    known = ID_RE.fullmatch(sid)
                    problem = "unknown source" if known else "malformed (S + 2-3 digits)"
                    rep.fail("tags", f"{relative(out, path)}:{no}: tag {sid} is {problem}")
    if not bad:
        rep.ok("tags", f"{total} citation tags resolve")


def has_absolute_path(line):
    """ABS_RE hits, except inside a URL token (one whose text before the hit contains ://)."""
    return any("://" not in re.split(r"[\s<>()\[\]\"'`]", line[:m.start()])[-1]
               for m in ABS_RE.finditer(line))


def check_text_rules(out, rep):
    clean = {"paths": True, "placeholders": True}
    for path in md_files(out) + [p for p in [out / LEDGER] if p.is_file()]:
        lines = list(enumerate(read_text(path).splitlines(), 1))
        for name, test, what in (("paths", has_absolute_path, "absolute path"),
                                 ("placeholders", TODO_RE.search, "TODO/placeholder marker")):
            hits = [no for no, line in lines if test(line)]
            if hits:
                clean[name] = False
                rep.fail(name, f"{relative(out, path)}:{hits[0]}: {what} ({len(hits)} lines)")
    for name in (n for n, ok in clean.items() if ok):
        rep.ok(name, f"no {'absolute paths' if name == 'paths' else 'TODO or placeholder markers'}")


ANGLE_RE = re.compile(r"<([^\s<>][^<>\n]*)>")
HTML_TAG_RE = re.compile(r"/?(br|sub|sup|details|summary|kbd|img|a|p|div|span)\b[^<>]*/?", re.I)
PLACEHOLDER_FILES = ("SKILL.md", CASEBOOK, VOICE, "FIDELITY.md")


def angle_placeholders(text):
    """(line_no, token) for <Name>-style template tokens outside code, comments and HTML tags."""
    text = re.sub(r"<!--.*?-->", lambda m: "\n" * m.group().count("\n"), text, flags=re.S)
    hits = []
    for no, line in numbered(text):
        for match in ANGLE_RE.finditer(re.sub(r"`[^`\n]*`", "", line)):
            token = match.group(1)
            if not HTML_TAG_RE.fullmatch(token) and not re.match(r"(https?|mailto):", token):
                hits.append((no, match.group()))
    return hits


def check_angle_placeholders(out, rep):
    clean = True
    for name in (n for n in PLACEHOLDER_FILES if (out / n).is_file()):
        hits = angle_placeholders(read_text(out / name))
        if hits:
            clean = False
            rep.fail("placeholders", f"{name}:{hits[0][0]}: template placeholder {hits[0][1]} "
                     f"({len(hits)} found)")
    if clean:
        rep.ok("placeholders", "no <angle-bracket> template placeholders")


def first_shingle(words, haystack, size=8):
    shingles = (" ".join(words[i:i + size]) for i in range(len(words) - size + 1))
    return next((s for s in shingles if f" {s} " in haystack), "")


def check_holdout_leak(out, rep):
    if not (out / HOLDOUT).is_file():
        return rep.warn("holdout-leak", f"no {HOLDOUT}; leak check skipped")
    targets = {name: f" {normalise(read_text(out / name))} "
               for name in LEAK_TARGETS if (out / name).is_file()}
    leaks, items = 0, parse_blocks(read_text(out / HOLDOUT), HOLD_RE, HOLDOUT_FIELDS)
    if not items:
        return rep.warn("holdout-leak", f"no '## H1 · title' items parsed in {HOLDOUT}; "
                        "leak check skipped")
    for item in items:
        words = normalise(item["fields"].get("What happened", "")).split()
        for name, hit in ((n, first_shingle(words, h)) for n, h in targets.items()):
            if hit:
                leaks += 1
                rep.fail("holdout-leak",
                         f"{item['id']} 'What happened' leaks into {name}: \"{hit}\"")
    if not leaks:
        rep.ok("holdout-leak", "no holdout text in SKILL.md, casebook.md or voice.md")


def cmd_check(args, rep):
    out = resolve_out(args.out)
    for name in (n for n in REQUIRED_FILES if not (out / n).is_file()):
        rep.fail("files", f"{name} is missing")
    ledger = load_ledger(out, rep)
    if not ledger:
        rep.fail("sources", "the ledger has no sources")
    cards = check_casebook(out, skill_meta(out)[1], rep)
    check_skill(out, {"ledger": ledger, "cards": cards}, rep)
    check_tags(out, ledger, rep)
    status_holdout(out, ledger, rep, sealed=True)
    check_text_rules(out, rep)
    check_angle_placeholders(out, rep)
    check_holdout_leak(out, rep)
    run_quotes(out, ledger, args.strict, rep)


# Entry point
def build_parser():
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--json", action="store_true", help="print findings as JSON")
    parser = argparse.ArgumentParser(prog="mindprint.py", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    options = {
        "init": [("--name", {"required": True}),
                 ("--tier", {"choices": TIERS, "default": "standard"}),
                 ("--topic", {"action": "store_true", "help": "a field: <slug>-field"})],
        "status": [("--allow-low-primary", {"metavar": "REASON",
                                            "help": "WARN, not FAIL, on primary share < 50%%"})],
        "check": [("--strict", {"action": "store_true", "help": "unarchived quotes FAIL"})],
        "quotes": [("--strict", {"action": "store_true", "help": "unarchived quotes FAIL"})],
        "blind": [("--question", {"required": True}), ("--seed", {"type": int}), ("--date", {}),
                  ("--arm", {"action": "append", "help": "name=<answer file>, repeatable"})],
        "unblind": [("--grades", {"required": True}), ("--date", {"help": "YYYY-MM-DD"})],
    }
    for name, flags in options.items():
        command = sub.add_parser(name, parents=[common], help=f"see '{name}' in docs/SPEC.md")
        command.add_argument("out")
        command.set_defaults(func=globals()[f"cmd_{name}"])
        for flag, kwargs in flags:
            command.add_argument(flag, **kwargs)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    rep, extra = Report(), None
    try:
        extra = args.func(args, rep)
    except MindprintError as exc:
        rep.fail("error", str(exc))
    payload = {"command": args.command, "ok": not rep.failed, "findings": rep.findings,
               **({"output": extra} if extra else {})}
    print(json.dumps(payload, indent=2, ensure_ascii=False) if args.json
          else (extra + "\n" if extra else "") + rep.render())
    return 1 if rep.failed else 0


if __name__ == "__main__":
    sys.exit(main())
