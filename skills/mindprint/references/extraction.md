# Extraction

Read this for step 4. It turns research notes into parts a model can run. Work in the order below.
Each section ends with what failure looks like.

Contents: 1 · Sort by difference · 2 · Moves · 3 · Mental models and the triple test · 4 · Heuristics ·
5 · Case cards · 6 · Common misreadings · 7 · Voice · 8 · Contradictions and tensions · 9 · Boundaries ·
10 · When material is thin

Two rules hold throughout:

- **Every item carries a tag** (`[S501]`) that resolves to the ledger. `check` fails on unresolved tags.
- **Nothing from `holdout.md`.** Not the event, not its reasons, not its words. `check` fails on any
  8-word overlap with a holdout `What happened` line. If a fact appears both in a holdout item and
  elsewhere, leave it out anyway.

## 1 · Sort by difference

Extraction starts with sorting, not summarising. Gather every `## Differs from prior` item from all track
files into one working list:

| Kind | Meaning | Where it goes |
|---|---|---|
| `[overturn]` | the prior or public image is wrong | Common misreadings; rewrite any model it touches from primary sources |
| `[deepen]` | right direction, now with cases, conditions, words | main source of moves, case cards and model evidence |
| `[new]` | not in the prior at all | moves and case cards first |
| confirmed (no tag) | matches the prior, nothing new | one line at most |

Then ask of every item you plan to write: **would a model say this without the skill?** If yes, compress it or drop it.

Failure looks like: paragraphs of "values the long term", "thinks from first principles". Anyone could
write them. Nothing would surprise a person who knows the subject well.

## 2 · Moves

A move is an observable action: what they actually do first in a kind of situation. Mental models answer
"how do they think"; moves answer "what do they do". Users want the second most, and it is the first to get lost.

1. Read `05-decisions.md` and `02-conversations.md`. Pull out every **past-tense action sentence**:
   things they did, not things they argued for.
2. Group similar actions. Count how often each happens and in how many different settings. Two or more
   times, across settings: that is a move.
3. Write each as trigger → concrete action → one cited example. Concrete enough that someone else could copy it.
4. Check back: any fact in the notes with no matching move? That is the usual loss: gathered in research,
   flattened into a value statement in extraction.

Example, with a made-up subject. Notes: "<Name> phoned three customers before reading the pitch deck [S512]",
"before the board vote, <Name> asked two former employees what broke [S524]".
Lost: "values customer insight". Kept: **Talk to the people who live with it before reading the pitch.**
When: judging a product or a company. I do: call two or three users or former staff first, then read the material.

Runtime rule 4 ("look up current facts first") depends on moves naming what this person checks first.
Make sure at least one move says it, concretely.

Failure looks like: a Moves section full of adjectives ("stays curious", "keeps it simple"), none of which
someone could do tomorrow.

## 3 · Mental models and the triple test

A claim counts as a mental model only if it passes all three:

- **Recurs across domains**: the same frame shows up in at least two different areas they discuss.
- **Generative**: it predicts their stance on a question they never addressed.
- **Distinctive**: not what every smart person thinks.

All three: mental model. One or two: heuristic. None: probably a remark made once; drop it.

Process: list every candidate from tracks 01–05 (usually 15–30). Test each. Rank survivors by
distinctiveness. Keep the top 3–7. For each write: one-line statement; evidence from two or more domains,
each tagged; when to use it; **when it breaks**. The best `Breaks when:` is a case where they themselves
got it wrong, with a source.

Failure looks like: the models read like a generic thinking-tools handbook. Swap in another smart person's
name and nothing changes. If you cannot tell who it is with the name removed, you have not extracted them.

## 4 · Heuristics

Fast rules: when X, do Y. 5–10, each with one real instance where they used it, tagged.
Check that a new situation could trigger it. A rule that only fits its original case is an anecdote;
put it in the casebook instead.

## 5 · Case cards

Case cards add more than any other part. At runtime the model finds the closest case and reasons by
analogy before it judges. Answers grounded in a real episode are closer to the person than answers
from a character sketch.

Format: `template.md` § casebook.md (six fields: Situation, What they did, In their words, Outcome, Use for, Sources).
Minimums: quick 6, standard 12, deep 20 (`check` counts).

What to include:

- every major decision and turning point;
- failures, regrets, reversals and word–deed gaps: **at least a quarter** of cards. A casebook of wins
  teaches the model nothing about where they go wrong;
- small, concrete everyday cases: how they answered one email, how they killed one proposal. These
  transfer to users' problems better than famous events;
- two cases with opposite outcomes for the same kind of problem: include both.

How to write:

- Situation: specific enough to show they had other options.
- What they did: actions, not attitudes.
- In their words: words from **that** episode, verbatim from the archive, with a tag. None exists? Write
  `In their words: (none on record)`. Never borrow a line from another occasion.
- Outcome: include later costs and their own second thoughts.
- Use for: the kinds of user questions this case answers, in the user's terms ("whether to shut a
  profitable side line that distracts the team"), not the case's terms. The casebook index copies this.

Failure looks like: every card runs "faced adversity, held firm, won", and would work for any famous
person; or a quote and an event from different years.

## 6 · Common misreadings

Take the 2–5 strongest `[overturn]` items. Each is one list item: what people assume, and what the primary
record shows, tagged. This section corrects the model's prior directly; nothing else does that job.

Found none? Research probably stayed in secondary retellings. Go back to full interview transcripts.

## 7 · Voice

Rules plus samples. Samples matter more.

Rules, six dimensions:

| Dimension | Ask |
|---|---|
| Sentences | long or short; questions or statements; how often analogies |
| Words | frequent words, coined terms, words they never use |
| Rhythm | conclusion first or build-up first; how they turn |
| Humour | irony, self-mockery, absurd, deadpan, none |
| Certainty | "obviously" or "I don't know" |
| References | whom they cite, and how |

For more precision, sample 20 passages from essays and talks and count: average sentence length,
share of questions, analogies per thousand words.

Samples: passages of 80–300 words, verbatim from archives, tagged, grouped by setting (writing, off the cuff,
under challenge, on their own mistakes). Choose passages where you can watch them think, not slogans.
Two or three go in `SKILL.md` to set the tone; 8–15 go in `voice.md`.

Tics in moderation: their frequent phrases belong, but a pile of them is a comedy impression.
Words they never use stay out of the skill too.

Failure looks like: read 100 words and you cannot tell who it is (generic assistant); or a catchphrase in
every sentence (sketch comedy).

## 8 · Contradictions and tensions

Contradictions are part of a person, not bugs to fix. Three kinds:

- **Over time**: said A early, B later. Record the path; weight the recent view; say it changed.
- **By domain**: one rule at work, another at home. Record both; do not force them together.
- **At the core**: values that pull against each other. These go in `## Tensions`, with evidence for each side.

Three wrong ways: pick one side and drop the other; invent a story that reconciles them; pretend there is no conflict.

## 9 · Boundaries

Split their ground into three zones, written as instructions the runtime model can follow:

- **Known ground**: topics they discussed again and again, or acted on, on record. Respond: answer directly, use cases.
- **Inferred ground**: topics they never addressed that their models reach. Respond: answer, and say once it is inferred.
- **Silent or wrong**: topics they deliberately avoid (show the silence; do not generate a clever middle
  position for them) and areas where they were publicly wrong, with an example and tag. Respond: say so; do not force an answer.

Then three declarations that give the skill a shelf life:

- **Blind spots**: what material you could not get; which tracks were thin.
- **Prior bias**: where your pre-research impression leaned, and where it may still linger.
- **What would change this**: specific new information that would rewrite a named model or move.

A list of "I am not the real person" disclaimers is not a boundary. The disclaimer has its own line;
Boundaries say what to do.

## 10 · When material is thin

| Situation | Do this |
|---|---|
| A track has little public information | Write "thin: inferred" next to items drawn from it; list it under Blind spots |
| Only secondary sources for a point | Lower the confidence in the wording: "according to <outlet> [S4xx]" |
| Sources conflict and you cannot decide | Show both; let the user judge |
| They keep something private on purpose | Respect it; it goes in Silent or wrong |
| Fewer than 10 sources | 2–3 models, each marked "based on limited sources"; longer Boundaries; no holdout |
