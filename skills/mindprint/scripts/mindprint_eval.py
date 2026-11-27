"""mindprint blind and unblind: two-arm blind validation packets, key and results."""
from __future__ import annotations

import datetime
import json
import random
import re
import string
from pathlib import Path

from mindprint_common import (DAY_RE, MindprintError, QID_RE, is_number, load_json, read_text,
                              resolve_out, skill_meta, write_text)


def parse_day(value):
    try:
        return datetime.date.fromisoformat(value).isoformat()
    except ValueError as exc:
        raise MindprintError(f"--date '{value}' must be YYYY-MM-DD") from exc


def load_key(path):
    key = load_json(path) if path.is_file() else {}
    if not isinstance(key, dict):
        raise MindprintError(f"{path}: must be a JSON object")
    return key


def parse_arms(specs):
    arms = {}
    for spec in specs or []:
        name, sep, file = spec.partition("=")
        if not sep or not QID_RE.fullmatch(name) or not file or name in arms:
            raise MindprintError(f"--arm '{spec}' must be name=<file> with a unique name")
        arms[name] = read_text(file)
    return list(arms.items())


META_RE = re.compile(r"\b(using|without) the skill\b|\bas an ai\b"
                     r"|\bi don['’]t have access to\b", re.I)
META_MAX_WORDS = 15
CASE_ID_RE = re.compile(r"\bC\d+\b(\s*·)?\s*")


def is_meta_line(line):
    bare = re.sub(r"^\s*(?:[-*+>]\s*|\d+[.)]\s*)*", "", line)
    match = META_RE.search(bare)
    return bare.casefold().startswith("arm:") or bool(match) and (
        match.start() == 0 or len(bare.split()) <= META_MAX_WORDS)


def scrub_answer(text, skill_name):
    """Blind one answer; return (text, lines dropped, inline edits).

    A line is dropped only when it is purely meta: it starts with "Arm:" or with a META_RE
    phrase, or contains one and has at most META_MAX_WORDS words. Case ids (C05, "C05 ·")
    are deleted inline, and the skill name and its slug become "the person's". Arm names
    are left alone.
    """
    names = [n for n in (skill_name, re.sub(r"-(mind|field)$", "", skill_name)) if n]
    name_re = re.compile("|".join(r"(?<![\w-])%s(?![\w-])" % re.escape(n) for n in names), re.I)
    kept, dropped, edits = [], 0, 0
    for line in text.splitlines():
        if is_meta_line(line):
            dropped += 1
            continue
        new = CASE_ID_RE.sub("", line)
        new = name_re.sub("the person's", new) if names else new
        new = re.sub(r"\(\s*\)", "", new)
        new = re.sub(r"\s+([,.;:!?)])", r"\1", re.sub(r"(?<=\S)[ \t]{2,}", " ", new)).rstrip()
        edits += new != line.rstrip()
        kept.append(new)
    return "\n".join(kept) + "\n", dropped, edits


def cmd_blind(args, rep):
    out = resolve_out(args.out)
    if args.question == "max":
        raise MindprintError("--question 'max' is reserved (grades.json uses it for the scale)")
    if not QID_RE.fullmatch(args.question):
        raise MindprintError(f"--question '{args.question}' must be letters, digits, - or _")
    arms = parse_arms(args.arm)
    if len(arms) < 2:
        return rep.fail("blind", f"{len(arms)} arm(s), need >= 2",
                        "pass --arm skill=… --arm baseline=…")
    date = parse_day(args.date) if args.date else datetime.date.today().isoformat()
    vdir = out / "references/validation" / date
    key = load_key(vdir / "key.json")
    if args.question in key or (vdir / args.question).exists():
        return rep.fail("blind", f"{args.question} is already blinded for {date}", "use a new id")
    skill_name = str(skill_meta(out)[0].get("name", ""))
    random.Random(args.seed).shuffle(arms)
    mapping, dropped, edits = {}, 0, 0
    for letter, (arm, text) in zip(string.ascii_uppercase, arms):
        scrubbed, lines_dropped, lines_edited = scrub_answer(text, skill_name)
        write_text(vdir / args.question / f"{letter}.md", scrubbed)
        mapping[letter], dropped, edits = arm, dropped + lines_dropped, edits + lines_edited
    key[args.question] = mapping
    write_text(vdir / "key.json", json.dumps(key, indent=2, sort_keys=True) + "\n")
    rep.ok("blind", f"wrote {len(arms)} answers to references/validation/{date}/{args.question}/ "
           f"({dropped} meta lines dropped, {edits} lines scrubbed); mapping appended to key.json")


def parse_grades(path, key, rep):
    """Map {"Q1": {"A": 7}} through key.json to {"Q1": {"skill": 7}}; return (max, scores)."""
    grades = load_json(path)
    if not isinstance(grades, dict) or not all(
            isinstance(v, dict) for q, v in grades.items() if q != "max"):
        raise MindprintError(f'{path}: must look like {{"Q1": {{"A": 7, "B": 5}}, "max": 10}}')
    max_score = grades.get("max", 10)
    if not is_number(max_score) or max_score <= 0:
        rep.fail("grades", f"max {max_score!r} must be a positive number")
        max_score = 10
    scores = {q: {} for q in grades if q != "max"}
    for question, letter, score in ((q, a, v) for q in scores for a, v in grades[q].items()):
        mapping = key.get(question, {})
        if letter not in mapping:
            rep.fail("grades", f"{question}.{letter} is not in key.json")
        elif not is_number(score) or not 0 <= score <= max_score:
            rep.fail("grades", f"{question}.{letter}: score {score!r} must be 0-{max_score}")
        else:
            scores[question][mapping[letter]] = score
    for question in (q for q in key if q not in grades):
        rep.warn("grades", f"{question} has no grades")
    for question in (q for q in scores if q in key):
        for letter in (m for m in key[question] if m not in grades[question]):
            rep.warn("grades", f"{question}.{letter} has no grade; shown as — and left out "
                     "of that arm's total")
    return max_score, scores


TIE_EPSILON = 1e-9


def tie_flag(question, row):
    """Holdout (H*) questions tie within 2 points; others only on equal scores."""
    top, holdout = sorted(row.values(), reverse=True)[:2], question.startswith("H")
    if len(top) < 2 or top[0] - top[1] > (2 if holdout else 0) + TIE_EPSILON:
        return ""
    return "tie (within 2 points)" if holdout else "tie"


def fmt(value):
    return str(int(value)) if float(value).is_integer() else f"{value:g}"


def results_markdown(date, max_score, scores, rep):
    arms = sorted(dict.fromkeys(a for row in scores.values() for a in row),
                  key=lambda arm: arm != "skill")
    totals = {arm: sum(row.get(arm, 0) for row in scores.values()) for arm in arms}
    lines = [f"# Blind validation results · {date}", "",
             f"Scores out of {fmt(max_score)} per question.", "",
             "| Question | " + " | ".join(arms) + " | Flag |", "|---" * (len(arms) + 2) + "|"]
    for question in sorted(scores, key=lambda q: [int(p) if p.isdigit() else p
                                                  for p in re.split(r"(\d+)", q)]):
        row, flag = scores[question], tie_flag(question, scores[question])
        if flag:
            rep.warn("tie", f"{question}: {flag}")
        cells = [fmt(row[arm]) if arm in row else "—" for arm in arms]
        lines.append(f"| {question} | " + " | ".join(cells) + f" | {flag} |")
    lines.append("| **Total** | " + " | ".join(f"**{fmt(totals[a])}**" for a in arms) + " | |")
    return "\n".join(lines) + "\n"


def latest_date(out):
    vdir = out / "references/validation"
    days = vdir.iterdir() if vdir.is_dir() else []
    dates = sorted(d.name for d in days if DAY_RE.fullmatch(d.name) and (d / "key.json").is_file())
    if not dates:
        raise MindprintError(f"{vdir}: no <date>/key.json found; run blind first or pass --date")
    return dates[-1]


def cmd_unblind(args, rep):
    out = resolve_out(args.out)
    date = parse_day(args.date) if args.date else latest_date(out)
    key_path = out / "references/validation" / date / "key.json"
    key = load_key(key_path)
    if not key:
        return rep.fail("unblind", f"references/validation/{date}/key.json is missing or empty",
                        "run blind first, or pass the right --date")
    max_score, scores = parse_grades(Path(args.grades), key, rep)
    if rep.failed:
        return None
    markdown = results_markdown(date, max_score, scores, rep)
    write_text(key_path.parent / "results.md", markdown)
    rep.ok("unblind", f"wrote references/validation/{date}/results.md")
    return markdown
