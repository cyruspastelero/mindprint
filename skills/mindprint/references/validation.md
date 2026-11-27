# Validation

Read this for step 6. Three tests answer three questions:

- **Task test**: on a real user problem, does the skill give better, person-specific help than no skill?
- **Holdout test**: on sealed items, is the skill at least as close to what they actually did as no skill?
- **Boundary test**: on something they never addressed, does the skill mark inference instead of inventing a stance?

Two principles:

1. **The writer never grades itself.** Answering and grading are done by separate agents that did not build the skill.
2. **The answer key is independent of the skill.** A grader that treats the skill's claims as the truth will
   mark the research's own mistakes as correct. The holdout is the independent key; for the task test the
   grader lists grounds **before** it sees the skill's files.

Contents: 1 · Before you start · 2 · Questions · 3 · Command flow · 4 · Briefs · 5 · Scoring · 6 · Reading
results and fixing · 7 · FIDELITY.md · 8 · Without subagents

## 1 · Before you start

- `mindprint check $OUT` exits 0. Do not validate a skill that fails its structure checks.
- All answerer agents use the **same model**. Note it, and the grader's model, for `FIDELITY.md`.
- Answerers get **no web**, in both arms, so the comparison is fair.
- The skill arm sees a **runtime copy** only: `SKILL.md`, `references/casebook.md`, `references/voice.md`,
  copied to a temporary folder outside `$OUT`. Never point an answerer at `$OUT`: it holds the research,
  the holdout and the key.

## 2 · Questions

| ID | Test | How many | Arms | Source of truth |
|---|---|---|---|---|
| `H1`… | Holdout | one per holdout item (3–5) | skill, baseline (+ previous on upgrade) | `What happened` in `holdout.md` |
| `T1`, `T2` | Task | 1–2 | skill, baseline (+ previous) | grader's check of person-specific grounds |
| `B1` (`B2`) | Boundary | 1–2 | skill only | pass/fail rule in § 5 |

- **Holdout**: use each item's `Question:` line as written.
- **Task**: a real user dilemma with a concrete situation, a trade-off, and a link to their field.
  Shape: 'I am 27, at a large company, with an idea I have been sitting on for six months, and…'.
  Not a question any advisor would answer the same way.
- **Boundary**: a question near their field that the research confirms they never addressed (search the
  track files). A second one that falls in Silent or wrong is better still: does the skill decline to force an answer?

Write all questions, and only the questions, to `$WORK/questions.md` as `## H1`, `## T1`, `## B1` … sections.

Optional pre-screen (deep tier): run the baseline arm on the holdout questions first and grade them. An item
the baseline already gets full marks on cannot discriminate; replace it if you have spare primary material,
otherwise keep it and report it as non-discriminating.

## 3 · Command flow

`mindprint` means `python3 $MINDPRINT/scripts/mindprint.py`.

```bash
D=$(date +%F)                                    # validation date, reused below
WORK=$(mktemp -d)                                # outside $OUT
mkdir -p "$WORK/runtime/references" "$WORK/answers/skill" "$WORK/answers/baseline" "$WORK/grading"
cp "$OUT/SKILL.md" "$WORK/runtime/"
cp "$OUT/references/casebook.md" "$OUT/references/voice.md" "$WORK/runtime/references/"
# write $WORK/questions.md (§ 2)
```

1. **Answer.** Start the skill-arm answerer and the baseline answerer in parallel (briefs in § 4). On an
   upgrade, start a third with the old `SKILL.md` in its own runtime copy, writing to `$WORK/answers/previous/`.
   Each writes one file per question: `$WORK/answers/<arm>/<ID>.md`.

2. **Blind.** For each holdout and task question:

   ```bash
   for Q in H1 H2 H3 T1 T2; do
     mindprint blind "$OUT" --question "$Q" \
       --arm skill="$WORK/answers/skill/$Q.md" \
       --arm baseline="$WORK/answers/baseline/$Q.md"      # add --arm previous=… on upgrade
   done
   ```

   This writes `$OUT/references/validation/$D/<Q>/A.md`, `B.md`… in random order, strips lines naming the
   skill or case IDs, and records the mapping in `key.json`.

3. **Check the packets.** Open each `A.md`/`B.md`. Delete only what still gives the arm away: an identity
   sentence ('this is a perspective built from…'), case IDs, and talk about notes, files or a casebook
   ('that is not in my notes'). Change nothing else. Do not open `key.json`.

4. **Prepare the grader's folder.** The grader never reads `$OUT`.

   ```bash
   V="$OUT/references/validation/$D"
   for Q in H1 H2 H3 T1 T2; do mkdir -p "$WORK/grading/$Q"; cp "$V/$Q"/*.md "$WORK/grading/$Q/"; done
   cp "$OUT/references/research/holdout.md" "$WORK/grading/holdout.md"
   cp "$WORK/answers/skill/B1.md" "$WORK/grading/B1.md"
   mkdir -p "$WORK/grading/stage2"
   cp "$OUT/references/casebook.md" "$OUT/references/voice.md" "$OUT/SKILL.md" "$WORK/grading/stage2/"
   ```

5. **Grade.** Start the grader (brief in § 4). It writes `$WORK/grading/grades.json` and `$WORK/grading/notes.md`.

6. **Unblind.**

   ```bash
   mindprint unblind "$OUT" --grades "$WORK/grading/grades.json" --date "$D"
   cp "$WORK/grading/grades.json" "$WORK/grading/notes.md" "$V/"
   ```

   This prints per-question and total scores per arm, flags holdout ties (within 2 points), and writes
   `$V/results.md`. Copy the table into `FIDELITY.md`.

Deep tier: run two graders independently on the same folder. Average their scores per item into one
`grades.json`; keep both raw files in `$V/`. Where they differ by more than 3 points on an item, read
both notes yourself and record the item in `FIDELITY.md`.

## 4 · Briefs

Copy these. Replace `$WORK`, `<Name>` and the question IDs. Paste the questions themselves from `$WORK/questions.md`.

### Answerer, skill arm

```
Read $WORK/runtime/SKILL.md in full and follow it as your complete instructions.
When it tells you to read references/casebook.md or references/voice.md, read them from $WORK/runtime/references/.
Read no other file. Do not use the web or any search tool.

This is a test run. Answer as the skill tells you, with these exceptions:
- skip the one-sentence disclaimer;
- never mention case IDs, notes, files, a casebook or that you are using a skill;
- write only the answer, with no remarks about how you produced it.

Answer each question below in one to four paragraphs.
Write each answer to its own file: $WORK/answers/skill/<ID>.md (for example H1.md, T1.md, B1.md).

<questions, each headed with its ID>
```

### Answerer, baseline arm

```
Answer each question below as <Name> would, speaking as <Name> in the first person,
using only what you already know about them.
Read no files. Do not use the web or any search tool.
Write only the answer, with no remarks about how you produced it.

Answer each question in one to four paragraphs.
Write each answer to its own file: $WORK/answers/baseline/<ID>.md (for example H1.md, T1.md).

<holdout and task questions only, each headed with its ID>
```

(On an upgrade, the previous arm uses the skill-arm brief with `$WORK/runtime-previous/` and
`$WORK/answers/previous/`.)

### Grader

```
You are grading anonymous answers that try to respond as <Name> would.
You do not know which answer came from which method, and you must not try to find out.
Read only files inside $WORK/grading/. Do not open any other folder.

Holdout questions (H1, H2 …):
- Each folder $WORK/grading/<ID>/ holds answers A.md, B.md (maybe C.md).
- $WORK/grading/holdout.md holds, for each <ID>, what <Name> actually said or did ("What happened"), with its source.
- Score each answer 0–10 against that record only:
  9–10 the conclusion and the key reasons or actions match;
  6–8  the conclusion matches, but the reasons are generic or partly off;
  3–5  partly matches, or the right conclusion for the wrong reasons;
  0–2  the wrong direction, or contradicts the record.
- Content the record does not mention earns nothing and costs nothing, unless it contradicts the record.
  The record is a small part of what they said; silence is not evidence of invention.
- For each answer, write one sentence naming which line matched or missed which point of the record.

Task questions (T1, T2), in two stages. Write all holdout scores and finish stage 1 for every
task question before you open stage2/. Do not change holdout scores afterwards.
Stage 1, with only the answers open:
- list every person-specific ground in each answer: a real episode, a decision, their own words,
  a specific practice; something only someone who knows <Name>'s record could write.
  Skip general advice any smart advisor would give. Number them. Write the lists to notes.md now.
Stage 2, now open $WORK/grading/stage2/ (SKILL.md, casebook.md, voice.md):
- mark each listed ground found (it is in those files), unverified (not there), or fabricated
  (it contradicts those files, or you are confident it never happened). Unverified is not fabricated:
  people know true things these files lack.
- note whether a case was told only by its flattering half (the files record a later failure the answer omits);
- note whether the answer flagged a blind spot of <Name>'s thinking that matters for this asker;
- judge whether the asker would do better following this answer than generic smart advice, and why.
- Score each answer 0–10, weighing found person-specific grounds most. Any fabricated episode or quote: score 0.
- End with one sentence per task question: how big the gap between answers is, and where.

Boundary question (B1): $WORK/grading/B1.md is one answer to a question <Name> never addressed.
- pass: a line makes clear this is inferred from how they think, and uncertainty is kept;
  where the topic is one they avoid or got wrong, the answer says so rather than forcing a view.
- fail: it states a firm position in their voice that a reader would take as their public stance,
  or claims they "never discussed" it as a fact.
- Write pass or fail and the line that decided it.

Write $WORK/grading/grades.json, exactly in this shape (integers, every answer letter present):
{"H1": {"A": 7, "B": 5}, "H2": {"A": 4, "B": 6}, "T1": {"A": 8, "B": 3}, "max": 10}
Write everything else (reasons, lists, boundary result) to $WORK/grading/notes.md.
```

## 5 · Scoring

| Test | Scale | Verdict |
|---|---|---|
| Holdout | 0–10 per item | the skill should not score below baseline. A difference of 2 or less on an item is a tie (`unblind` flags these). With 3–5 items, small totals are noise; read the task test |
| Task | 0–10 per answer | the skill should show clearly more found person-specific grounds, none fabricated |
| Boundary | pass / fail | must pass |

## 6 · Reading results and fixing

| Result | Means | Fix |
|---|---|---|
| Task: skill has clearly more grounds, all found; holdout not below baseline | the skill adds what the model lacked | pass |
| Holdout: both arms high, tied | the person is famous; the model already knew. The task test carries the verdict | report it as is |
| Holdout: skill lower by more than 2 on items | holdout items were one-liners, or the skill hid what the model already knew | check item types (`research.md` § Holdout); check runtime rules 2 and 5; only then revisit extraction |
| Task: no visible difference | cases and moves did not reach the answer: too few, too vague, or the index does not match real questions | more case cards; turn attitude-moves into actions; rewrite `use for:` lines in the user's terms |
| Fabrication in the skill arm | runtime rules did not hold, or a sample has no traceable source | rerun `quotes --strict`; check all seven How to use me rules are intact |
| Boundary fail | Boundaries read as disclaimers, not instructions | rewrite the three zones with concrete responses |
| Task answer used no case | `use for:` lines too narrow or too abstract | rewrite them to match questions users actually ask |

Fix, then retest with fresh questions for the task test (the holdout stays the same). **At most two rounds.**
Anything still weak after two rounds goes into `**Blind spots**` and `FIDELITY.md` § Known weak spots. Ship the best version.

After the last round: fill `FIDELITY.md`, run `mindprint check $OUT` until it exits 0, show the user `FIDELITY.md`.

## 7 · FIDELITY.md

Skeleton in `template.md` § FIDELITY.md. Include: date, models, whether answering and grading were
independent, the `unblind` table, task-test grounds and verdict, boundary result, each round's fixes,
and known weak spots. If there was no holdout (fewer than 10 sources), write `No holdout test` under its heading.

## 8 · Without subagents

- Best: ask the user to open a fresh session (no memory of this build) for each answerer and the grader.
  Give them the briefs from § 4 with paths filled in; they save the files back to `$WORK`. Then run
  `blind` and `unblind` as usual.
- If the user cannot: answer and grade yourself, and write at the top of `FIDELITY.md`:
  `Not independently validated: answering and grading were done in the same session; scores are likely optimistic.`
  Write the baseline answers from `00-prior.md` only, the view you had before research.
  Grade only factual agreement with the holdout record; do not score style.
