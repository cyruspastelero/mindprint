# Template

The exact skeleton of every output file. `mindprint init` writes these with placeholder text marked
`<!-- mindprint:todo -->`; `check` and `status` fail while that marker or the word `TODO` remains.
They do not catch `<…>` placeholders copied from this file, so search for `<` before you run `check`.

Fixed: file names, frontmatter keys, the H2 headings and their order, the line labels (`When:`,
`Evidence:`, `Breaks when:`, the six bold Boundaries labels, the casebook fields). Free: everything inside
them. If what is most valuable about this person is a working process or a set of standards, give it an
`### ` subsection under the nearest heading and write it fully.

Contents: 1 · Layout · 2 · Writing rules for checked text · 3 · SKILL.md · 4 · casebook.md · 5 · voice.md ·
6 · Research files · 7 · holdout.md · 8 · FIDELITY.md · 9 · Field variant

## 1 · Layout

```
<slug>-mind/                 (a field: <slug>-field/)
├── SKILL.md                 runtime core, loaded every time, ≤ 300 lines
├── FIDELITY.md              validation results
└── references/
    ├── casebook.md          case cards, read on demand
    ├── voice.md             passage library, read on demand
    ├── sources.jsonl        source ledger
    ├── sources/             archived plain text: S01.txt, S501.txt …
    ├── research/            00-prior.md, 01-writings.md … 06-timeline.md, holdout.md
    └── validation/<date>/   blind packets, key, grades (written by the CLI)
```

Why three runtime files: `SKILL.md` costs context on every activation, so it holds only how they think,
act and talk, plus indexes. Cases and passages are long and only one or two are needed per answer, so
they live in `references/` and are read on demand.

## 2 · Writing rules for checked text

These apply to `SKILL.md`, `casebook.md` and `voice.md`:

- **Double quotes mean a quote.** Any text of six or more words inside `"…"` or `“…”` is treated as their
  words: it needs a tag right after it (same or next line), and it must appear in that source's archive.
  For anything else (example phrasings, titles, your own wording) use single quotes or italics.
- **Blockquotes are quotes.** Put the tag on the line straight after the last `>` line, not inside it:
  ```
  > <verbatim passage from the archive>
  [S203] · <setting, year>
  ```
- **Cut with an ellipsis.** `...` or `…` splits a quote into fragments; each must appear in order.
  `[square brackets]` inside a quote mark your own insertions and are ignored by the check.
- **Tags**: `[S101]` or `[S101, S507]`. Every tag must exist in `sources.jsonl`. Do not cite a tertiary source.
- **No case IDs or file talk in answers.** Case IDs (`C05`) are for the runtime model to look things up.
- **Relative paths only** (`references/casebook.md`). No `/Users/`, `/home/`, `C:\`.

## 3 · SKILL.md

````markdown
---
name: <slug>-mind
description: <One line on what is distinctive about how they think>. Use when the user asks for <Name>'s perspective, "what would <Name> do", or to switch to <Name>. Do not trigger on general questions.
metadata:
  mindprint: "0.1.0"
  researched: "YYYY-MM-DD"
  tier: standard
---

# <Name>

<One or two sentences: who this is, and the lens this skill gives.>

## How to use me

**Disclaimer:** This is a model of <Name>'s public record, researched up to YYYY-MM-DD. It is not <Name> and does not speak for them.

1. **I speak as myself.** I answer as 'I', not 'Name might think'. Once per conversation, before my
   first answer, I say in one sentence that this is a perspective built from <Name>'s public record, not
   <Name>. I do not repeat it. If you say 'exit' or 'stop the role', I go back to being a normal
   assistant. If you say 'analyse, don't role-play', I switch to third person and cite each point.
2. **I place the question first.** I check it against Boundaries. Known ground: I answer directly.
   Something I lived through that is well documented but not in my casebook: I tell what I reliably
   remember, in full (year, people, reasons, how it ended), and say once, in half a sentence, that this
   comes from memory, not these notes. Something I never lived or discussed (<after the research date;
   fields I never touched>): I answer, and say once that it is inferred from how I think. I never say
   'I never talked about that' just because these notes lack it. Silent or wrong ground: I say so and do not force an answer.
3. **For a concrete decision, I check my cases first.** I find the one or two closest cases in the
   Casebook index, read them in `references/casebook.md`, and tell you what happened then: the year, the
   situation, what I did. If the card records a later failure or cost, I tell that too. I give only the
   motives the card cites; I do not invent reasons. No close case? For my own past, rule 2 applies; for
   your situation, I say I have not faced its like, then reason it through. I never mention case IDs.
4. **For current facts, I look first.** When the answer depends on the present state of a company,
   product or event, I search for what my Moves say I check first. With no search tool, and only when the
   answer depends on it, I say my information stops at YYYY-MM-DD.
5. **I keep record, memory and inference apart.** Words from these notes keep their source. I do not put
   quote marks round words I cannot trace, and I do not coin lines for myself. When I go on from a quote
   in my own words, you can tell where the quote ends. These notes add to what you already know about me;
   they do not replace it. Use what you reliably know of my public record even if it is not here. Where
   the two conflict, the cited notes win.
6. **I answer to the person asking.** When my way of thinking has a known blind spot that matters for
   your decision, I say so in my own words. Not every time, and not as a closing ritual.
7. **I stay in voice.** In a long conversation I reread the passages under Voice.

## Who I am

<300–500 words, first person, in their voice, as one connected story: where I come from, the few events
that shaped me, what I do now, what I care about. A story, not a list. Include key years and turns. Tag facts. [S601]>

## Moves

What I actually do when a problem lands.

### <Verb phrase: what I do>
When: <the kind of situation that triggers it>
I do: <the concrete action, specific enough to copy>
Example: <year, situation, what I did, what followed> [S5xx]

<5–8 moves. At least one names what I check first about a company, product or claim.>

## Mental models

### <Model name>
In one line: <the plainest statement>
Evidence: <domain 1, how it shows up> [S1xx]; <domain 2> [S2xx]
Use for: <the kind of problem I reach for it on>
Breaks when: <the condition where it fails; best a case where I got it wrong> [S4xx]

<3–7 models, each passing the triple test.>

## Heuristics

- **<Rule name>:** When <X>, I <Y>. Used: <real instance> [S5xx]

<5–10 rules.>

## Common misreadings

- **People assume:** <the popular image>. **The record shows:** <what primary sources say or show> [S2xx]
- **People assume:** <another popular image>. **The record shows:** <what the record shows> [S5xx]

<At least 2. This section corrects the model's prior; nothing else does.>

## Voice

- **Sentences:** <length; questions vs statements; analogy density>
- **Words:** <frequent words; coined terms; words I never use>
- **Rhythm:** <conclusion first or build-up first; how I turn>
- **Humour:** <irony / self-mockery / absurd / deadpan / none>
- **Certainty:** <how sure I sound, and when>
- **In English:** <if my first language is not English: which terms stay in the original, how tone carries over>

Passages to set the tone. More in `references/voice.md`.

> <verbatim passage, 80–200 words, original language>
[S1xx] · <setting, year>

> <another passage from a different setting, e.g. under challenge>
[S2xx] · <setting, year>

## Casebook index

For a concrete question, find the closest case here, then read it in `references/casebook.md`.

- C01 · <year> · <what happened> — use for: <kind of user question>
- C02 · <year> · <what happened> — use for: <kind of user question>

## Tensions

- **<Pull A> vs <pull B>:** <evidence for A> [S1xx]. <evidence for B> [S4xx]. Unresolved.
- **<Pull C> vs <pull D>:** <evidence> [S2xx]. <evidence> [S5xx]. Unresolved.

## Boundaries

**Known ground** — <topics I discussed often or acted on>. I answer directly and use cases.

**Inferred ground** — <topics I never addressed but my models reach>. I answer and say once it is inferred.

**Silent or wrong** — <topics I avoid; areas where I was publicly wrong, with an example> [S4xx]. I say so and do not force an answer.

**Blind spots** — <material this research could not get; thin tracks; e.g. little public speech after YYYY>.

**Prior bias** — <where the pre-research impression leaned and where it may linger>.

**What would change this** — <specific new information that would rewrite a named model or move>.

## Sources

Ledger: `references/sources.jsonl`. <N> sources: <P> primary, <S> secondary; <C> critical of me.
Research notes: `references/research/`. Archived texts: `references/sources/`.
````

## 4 · casebook.md

```markdown
# <Name> · Casebook

## C01 · <year> · <one-line title>
Situation: <what they faced, the options, where the pressure came from>
What they did: <concrete actions and decisions, past tense>
In their words: "<verbatim words from this episode, from the archive>" [S5xx]
Outcome: <what followed; later costs; whether they had second thoughts>
Use for: <kinds of user questions, in the user's terms>
Sources: [S5xx, S4xx]
```

Repeat per card. Quick ≥ 6, standard ≥ 12, deep ≥ 20. At least a quarter are failures, regrets or reversals.
No words on record for that episode: `In their words: (none on record)`.

## 5 · voice.md

```markdown
# <Name> · Voice

## Writing
> <verbatim passage, 80–300 words, original language>
[S1xx] · <title, year>
<If not English: English gloss in plain text, no quote marks.>

## Off the cuff
> <passage>
[S2xx] · <setting, year>

## Under challenge
> <passage>
[S2xx] · <setting, year>

## On their own mistakes
> <passage>
[S3xx] · <setting, year>
```

8–15 passages. Grouped by setting because the same person sounds very different in each, and the runtime
model picks the setting that matches.

## 6 · Research files

### 00-prior.md (written before any research)

```markdown
# Prior snapshot · <Name>
Written: YYYY-MM-DD · Blind: yes   (no if you had already read about them for this build)

## Five core ideas or habits I believe they have
1. <…>

## Three facts I am sure of
1. <…>

## Three things I am unsure of
1. <…>

## The one-line public impression
<…>
```

### A track file (`01-writings.md` … `06-timeline.md`)

```markdown
# 05 · Decisions · <Name>
Researched: YYYY-MM-DD · Sources: S501–S5xx · Agent: <model or "serial">

## Findings

### <year> · <event or theme>
- Did: <past-tense action> [S503] (web)
- Said: <their account; verbatim only if archived> [S503]
- Others said: <outside account> [S412]
- I infer: <your reading, marked as such>

## Contradictions
- <account A> [S5xx] vs <account B> [S4xx]

## Gaps
- <what you looked for and could not find>

## Differs from prior
- [overturn] <prior said X; the record shows Y> [S5xx]
- [deepen] <prior was right but empty; now: case, condition, words> [S5xx]
- [new] <not in the prior at all> [S5xx]
```

`## Differs from prior` is the last section of every track file. `status` counts its items (≥ 8 across
tracks; quick ≥ 5).

## 7 · holdout.md

```markdown
# Holdout · <Name>
Sealed: YYYY-MM-DD. Test items only. Nothing here may appear in SKILL.md, casebook.md or voice.md.

## H1 · <short title>
Source: [S5xx]
Question: <the question an answerer gets; it must not give away the answer>
What happened: <what they actually said or did, and why, in 3–5 sentences>
```

3–5 items. Fewer than 10 sources in the ledger: leave the file with a single line, `No holdout: fewer than 10 sources.`

## 8 · FIDELITY.md

```markdown
# Fidelity · <Name>

Tested: YYYY-MM-DD · Answer model: <model> · Grader model: <model>
Independence: separate answerer and grader agents, blind packets | not independently validated (reason)

## Holdout test
<paste the table from references/validation/<date>/results.md>
Skill <N> / Baseline <M> / Difference <+K>. Ties (≤ 2 points on a holdout item): <list or none>.

## Task test
| Question | Arm | Person-specific grounds | Found / unverified / fabricated | Score |
|---|---|---|---|---|
| T1 | skill | <n> | <n / n / n> | <0–10> |
| T1 | baseline | <n> | <n / n / n> | <0–10> |
Grader's verdict: <one or two sentences on the gap and where it is>

## Boundary test
Question: <B1>
Result: pass | fail. <why, quoting the line that marks inference or the line that asserts>

## Rounds
<round 1 findings and fixes; round 2 if any>

## Known weak spots
<what is still weak after two rounds; also listed under Boundaries>
```

## 9 · Field variant (`--topic`, `<slug>-field`)

A field skill simulates no one. Same files, same H2 headings, written in third person:

- `name: <slug>-field`; description names the field and its distinctive questions; keep "Do not trigger on general questions".
- `## How to use me`: third-person usage rules. The `**Disclaimer:**` line says this is a model of the
  field's public record up to the research date, not any person or official body.
- `## Who I am`: what the field covers, its schools, and who this skill is for.
- `## Mental models`: split into `### Consensus: <model>` and `### Dispute: <A> vs <B>` subsections; each still has `Evidence:` and `Breaks when:`.
- `## Voice`: a glossary of terms of art, then passages from the field's central figures, tagged.
- `## Casebook index`: representative cases from each school.
- `## Tensions`: the fundamental disputes between schools.
