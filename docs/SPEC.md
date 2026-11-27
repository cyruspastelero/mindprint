# mindprint spec (contract between the method docs and the CLI)

mindprint is an agent skill that researches a real person (or a field) and builds a
runnable "perspective skill" from it: how they think, act, judge and talk, with every
claim cited and every quote checked against an archived source.

It is an English rewrite of the method in alchaincyf/nuwa-skill (MIT), redesigned so that
the rules a model tends to break are enforced by a script, not just asked for in prose.

This file is the contract. `skills/mindprint/` (the method) and
`skills/mindprint/scripts/mindprint.py` (the CLI) must both follow it exactly.

## Repo layout

```
mindprint/
├── .claude-plugin/plugin.json, marketplace.json
├── skills/mindprint/
│   ├── SKILL.md                  # the method; ≤ 250 lines
│   ├── references/
│   │   ├── scoping.md            # vague requests → candidates; tiers + cost; special cases (topic, self, private person, obscure)
│   │   ├── research.md           # six research tracks, brief template for subagents, source tiers, serial fallback
│   │   ├── extraction.md         # moves, models (triple test), heuristics, case cards, voice, contradictions
│   │   ├── template.md           # exact skeleton of the output skill (headings below)
│   │   ├── validation.md         # task test, holdout test, boundary test; blind two-arm protocol; briefs
│   │   └── ethics.md             # living people, consent, impersonation, defamation, disclaimer
│   └── scripts/mindprint.py      # single-file CLI, Python ≥ 3.9 stdlib only
├── tests/test_mindprint.py       # unittest, stdlib only
├── examples/benjamin-franklin-mind/   # a full output skill built with mindprint
└── .github/workflows/ci.yml
```

## Output skill layout (`$OUT`, named `<slug>-mind`, topics `<slug>-field`)

```
<slug>-mind/
├── SKILL.md                 # runtime core, ≤ 300 lines
├── FIDELITY.md              # validation results
└── references/
    ├── casebook.md          # case cards, read on demand
    ├── voice.md             # quote library, read on demand
    ├── sources.jsonl        # source ledger, one JSON object per line
    ├── sources/             # archived plain-text snapshots: S01.txt, S02.txt …
    ├── research/
    │   ├── 00-prior.md      # written before any research
    │   ├── 01-writings.md
    │   ├── 02-conversations.md
    │   ├── 03-fragments.md
    │   ├── 04-critics.md
    │   ├── 05-decisions.md
    │   ├── 06-timeline.md
    │   └── holdout.md       # sealed test items; content must never appear in the skill
    └── validation/<YYYY-MM-DD>/   # blind packets, key, grades (written by the CLI)
```

Quick tier uses tracks 01, 02 (or 01 if no conversations exist), 05 only; the other
track files may be absent.

## Source ledger: `references/sources.jsonl`

One object per line. Fields:

| field | type | rule |
|---|---|---|
| `id` | string | `S` + 2–3 digits, unique (`S01`) |
| `title` | string | required |
| `by` | string | author or outlet |
| `date` | string | `YYYY`, `YYYY-MM` or `YYYY-MM-DD`, or `""` if unknown |
| `url` | string | `""` allowed for user-supplied files |
| `track` | string | one of `writings conversations fragments critics decisions timeline` |
| `tier` | string | `primary` (their own words or acts, first-hand record), `secondary` (reporting, biography, interviews of others), `tertiary` (summaries, wikis, quote sites) |
| `critical` | bool | true if the source criticises or disputes them |
| `archive` | string | path relative to `references/`, e.g. `sources/S01.txt`, or `""` |

## Citation tags

Anywhere in the output skill, a claim cites sources with `[S01]` or `[S01, S07]`.
Every tag must resolve to the ledger.

## Research files

Each track file ends with a section `## Differs from prior` whose list items begin with
one of `[overturn]`, `[deepen]`, `[new]`.

`holdout.md` holds 3–5 items:

```
## H1 · <short title>
Source: [S04]
Question: <the question an answerer will get>
What happened: <what they actually said or did, and why>
```

## Output SKILL.md

Frontmatter:

```
---
name: <slug>-mind
description: <one line: what is distinctive about how they think>. Use when the user asks for <Name>'s perspective, "what would <Name> do", or to switch to <Name>. Do not trigger on general questions.
metadata:
  mindprint: "0.1.0"
  researched: "YYYY-MM-DD"
  tier: quick | standard | deep
---
```

Description ≤ 1024 characters (hard), ≤ 400 recommended, must contain
"Do not trigger on general questions".

Required H2 headings, in this order (exact text):

1. `## How to use me` – must contain a line starting `**Disclaimer:**` stating this is a model of
   the public record, not the person, and the research cutoff date.
2. `## Who I am`
3. `## Moves` – 5–8 `### ` subsections. Each has a line starting `When:` and at least one tag.
4. `## Mental models` – 3–7 `### ` subsections. Each has lines starting `Evidence:` and `Breaks when:` and at least one tag.
5. `## Heuristics` – 5–10 list items, each with a tag.
6. `## Common misreadings` – ≥ 2 list items, each with a tag.
7. `## Voice` – rules plus ≥ 2 blockquote passages with tags; points to `references/voice.md`.
8. `## Casebook index` – list of `C01 · title` lines pointing to `references/casebook.md`.
9. `## Tensions` – ≥ 2 list items (unresolved contradictions; do not reconcile them).
10. `## Boundaries` – contains the bold labels `**Known ground**`, `**Inferred ground**`, `**Silent or wrong**`, `**Blind spots**`, `**Prior bias**`, `**What would change this**`.
11. `## Sources` – points to `references/sources.jsonl`; summary of primary/secondary counts.

## casebook.md

```
## C01 · <title>
Situation: …
What they did: …
In their words: "…" [S03]
Outcome: …
Use for: …
Sources: [S03, S09]
```

Minimum cards: quick 6, standard 12, deep 20.

## Quotes

A quote is either a markdown blockquote (`> …` lines) or text in straight or curly double
quotes of ≥ 6 words, followed on the same line or the next line by a citation tag.
When the cited source has an `archive`, the quote must appear in that file after
normalisation: casefold, unify curly quotes and dashes, collapse whitespace, drop
punctuation other than apostrophes. `...` or `…` splits the quote into fragments that
must each appear, in order. Square-bracket editorial insertions `[like this]` are ignored.

## CLI: `python3 skills/mindprint/scripts/mindprint.py <command>`

All commands print a plain report, one finding per line, prefixed `PASS`, `WARN` or `FAIL`,
each FAIL followed by an indented `fix:` line. Exit code 1 if any FAIL, else 0.
`--json` prints the findings as JSON instead.

| command | does |
|---|---|
| `init <out-dir> --name "Full Name" [--tier standard] [--topic]` | scaffolds `$OUT` with all files above, placeholder text, empty ledger; refuses to overwrite a non-empty dir |
| `status <out>` | research gate: per-track source counts; primary share ≥ 50%; ≥ 1 critical source (standard/deep: ≥ 2); `Differs from prior` items ≥ 8 (quick: ≥ 5); holdout has 3–5 items unless ledger < 10 sources (then WARN "no holdout test"); 00-prior.md exists and is non-placeholder |
| `check <out>` | everything in "Output SKILL.md", casebook minimum, tags resolve, line limits, no absolute paths (`/Users/`, `/home/`, `C:\`), no leftover `TODO`/placeholder markers, holdout leak check (no holdout `What happened` sentence of ≥ 8 words, and no 8-word shingle from it, appears in SKILL.md/casebook.md/voice.md), then runs `quotes` |
| `quotes <out> [--strict]` | verifies every quote as above. Archived and found: PASS. Archived and not found: FAIL. No archive: WARN (FAIL with `--strict`) |
| `blind <out> --question Q1 --arm skill=<file> --arm baseline=<file> [--arm …]` | copies each arm's answer into `validation/<date>/<Q>/` as `A.md`, `B.md`… in a random order (`--seed` for tests), strips lines matching skill names/case ids (`C\d+`, `[S\d+]` tags are kept), appends the mapping to `validation/<date>/key.json` |
| `unblind <out> --grades <grades.json> [--date YYYY-MM-DD]` | grades.json: `{"Q1": {"A": 7, "B": 5}, …}` plus optional `"max": 10`; joins with key.json; prints a markdown table of per-question and total scores per arm, flags ties (within 2 points on holdout questions, `H*`), and writes it to `validation/<date>/results.md` |

Clarifications (settled after the first build):

- `check --strict` passes `--strict` to `quotes`. A finished skill must pass `check --strict`.
- `check` fails on template placeholders (`<quote>`, `<Name>`, `<one line …>`) outside code,
  ignoring HTML comments and real HTML tags.
- Blockquote tags go on the last line of the quote or the line after it. Lines starting with
  `—`, `–` or `--` inside a blockquote are attribution and are not checked.
- A blockquote is checked as a whole (minus attribution lines). If only a quoted span inside
  it is in the source and the rest is at most 6 framing words ("He said"), `quotes` WARNs
  `quote-framing`; otherwise it FAILs. A quote with no words left after removing tags,
  `[insertions]` and `...` FAILs.
- An inline quote may wrap across lines within one paragraph. A cited paragraph with an odd
  number of straight double quotes (e.g. `5"`) gets WARN `quote-unparsed`; use curly quotes.
- `check` also runs the holdout rules (when the ledger has ≥ 10 sources). The absolute-path
  rule ignores matches inside a URL (`https://…/home/…`).
- Parallel research agents take separate ID ranges (`S101–S199` for track 01, `S201–S299` for
  track 02 …) so the ledger never collides.
- Disclaimer: must contain "public record" and a four-digit year.
- Grades are 0–10 per question. Holdout questions (`H*`) count as a tie when the arms are within
  2 points of each other; task and boundary questions tie only on equal scores.
- `blind` takes `--date`. It never prints the letter mapping. It scrubs case ids and the skill's
  name inline and drops only purely meta lines ("using the skill", "as an AI"). The grader works
  in a folder outside `$OUT` and never sees `key.json`.
- `FIDELITY.md` follows `references/template.md` §8: a header line (date, answer and grader
  models, independence), then `## Holdout test`, `## Task test`, `## Boundary test`, `## Rounds`,
  `## Known weak spots`. Results that are not in yet say "pending".

Code rules: functions under ~50 lines, no third-party packages, clear error messages naming
the file and line, no swallowed exceptions.
