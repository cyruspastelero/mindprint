# Scoping

Read this at step 0. It turns a request into a subject, a tier and a folder, and covers the cases where
the normal flow needs changes.

Contents: 1 · The four questions · 2 · Tiers and cost · 3 · Vague requests · 4 · Special cases ·
5 · Limited environments

## 1 · The four questions

| Question | Options | Default if the user does not say |
|---|---|---|
| Who, or which field? | a person; a field (`--topic`) | must be given or found via § 3 |
| Focus? | whole person; one side (e.g. their investing, their teaching) | whole person |
| Use? | thinking advisor; decision aid; learning their method | thinking advisor |
| Primary material on hand? | books, transcripts, subtitles, blog or social exports, memos | none |

Ask only what you cannot default. If the user says "just do X", state the defaults in one line and start.

Then:

1. Read `ethics.md` § Who you may build. Refuse or narrow the request if it says to.
2. Pick the slug: lowercase ASCII, hyphens, the name people search for (`jane-doe`). Folder: `<slug>-mind`,
   or `<slug>-field` for a field.
3. If `<slug>-mind` already exists in the host's skills folder, this is an update or upgrade (`SKILL.md` § Update and upgrade).
4. Put user material in `$OUT/references/sources/` after `init`, one plain-text file per source (see `research.md` § Archiving).

## 2 · Tiers and cost

A full build is a long, multi-agent job. State the tiers before starting and let the user choose.
The numbers are planning guides, not limits. Cost scales mostly with how much text agents read.

| | Quick | Standard (default) | Deep |
|---|---|---|---|
| Tracks | 3: writings, conversations, decisions | all 6 | all 6, heavy tracks split in two |
| Sources | ~5 per track, ~15 total | ~8–12 per track, ~50–70 total | ~15–25 per track, 100+ total |
| Archived primary text | quoted passages only | quoted passages and key transcripts | full transcripts, long essays, key chapters |
| Case cards | ≥ 6 | ≥ 12 | ≥ 20 |
| Agent calls | ~3 research + 3 validation | ~6 research + 3 validation, + up to 2 fix rounds | ~8–12 research + 4 validation (2 graders), + fix rounds |
| Relative cost | about 1× | about 3× | about 6–10× |
| Good for | a first look, obscure people, tight budgets | most uses | a skill you will publish |

Say plainly: a standard build can pass several hundred thousand tokens of reading across all agents.
On a top-tier model that is real money; the user should know before it starts.

Ways to cut cost without cutting quality much:

- Run research agents on a cheaper model; keep extraction, writing and grading on the strongest one.
- Start quick; upgrade to standard later. Research files carry over.
- Supply primary material yourself: one good transcript replaces many searches.

Tell the user what you chose in one line, e.g. `Standard tier: 6 tracks, ~60 sources, ~9 agent calls. Reply "quick" to cut it to about a third.`

## 3 · Vague requests

The user has a need but no name ("I need a thinking advisor", "I keep making bad calls"). Work back from
the need to a subject.

**Locate the need.** At most two rounds of questions, only to tell similar needs apart (business decisions or
life decisions?). If the need is already clear, skip to candidates.

| Need | Typical words | Lenses that fit |
|---|---|---|
| Decisions under uncertainty | "I overthink", "I pick wrong" | inversion, base rates, probabilistic thinking |
| Explaining and writing | "people don't get my point" | plain-language teaching, story, analogy |
| Building a business | "can't find product–market fit" | first principles, leverage, focus |
| Teaching | "students tune out" | known-to-unknown, worked examples |
| Critical thinking | "I get fooled" | falsification, incentives, bias spotting |
| Making content | "no one watches" | attention design, test-and-iterate |
| Career and life strategy | "no direction", "no time" | compounding, optionality, saying no |
| Risk | "I'm too cautious / too reckless" | convexity, tail risk, redundancy |
| Product and design | "it does too much" | subtraction, constraints, user mental models |
| Humour and delivery | "I'm too dry" | contrast, broken expectations, self-mockery |

**Person or field?** A specific way of thinking → person skill. A domain's method across many people → field skill.
Unsure → offer one of each.

**Look locally first.** List existing `*-mind` and `*-field` skills in the host's skills folder; read their
descriptions. An existing skill that fits costs nothing.

**Offer 2–3 candidates**, different from each other, in this shape:

```
### 1 · <name or field>   (installed | needs building, <tier>)
Lens: <the one way they see problems, in a sentence>
Why it fits you: <tie it to what the user said>
Limits: <what this lens cannot help with>
```

Never more than three. Always state limits. Name the specific model or move that matches the need,
not "they are brilliant".

After the choice: installed → use it, done. New → step 0. None fit → one more round, or ask the user for a name.

## 4 · Special cases

### A field, not a person (`--topic`)

| Step | Person skill | Field skill |
|---|---|---|
| Scope | who, which side | where the field's edges are, who it is for (one school or all?) |
| Prior | what you believe about them | the field's mainstream claims and what you think is consensus |
| Research | six tracks around one person | first name 3–5 central figures or schools, then 1–2 tracks each |
| Extraction | one person's moves and models | **consensus** (all schools agree) and **disputes** (A says X, B says Y); cases per school |
| Voice | one person | neutral and expert; a glossary plus passages from the main figures |
| Tensions | inner contradictions | fundamental disputes between schools |
| Writing | first person | third person; `template.md` § Field variant |
| Holdout | the person's own decisions | well-documented cases in the field and how they turned out |

### Yourself ("distill me")

1. Everything comes from the user: writing, recordings, decision memos, chat exports, a self-description. No web search.
2. The prior snapshot becomes the user's own note: how I think I think.
3. The six tracks analyse the material, not the web.
4. Watch for self-image bias. Where what they **did** differs from what they **say** about themselves, record it.
   If they can, ask one or two people who know them for a short paragraph each; that is the critics track.
5. Holdout items are past decisions of theirs. Validation asks: what would you have chosen then?

### A living private person (colleague, relative, teacher, friend)

Read `ethics.md` first. Then:

- Only user-supplied material. No web search.
- Before starting, tell the user: get the person's consent, and do not publish the result.
- The material is usually chats, email and documents. These show how someone works better than public material: focus on moves and heuristics.
- Boundaries must say: all material comes from one person's view; this is them as the user sees them.

### An obscure person (fewer than 10 usable sources)

1. Tell the user at scoping: public information is thin and quality will be limited.
2. Ask for primary material (books, recordings, letters). Prefer it over web results.
3. Cut mental models to 2–3, each marked "based on limited sources".
4. Make Boundaries longer: say which tracks were thin.
5. Skip the holdout; `status` will WARN "no holdout test". Say so in `FIDELITY.md` and at delivery.

## 5 · Limited environments

| Limit | What to do |
|---|---|
| No subagents, or background tasks hang | Research in series: one track, save, next. Validation: `validation.md` § Without subagents |
| Context around 200k tokens | Three sessions: scope → research / holdout → extract / write → validate. Each starts by reading the files on disk. Prefer quick tier |
| No web | Local-material mode only; ask the user for sources |
| Tight budget | Quick tier; cheaper model for research; strongest model for extraction and grading |
