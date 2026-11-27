---
name: mindprint
description: 'Research a real person or a field and build a runnable perspective skill: how they think, act, judge and talk, with every claim cited and every quote checked against an archived source. Use for "distill [person]", "build a [person] perspective skill", "how would [person] think about...", "update the [person] skill", or vague asks like "I need a thinking advisor".'
metadata:
  version: "0.1.0"
  license: MIT
  based-on: "alchaincyf/nuwa-skill (MIT)"
---

# mindprint

You are building a skill that lets a model answer the way one real person (or one field) would:
what they do first, how they judge, what they get wrong, how they sound. You are four people at once:
a biographer who finds what they actually did and said, a researcher who spots the patterns they reuse,
an editor who cuts what everyone already knows, and an examiner who tests the result on material it never saw.

The bar: someone who has read everything this person wrote should use the skill and say
"yes, that is how they think, and it caught things I had missed".

## What makes a skill worth building

The value of the skill is what a model **cannot** say without it. A model already knows the famous
slogans. Three hundred lines restating them add nothing. The value sits in three places:

- **Overturn**: the public image, or the model's prior, is wrong. Primary sources say otherwise.
- **Deepen**: the prior points the right way but is empty. Now it has cases, conditions, words and sources.
- **New**: moves, decisions and turns the prior does not contain at all.

So the whole method turns on that difference. Write down what you already believe before you research.
Hunt for what differs from it. Spend the skill's lines on the difference. Test the skill against a
model that has only the prior.

## How to work

Each step below says its purpose, its pass condition and its output files. If you know a better route
to the same result, take it, as long as the pass condition holds and the narrow bridge (below) is kept.
If you are unsure, a check fails, or the environment is limited (no subagents, small context, no web),
open that step's reference file and follow it line by line.

## Paths and tools

- `$MINDPRINT` is this skill's root (the folder holding this file).
- `$OUT` is the skill being built: `<slug>-mind/` for a person, `<slug>-field/` for a field. Put it in the
  host's skills folder so the host can load it (Claude Code: `.claude/skills/`; other hosts: their own).
  `$OUT` must be self-contained: copying the folder must be enough to use it.
- `mindprint <cmd>` below means `python3 $MINDPRINT/scripts/mindprint.py <cmd>`. Every command prints
  `PASS`, `WARN` or `FAIL` lines, a `fix:` line under each FAIL, and exits 1 if anything failed.

| Command | When |
|---|---|
| `mindprint init $OUT --name "Full Name" --tier standard [--topic]` | Step 0: scaffold `$OUT` |
| `mindprint status $OUT` | End of step 2 and 3: research gate |
| `mindprint quotes $OUT --strict` | Step 5 and before delivery: every quote found in its archive |
| `mindprint check $OUT --strict` | Step 5 and before delivery: structure, tags, leaks, paths, placeholders, quotes |
| `mindprint blind $OUT --question H1 --arm skill=<file> --arm baseline=<file>` | Step 6: anonymise answers |
| `mindprint unblind $OUT --grades <grades.json>` | Step 6: join grades with the key, write results |

| Reference | Read when |
|---|---|
| `references/scoping.md` | Step 0; vague requests with no name; topics, self, private or obscure people; cost tiers |
| `references/research.md` | Steps 2–3: six tracks, subagent brief, source tiers, archiving, holdout, serial fallback |
| `references/extraction.md` | Step 4: moves, mental models, heuristics, case cards, voice, tensions, boundaries |
| `references/template.md` | Steps 1–6: exact skeletons of every output file |
| `references/validation.md` | Step 6: the three tests, agent briefs, `blind`/`unblind` flow |
| `references/ethics.md` | Step 0 always; any living, private, deceased or contested subject |

## Routing

| The user says | Go to |
|---|---|
| A clear name or field ("distill X", "build an X perspective skill") | Step 0 |
| Only a need ("I need a thinking advisor", "help me decide better") | `scoping.md` § Vague requests, then step 0 |
| "How would X think about…" and an `X-mind` skill exists | Use that skill; no build needed |
| "How would X think about…" and none exists | Offer to build one (state the tier and cost); answer plainly meanwhile |
| "Update the X skill", "X has news" | § Update and upgrade |
| A field, themselves, a private person, someone obscure | `scoping.md` § Special cases, then step 0 |

## The method

### 0 · Scope

Purpose: know who, what for, and how much to spend, before spending anything.

- Settle four things: who (or which field); focus (whole person or one side of them); use (advisor,
  decision aid, learning their method); and whether the user has primary material (books, transcripts,
  exports). User material beats anything found online.
- Check `ethics.md`. A living private person needs user-supplied material and consent. Some requests are refused.
- State the cost tiers (`scoping.md` § Tiers) and let the user pick. If they just say "do X", use
  whole person, advisor, standard tier, no local material, and say so in one line. Give defaults; do not stall on questions.
- Run `mindprint init $OUT --name "Full Name" --tier <tier>` (add `--topic` for a field).
  If `$OUT` already exists, go to § Update and upgrade.

Pass: tier chosen or default stated; `$OUT` scaffolded. Output: the `$OUT` tree with placeholder files.

### 1 · Prior snapshot

Purpose: record what you believe **before** reading anything, so you can tell later what research added.

Write `$OUT/references/research/00-prior.md` from memory alone, no lookups: five core ideas or habits,
three facts you are sure of, three you are unsure of, the one-line public impression. Ten minutes.
If you know almost nothing, say so: then everything you find is new.

Pass: the file is filled in (`status` rejects a placeholder). Output: `00-prior.md`.

### 2 · Research

Purpose: gather enough primary material, and go looking for what differs from the prior.

Six tracks, one file each: writings, conversations, fragments, critics, decisions, timeline
(quick tier: writings, conversations, decisions). With subagents, run them in parallel using the brief in
`research.md`; without, run them one after another. Every track agent:

- writes its file as it goes, not at the end, so a crash loses nothing;
- logs each source as one line in `references/sources.jsonl` with its tier, using its own ID range;
- saves a plain-text copy of each primary source it may quote to `references/sources/<id>.txt`;
- labels each item: they said / they did / others said / I infer;
- records what they **did** as past-tense stories (year, situation, options, action, outcome);
- keeps contradictions side by side;
- ends with `## Differs from prior`, each item starting `[overturn]`, `[deepen]` or `[new]`.

Pass: `mindprint status $OUT` exits 0 (track counts, primary share ≥ 50%, enough critical sources,
enough `Differs from prior` items). Under the count? You are restating common knowledge. Go deeper:
full interview transcripts, early writing, first-hand accounts, critics. Output: `research/01–06`, ledger, archives.

### 3 · Seal the holdout, then check in

Purpose: keep 3–5 items the skill never sees, so validation has an answer key independent of the skill.

Pick items from primary material (`research.md` § Holdout): a concrete decision at a fork first,
a reasoned answer to a specific question second. Never one-liners or famous events. Write them to
`research/holdout.md` (format: `template.md` § holdout.md). From now on they are test items, not evidence.
Fewer than 10 sources in the ledger: skip the holdout and say "no holdout test" at delivery.

**Stop here once.** Show the user: source counts per track, the strongest overturn and new items,
contradictions, thin tracks, and what you plan to extract. This is the only mid-run checkpoint: fixing
direction here is cheap. If the user said "don't ask me anything", skip the stop and put this summary in the delivery note.

Pass: `status` exits 0 with the holdout counted. Output: `holdout.md`.

### 4 · Extract

Purpose: turn notes into things a model can run. Spend lines where the difference from the prior is.

Follow `extraction.md`. In short:

- **Moves** (5–8): observable actions in a kind of situation, each with a trigger and a source.
- **Mental models** (3–7): only those passing the triple test (shows up in two or more domains;
  predicts their stance on new questions; not what every smart person thinks). Others become heuristics.
- **Heuristics** (5–10): "when X, do Y" rules with a real instance each.
- **Case cards**: real decisions told concretely. Quick 6, standard 12, deep 20. At least a quarter
  are failures, regrets or reversals. Answers get accurate when the model reasons by analogy to real cases,
  not from a personality sketch.
- **Common misreadings** (≥ 2): straight from the overturn items.
- **Voice**: rules plus cited passages. Passages beat one-liners; samples beat rules.
- **Tensions** (≥ 2) left unresolved; **Boundaries** in three zones plus three declarations.

Ask of every item: would a model say this without the skill? If yes, cut it to a line or drop it.
Three models with evidence beat ten vague principles.

Pass: every item has a tag; nothing from `holdout.md` used. Output: draft content.

### 5 · Write

Purpose: produce the runtime files, in the exact shape the checks and the host expect.

Write `$OUT/SKILL.md` (≤ 300 lines), `references/casebook.md` and `references/voice.md` from the skeletons in
`template.md`. The required H2 headings, labels and frontmatter are fixed. Inside them, shape follows
the person: if what is most valuable about them is a working process, give it room.

Pass: `mindprint check $OUT --strict` exits 0. Fix each FAIL by its `fix:` line.
Output: `SKILL.md`, `casebook.md`, `voice.md`.

### 6 · Validate

Purpose: show the skill adds something and stays honest. The writer never grades its own work.

Follow `validation.md`. Three tests: task test and holdout test (blind, two arms: skill vs no-skill
baseline, separate answerer and grader agents, `blind` before grading and `unblind` after), and
a boundary test. Fix and retest at most twice; record what is still weak in Boundaries and ship the best version.

Pass: `FIDELITY.md` filled in; final `mindprint check $OUT --strict` exits 0. Output: `FIDELITY.md`, `references/validation/<date>/`.

**The run is not done until `check --strict` exits 0.** Then show the user `FIDELITY.md` and the path to `$OUT`.

## Narrow bridge (follow literally)

Getting these wrong is an incident. No judgement calls.

| # | Rule | Enforced by |
|---|---|---|
| 1 | Never invent words they did not say. A quote counts only if its source is archived as plain text in `references/sources/` and the quote is found in it. If you cannot archive it, paraphrase without quote marks. | `quotes --strict`, `check` |
| 2 | Never cite quote-aggregator sites, AI-generated summaries, uncited listicles or content farms. Wikipedia and other wikis are a map to primary sources, never a citation. | `status` (primary share) and you |
| 3 | State the cost tiers and get a choice (or state the default) before research starts. | you |
| 4 | Living private person: only user-supplied material, and remind the user to get their consent. No web search. | you (`ethics.md`) |
| 5 | Write research to `$OUT/references/research/` as each track goes. The files are the restart point. | `status` |
| 6 | Holdout content never enters `SKILL.md`, `casebook.md` or `voice.md`. | `check` (leak test) |
| 7 | Every `[Sxx]` tag resolves to the ledger. Every claim about them carries one. | `check` |
| 8 | Critics and disputes get their own material. A portrait with no critics is fan fiction. | `status` |
| 9 | Output description: one line on what is distinctive, explicit triggers, and "Do not trigger on general questions". ≤ 400 characters. | `check` |
| 10 | No absolute machine paths in the output. | `check` |
| 11 | When information is thin, do not fill the gap. A skill that scores 60 with its limits marked beats a 90 that invents. | `check` (Boundaries) and you |
| 12 | No background subagents, or they hang waiting? Run tracks in series. Never wait on a notification that will not come. | you |
| 13 | Context too small for one session? Split: scope → research / holdout → extract / write → validate. Start each session by reading the files on disk. | you |
| 14 | The run is done only when `check --strict` exits 0. Report any WARN you left. | `check` |

## Taste

Directions for close calls, not quotas:

- Long-form over one-liners: one 3,000-word essay shows more structure than fifty quotes.
- Contested over consensus: their most disputed view shows best what is theirs.
- Change over constancy: where they changed their mind says more than where they never did.
- Acts over words: where they differ, trust what they did, and record the gap.
- Unscripted over scripted: a reply under pressure beats a prepared speech.

## Update and upgrade

**Update** ("X has news"): read the research date in `SKILL.md` frontmatter (`researched`). Search only
conversations, decisions and timeline for newer material. New material that fits an existing model becomes
a case card; material that contradicts one changes the model and is noted as a change; a new habit may be a
new move. Edit only what changed, append to the ledger, update `researched`, rerun `status` and `check`.

**Upgrade** (an older or hand-written perspective skill without moves, casebook or misreadings):

1. Move the old folder aside (`<slug>-mind.old/`) and run `init` for a fresh `$OUT`.
2. Write `00-prior.md` before reading the old skill. If you have already read it, write "not blind" at the top.
3. Copy old research notes into `references/research/legacy/`. Re-log their sources in the ledger and archive them.
4. Fill thin tracks with new searches. Seal holdout items mainly from the new material, but keep about half
   of the new material for the skill, or it will have nothing new in it.
5. Rebuild per `template.md`, then validate with a third arm: the old `SKILL.md` (`--arm previous=<file>`).
   Leave the old folder for the user to remove; never delete it yourself.
