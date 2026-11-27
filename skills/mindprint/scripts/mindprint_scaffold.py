"""mindprint init: scaffold an output skill full of placeholders that check must FAIL."""
from __future__ import annotations

import datetime
import re
from pathlib import Path

from mindprint_common import (BOUNDARY_LABELS, CARD_FIELDS, CASEBOOK, HOLDOUT, HOLDOUT_FIELDS,
                              LEDGER, PRIOR, QUICK_TRACKS, SKILL_HEADINGS, TODO_MARK, TRACKS,
                              TRACK_FILES, VERSION, VOICE, write_text)


def scaffold(who, name, tier, today):
    todo = TODO_MARK + " TODO:"
    hints = {
        "## How to use me": f"**Disclaimer:** {todo} a model of {who}'s public record, not {who}; "
                            f"cutoff {today}.",
        "## Moves": f"### {todo} move\nWhen: {todo} the trigger [Sxx]",
        "## Mental models": f"### {todo} model\nEvidence: {todo} [Sxx]\nBreaks when: {todo}",
        "## Voice": f"> {todo} a passage in their words [Sxx]\n\nMore in references/voice.md.",
        "## Casebook index": f"- C01 · {todo} title\n\nFull cards: references/casebook.md.",
        "## Boundaries": "\n".join(f"- {label} {todo}" for label in BOUNDARY_LABELS),
        "## Sources": f"Ledger: references/sources.jsonl. {todo} <n> primary, <n> secondary.",
    }
    skill = (f"---\nname: {name}\ndescription: TODO what is distinctive about how {who} thinks. "
             f"Use when the user asks for {who}'s perspective, \"what would {who} do\", or to "
             f"switch to {who}. Do not trigger on general questions.\nmetadata:\n  mindprint: "
             f"\"{VERSION}\"\n  researched: \"{today}\"\n  tier: {tier}\n---\n\n# {who}\n"
             + "".join(f"\n{h}\n\n{hints.get(h, f'- {todo} [Sxx]')}\n" for h in SKILL_HEADINGS))
    files = {"SKILL.md": skill, LEDGER: "", "FIDELITY.md": f"# Fidelity\n\n{todo} blind results.\n",
             CASEBOOK: f"# Casebook\n\n## C01 · {todo} title\n"
                       + "".join(f"{field}: {todo}\n" for field in CARD_FIELDS),
             VOICE: f"# Voice\n\n{todo} quote library; cite each blockquote [Sxx].\n",
             PRIOR: f"# Prior\n\n{todo} before any research: what you believe about {who}, why.\n",
             HOLDOUT: f"# Holdout\n\n## H1 · {todo} title\n"
                      + "".join(f"{field}: {todo}\n" for field in HOLDOUT_FIELDS)}
    for track in QUICK_TRACKS if tier == "quick" else TRACKS:
        files[f"references/research/{TRACK_FILES[track]}"] = (
            f"# {track.capitalize()}\n\n{todo} findings [Sxx].\n\n## Differs from prior\n\n"
            f"- {todo} [new] what this track changed.\n")
    return files


def cmd_init(args, rep):
    out = Path(args.out)
    if out.exists() and (not out.is_dir() or any(out.iterdir())):
        return rep.fail("init", f"{out} exists and is not empty", "pick a new or empty directory")
    slug = re.sub(r"[^a-z0-9]+", "-", args.name.casefold()).strip("-")
    if not slug:
        return rep.fail("init", f"name '{args.name}' has no letters or digits", "pass a real name")
    name = f"{slug}-{'field' if args.topic else 'mind'}"
    files = scaffold(args.name, name, args.tier, datetime.date.today().isoformat())
    for path, body in files.items():
        write_text(out / path, body)
    (out / "references/sources").mkdir(parents=True, exist_ok=True)
    rep.ok("init", f"scaffolded {name} ({args.tier} tier, {len(files)} files) in {out}")
