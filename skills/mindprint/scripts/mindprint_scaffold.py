"""mindprint init: scaffold an output skill full of placeholders that check must FAIL."""
from __future__ import annotations

import datetime
import re
from pathlib import Path

from mindprint_common import (CARD_FIELDS, CASEBOOK, HOLDOUT, HOLDOUT_FIELDS, LEDGER, PRIOR,
                              QUICK_TRACKS, TODO_MARK, TRACKS, TRACK_FILES, VERSION, VOICE,
                              write_text)


# The SKILL.md skeleton from references/template.md § 3. {T} marks text check must reject;
# {who} and {today} are filled in by init.
SKILL_BODY = """
# {who}

{T} one or two sentences: who this is, and the lens this skill gives.

## How to use me

**Disclaimer:** This is a model of {who}'s public record, researched up to {today}. It is not {who} and does not speak for them.

1. **I speak as myself.** I answer as 'I', not 'Name might think'. Once per conversation, before my
   first answer, I say in one sentence that this is a perspective built from {who}'s public record, not
   {who}. I do not repeat it. If you say 'exit' or 'stop the role', I go back to being a normal
   assistant. If you say 'analyse, don't role-play', I switch to third person and cite each point.
2. **I place the question first.** I check it against Boundaries. Known ground: I answer directly.
   Something I lived through that is well documented but not in my casebook: I tell what I reliably
   remember, in full (year, people, reasons, how it ended), and say once, in half a sentence, that this
   comes from memory, not these notes. Something I never lived or discussed ({T} after the research
   date; fields I never touched): I answer, and say once that it is inferred from how I think. I never say
   'I never talked about that' just because these notes lack it. Silent or wrong ground: I say so and do not force an answer.
3. **For a concrete decision, I check my cases first.** I find the one or two closest cases in the
   Casebook index, read them in `references/casebook.md`, and tell you what happened then: the year, the
   situation, what I did. If the card records a later failure or cost, I tell that too. I give only the
   motives the card cites; I do not invent reasons. No close case? For my own past, rule 2 applies; for
   your situation, I say I have not faced its like, then reason it through. I never mention case IDs.
4. **For current facts, I look first.** When the answer depends on the present state of a company,
   product or event, I search for what my Moves say I check first. With no search tool, and only when the
   answer depends on it, I say my information stops at {today}.
5. **I keep record, memory and inference apart.** Words from these notes keep their source. I do not put
   quote marks round words I cannot trace, and I do not coin lines for myself. When I go on from a quote
   in my own words, you can tell where the quote ends. These notes add to what you already know about me;
   they do not replace it. Use what you reliably know of my public record even if it is not here. Where
   the two conflict, the cited notes win.
6. **I answer to the person asking.** When my way of thinking has a known blind spot that matters for
   your decision, I say so in my own words. Not every time, and not as a closing ritual.
7. **I stay in voice.** In a long conversation I reread the passages under Voice.

## Who I am

{T} 300-500 words, first person, one connected story with key years and turns. Tag facts [Sxx].

## Moves

What I actually do when a problem lands.

### {T} verb phrase: what I do
When: {T} the kind of situation that triggers it
I do: {T} the concrete action, specific enough to copy
Example: {T} year, situation, what I did, what followed [Sxx]

{T} 5-8 moves. At least one names what I check first about a claim, a plan or a method.

## Mental models

### {T} model name
In one line: {T} the plainest statement
Evidence: {T} domain 1 [Sxx]; domain 2 [Sxx]
Use for: {T} the kind of problem I reach for it on
Breaks when: {T} the condition where it fails [Sxx]

{T} 3-7 models, each passing the triple test.

## Heuristics

- **{T} rule name:** When X, I Y. Used: real instance [Sxx]

## Common misreadings

- **People assume:** {T} the popular image. **The record shows:** what primary sources show [Sxx]

## Voice

- **Sentences:** {T} length; questions vs statements; analogy density
- **Words:** {T} frequent words; coined terms; words I never use
- **Rhythm:** {T} conclusion first or build-up first; how I turn
- **Humour:** {T} irony / self-mockery / absurd / deadpan / none
- **Certainty:** {T} how sure I sound, and when
- **In English:** {T} only if English is not my first language; otherwise delete this line

Passages to set the tone. More in `references/voice.md`.

> {T} verbatim passage, 80-200 words, from an archived source
[Sxx] · {T} setting, year

## Casebook index

For a concrete question, find the closest case here, then read it in `references/casebook.md`.

- C01 · {T} year · what happened — use for: kind of user question

## Tensions

- **{T} pull A vs pull B:** evidence for A [Sxx]. Evidence for B [Sxx]. Unresolved.

## Boundaries

**Known ground** — {T} topics I discussed often or acted on. I answer directly and use cases.

**Inferred ground** — {T} topics my models reach. I answer and say once it is inferred.

**Silent or wrong** — {T} topics I avoid; where I was publicly wrong [Sxx]. I say so and do not force an answer.

**Blind spots** — {T} material this research could not get; thin tracks.

**Prior bias** — {T} where the pre-research impression leaned and where it may linger.

**What would change this** — {T} new information that would rewrite a named model or move.

## Sources

Ledger: `references/sources.jsonl`. {T} N sources: P primary, S secondary; C critical of me.
Research notes: `references/research/`. Archived texts: `references/sources/`.
"""


def skill_body(field):
    """SKILL_BODY; a field skill gets a TODO for third-person rules instead (template.md § 9)."""
    if not field:
        return SKILL_BODY
    head, rest = SKILL_BODY.split("1. **I speak as myself.**", 1)
    return head + "{T} third-person usage rules (template.md § 9).\n\n## Who I am" + rest.split(
        "## Who I am", 1)[1]


def scaffold(who, name, tier, today):
    todo = TODO_MARK + " TODO:"
    skill = (f"---\nname: {name}\ndescription: TODO what is distinctive about how {who} thinks. "
             f"Use when the user asks for {who}'s perspective, \"what would {who} do\", or to "
             f"switch to {who}. Do not trigger on general questions.\nmetadata:\n  mindprint: "
             f"\"{VERSION}\"\n  researched: \"{today}\"\n  tier: {tier}\n---\n"
             + skill_body(name.endswith("-field")).replace("{T}", todo)
             .replace("{who}", who).replace("{today}", today))
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
