<h1 align="center">mindprint</h1>

<p align="center">
  <b>Turn a person's public record into a skill your agent can think with. Every quote is checked against its source.</b>
</p>

<p align="center">
  <a href="https://github.com/cyruspastelero/mindprint/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/cyruspastelero/mindprint/actions/workflows/ci.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-d2430e"></a>
  <img alt="No dependencies" src="https://img.shields.io/badge/deps-none-171717">
</p>

<p align="center">
  <a href="#quick-start"><b>Quick start</b></a>
  &nbsp;·&nbsp;
  <a href="examples/benjamin-franklin-mind/SKILL.md"><b>Example: Benjamin Franklin</b></a>
  &nbsp;·&nbsp;
  <a href="#how-it-works"><b>How it works</b></a>
</p>

Based on [nuwa-skill](https://github.com/alchaincyf/nuwa-skill) by Huashu (花叔).

Say "distill Benjamin Franklin" and your agent researches him, builds a `benjamin-franklin-mind`
skill, and tests it blind against its own unaided guess. Then you can ask "what would Franklin do
here?" and get an answer grounded in what he actually did, not in famous slogans.

It works with Claude Code, Codex, Cursor, Gemini CLI and any agent that reads
[Agent Skills](https://agentskills.io).

## What a built skill looks like

From the [Franklin example](examples/benjamin-franklin-mind/SKILL.md):

> ### Hand over a procedure, not a verdict
> When: A friend asks me what to decide in their own affairs.
> I do: Decline to judge the facts I cannot see. Give a method: pro and con columns kept over three
> or four days, strike out equal weights, wait a day or two more, then decide.
> Example: 1772, Priestley asked my advice on a hard choice of his own. I answered that I could not
> advise him what to determine, "but if you please I will tell you how" [S202].

`[S202]` points to the source ledger. The letter is archived as plain text in the skill, and
`mindprint check` fails if the quote isn't in it.

## Why it is different

Persona prompts tend to invent quotes and repeat what the model already knows. mindprint is built
against both:

- **Quotes are verified.** A quote counts only if its source is saved in the skill and the words are
  found in it. The Franklin example has 120 quotes, all found.
- **It looks for what the model gets wrong.** Before any research, the agent writes down what it
  already believes. Research hunts for what overturns, deepens or adds to that, and the skill spends
  its lines there.
- **It is tested blind.** A few real decisions are sealed before extraction and never enter the
  skill. Separate agents answer with and without the skill, and a grader scores them without knowing
  which is which. The CLI shuffles the answers and keeps the key.
- **Critics are required.** A portrait with no critics fails the research gate.
- **Rules are enforced by a script, not just asked for.** Citations, structure, holdout leaks,
  leftover placeholders and machine paths are all checked by `mindprint check`.

## Quick start

**Claude Code:**

```text
/plugin marketplace add cyruspastelero/mindprint
/plugin install mindprint@mindprint
```

**Any other agent:** copy `skills/mindprint/` into its skills folder, or run
`npx skills add cyruspastelero/mindprint`.

Then ask:

```text
Distill Benjamin Franklin
Build a perspective skill for Ada Lovelace, quick tier
I keep making the same bad decisions. I need a thinking advisor.
```

The agent states the cost tier, researches, stops once to show you what it found, then builds and
tests the skill. Once it is built, ask "What would Franklin do about…?"

To try the example without building anything, copy `examples/benjamin-franklin-mind/` into your
skills folder.

## How it works

1. **Scope.** Who, what for, and which tier (quick, standard or deep). `mindprint init` scaffolds it.
2. **Prior snapshot.** The agent writes what it believes before reading anything.
3. **Research.** Six tracks: writings, conversations, fragments, critics, decisions, timeline.
   Sources are logged with a tier, and primary sources are archived as plain text.
4. **Seal the holdout.** 3–5 real decisions are set aside as test questions.
5. **Extract and write.** Moves, mental models, heuristics, case cards, voice, tensions, boundaries.
6. **Validate.** Blind holdout, task and boundary tests. Results go in `FIDELITY.md`, losses included.

The method is in [`skills/mindprint/SKILL.md`](skills/mindprint/SKILL.md), and the file formats
are in [`docs/SPEC.md`](docs/SPEC.md).

## The CLI

Python 3.9+, standard library only. The agent runs it; you can too. From the repo root, each
command below is `python3 skills/mindprint/scripts/mindprint.py <command>`.

| Command | Checks |
| --- | --- |
| `init <out> --name "…" --tier quick\|standard\|deep` | scaffolds a new skill (default tier: standard) |
| `status <out>` | research gate: primary share, critics, what differs from the prior, holdout |
| `check <out> --strict` | headings, counts, citations, holdout leaks, placeholders, paths, quotes |
| `quotes <out> --strict` | each quote against its archived source; unarchived quotes fail |
| `blind` / `unblind` | shuffles answers for the grader, then joins grades with the key |

## Example results

The Franklin example, tested blind on 2026-11-28. The same model answered with and without the
skill; a separate grader scored the shuffled answers 0–10.

| Test | With skill | Without | What it shows |
| --- | --- | --- | --- |
| Holdout (4 sealed decisions) | 32 | 26 | One clear win, three ties. Famous episodes gain little. |
| Task (2 real dilemmas) | 18 | 8 | All 8 Franklin-specific points were real and in the skill. None invented. |
| Boundary (smartphones) | pass | n/a | It said the view was inferred, not his. |

Full results, including where it still falls short, are in
[`FIDELITY.md`](examples/benjamin-franklin-mind/FIDELITY.md).

## Limits and ethics

A built skill is a model of the public record, not the person, and every skill says so. Living
private people are built only from material the user supplies, with their consent. See
[`ethics.md`](skills/mindprint/references/ethics.md).

## License

[MIT](LICENSE). See [NOTICE.md](NOTICE.md) for the original's licence and the example's sources.
