# Research

Read this for steps 2 and 3. Two goals only: get enough primary material, and find what differs from the prior.

Contents: 1 · Before you start · 2 · The six tracks · 3 · Source ledger and ID ranges · 4 · Source tiers ·
5 · Archiving · 6 · Subagent brief · 7 · Transcripts, books, other languages · 8 · Holdout · 9 · Serial fallback ·
10 · When things go wrong

## 1 · Before you start

**User material first.** Put each item the user supplied in `$OUT/references/sources/` as plain text
(`S01.txt`, `S02.txt` …; IDs `S01`–`S99` are for user material). Log each in the ledger. Note which tracks
it feeds (one book can feed writings, conversations and fragments). Search the web only for tracks it leaves empty.
If the user says "only use what I gave you", or the subject is a private person, do not search the web at all.
In track files, mark items `(user material)` or `(web)`.

| Material | How to use it | Feeds |
|---|---|---|
| Book or long PDF | core arguments; passages where they tell their own story | writings, decisions, fragments |
| Talk or interview transcript, subtitles | how they answer, unscripted reactions | conversations, fragments |
| Blog or newsletter export | ideas that recur | writings, fragments |
| Social media export | short-form voice | fragments |
| Internal memos, documents | decision logic | decisions |
| The user's own notes | secondary cross-check | depends |

**Tools.** Check what the host offers beyond plain search: full-page readers, PDF readers, transcript or
subtitle tools, multi-site fetchers. Tell each track agent what it may use. Plain search and page fetch are enough.

**Tier.** Quick: tracks 01, 02 and 05, ~5 sources each. No conversations on record (most people before
recorded interviews)? Delete `02-conversations.md`; `status` does not need it in the quick tier.
Quick still needs one critical source (below), but no critics track file: log it in the ledger with
`"track": "critics"` and `"critical": true`, and summarise it in `05-decisions.md` or `01-writings.md`.
Standard: all six. Deep: all six, more sources, fuller archives (`scoping.md` § Tiers).

## 2 · The six tracks

| # | Track (`track` value) | Look for | Pull out | File |
|---|---|---|---|---|
| 1 | writings | books, long essays, papers, newsletters | arguments that recur 3+ times, coined terms, books they recommend | `01-writings.md` |
| 2 | conversations | podcasts, long video interviews, Q&A, depositions | how they answer when pushed, improvised analogies, mid-answer corrections, questions they refuse | `02-conversations.md` |
| 3 | fragments | posts, short pieces, open letters, speeches | frequent words and sentence shapes, contested statements, humour, how they argue | `03-fragments.md` |
| 4 | critics | biographies, reviews, peers, critics, opponents | patterns outsiders see, the main criticisms and disputes, how they differ from peers | `04-critics.md` |
| 5 | decisions | major decisions, turns, controversial acts | the situation and options, what they did, what they said after, gaps between word and deed | `05-decisions.md` |
| 6 | timeline | start of career to now | key dates, shifts in thinking, the last 12 months (living people) | `06-timeline.md` |

Track 5 is worth the most and is the easiest to do shallowly. It needs past-tense stories: year, situation,
what they actually did, what followed, and their own explanation in their words where it exists.

Track 4 is what keeps the portrait from being fan fiction. `status` fails without enough critical sources
(≥ 1; standard and deep ≥ 2), marked `"critical": true` in the ledger. In the quick tier there is no
`04-critics.md`: see § 1 · Tier.

## 3 · Source ledger and ID ranges

One JSON object per line in `$OUT/references/sources.jsonl`:

```json
{"id": "S501", "title": "<title>", "by": "<author or outlet>", "date": "YYYY-MM", "url": "https://<url>", "track": "decisions", "tier": "primary", "critical": false, "archive": "sources/S501.txt"}
```

| Field | Rule |
|---|---|
| `id` | `S` + 2–3 digits, unique |
| `title`, `by` | title required; author or outlet |
| `date` | `YYYY`, `YYYY-MM`, `YYYY-MM-DD`, or `""` if unknown |
| `url` | `""` only for user-supplied files |
| `track` | `writings`, `conversations`, `fragments`, `critics`, `decisions` or `timeline` |
| `tier` | `primary`, `secondary` or `tertiary` (§ 4) |
| `critical` | `true` if the source criticises or disputes them |
| `archive` | path relative to `references/`, e.g. `sources/S501.txt`, or `""` |

Two habits keep parallel agents from colliding:

- **Each track has its own ID range.** User material `S01`–`S99`; writings `S101`–`S199`; conversations
  `S201`–`S299`; fragments `S301`–`S399`; critics `S401`–`S499`; decisions `S501`–`S599`; timeline `S601`–`S699`.
- **Append one whole line per write.** Never rewrite the file from a track agent.

If two tracks log the same source, the orchestrator keeps the lower ID, rewrites the other track's tags,
and deletes the duplicate line. Then run `mindprint status $OUT`.

## 4 · Source tiers

Tiers work the same in any language. Judge the source by how close it is to the person, not by where it is hosted.

| Tier | What counts | Use |
|---|---|---|
| `primary` | their own words or acts, first-hand: books and essays they wrote, their posts and letters, full transcripts or recordings of them speaking, their filings, court testimony, minutes, code, user-supplied material by them | the backbone. ≥ 50% of the ledger (`status` checks; see below for one-work subjects) |
| `secondary` | reporting, biographies, other people's interviews and memoirs, reviews, academic studies, a journalist's account of an event they witnessed | context, critics, events they never wrote about. Cross-check against primary where possible |
| `tertiary` | summaries, encyclopedias, wikis, quote collections | leads only. Follow them to the primary source and cite that |

**Never counts as a source** (do not log, do not cite, do not quote from):

- quote-aggregator sites and quote image cards;
- AI-generated summaries, answers or "biographies", including search-engine AI overviews;
- uncited listicles ("10 lessons from…"), content farms, SEO rewrites, re-uploads of someone else's video by an unrelated channel;
- anonymous posts claiming inside knowledge, unless a named outlet reported and verified them.

**Wikipedia and other wikis**: use them as a map to find primary sources and dates. Never cite them.
If a tertiary source slipped into the ledger, it may not back any `[Sxx]` tag in the skill.

**One main work** (a subject known for one book, one paper or one set of notes): log a long work as
separate sources only for parts published or written separately, such as separate letters, essays or
notes with distinct dates. Otherwise it is one source. If the primary share is then below 50% because
little else of theirs survives, run `mindprint status $OUT --allow-low-primary "<reason>"`: the FAIL
becomes a WARN that prints the reason. Repeat the reason in Boundaries (`**Blind spots**`).

**Weighting inside primary**: a full transcript beats an edited excerpt; an original recording beats a
transcript someone else made; their own account of a decision beats a later retelling, but record both
when they differ.

## 5 · Archiving

A quote counts only if its source is archived. `mindprint quotes $OUT --strict` checks each quote against
the archive after normalising case, quote marks, dashes, whitespace and punctuation. Unarchived quotes WARN,
and `--strict` turns that into FAIL.

- Save plain text to `references/sources/<id>.txt` and set `"archive": "sources/<id>.txt"` in the ledger.
- Start the file with three lines: `# <id> · <title>`, `URL: <url>`, `Retrieved: YYYY-MM-DD`. Then the text.
- Strip navigation, ads and comments. Keep the words exactly as published, including their typos.
- For a long copyrighted work (a book), archive only the passages you use plus a paragraph either side, not the whole work.
- No archive possible (paywall, audio with no transcript)? You may still cite the source for a claim, but
  write any of their words as paraphrase without quote marks.
- Before writing a quote anywhere, find it in the archive. If it is not there, it is not a quote.

## 6 · Subagent brief

Use this for each track. Replace the angle-bracket parts. This example is track 5; for others change
"What to find", the file name and the ID range.

```
Your task: research <Full Name>'s major decisions and actual actions.

First read $OUT/references/research/00-prior.md. It is what we believed before research.
Your job is to find what differs from it.

What to find:
- major decisions, turning points and controversial acts across their career;
- for each: the year, the situation and options, what they actually did, what followed,
  and how they explained it afterwards (their own words where they exist);
- places where what they said and what they did diverge;
- failures, regrets and reversals, as much as successes.

Rules:
- Write to $OUT/references/research/05-decisions.md as you go, not at the end.
- Log each source as one appended line in $OUT/references/sources.jsonl. Your IDs: S501–S599.
  Fields: id, title, by, date, url, track ("decisions"), tier, critical, archive.
- Tier honestly: primary = their own words or acts first-hand; secondary = others' reporting;
  tertiary = summaries and wikis (leads only, never cite).
- Never use quote-aggregator sites, AI-generated summaries, uncited listicles or content farms.
  Wikipedia is a map to primary sources, never a citation.
- For any source you might quote, save its text to $OUT/references/sources/<id>.txt
  (header: "# <id> · <title>", "URL: <url>", "Retrieved: <date>") and set "archive".
- Put words in quote marks only if they appear verbatim in an archived file. Otherwise paraphrase.
- Tag every item with its source, e.g. [S503], and label it: said / did / others said / I infer.
- Tell what they did as past-tense stories. Do not reduce them to attitudes.
- When accounts conflict, record both side by side. Do not reconcile them.
- Do not write a conclusion or summary of the person.
- End the file with "## Gaps" (what you could not find) and then "## Differs from prior",
  each item starting [overturn], [deepen] or [new], with a tag.

Stop after about <N> sources, or when several searches in a row turn up nothing new.
```

Give each agent the tools it may use (§ 1). Do not give it the other tracks' files: independent tracks find more.

## 7 · Transcripts, books, other languages

- **Long interviews on video** are among the best primary material. Use the host's transcript tool if there
  is one, or a subtitle downloader such as `yt-dlp` with `--skip-download --write-subs`. Prefer human-made
  subtitles over auto-generated ones; mark auto-generated archives `(auto transcript)` in the ledger title,
  because their words may be wrong. Strip timestamps and repeated lines before archiving.
- **Local video with no transcript**: use the host's transcription ability, or ask the user for a transcript.
- **Books**: use the user's copy or a legal public source. Without the book, use the author's published
  chapters, talks and long reviews, and say so in the track file.
- **Non-English subjects**: research in their language first; their own words are primary in any language.
  Archive the original text. In the skill, quote the original with an English gloss outside the quote marks,
  or quote a published translation, archived and cited as its own source with the translator in `by`.
  Never quote your own translation as their words.

## 8 · Holdout

After all tracks are done and before extraction, pick 3–5 items from primary sources and write them to
`research/holdout.md` (format in `template.md` § holdout.md).

Pick, in this order:

1. **A decision at a fork**: they had other options; what they did and why. Question form: "You face X. What do you do, and why?"
2. **A reasoned answer** to a specific question: a paragraph of argument, not a sentence.

Each item must pass two tests: someone who has read them closely would likely get it right; a smart person
who has not would likely get it wrong or vague. Spread items across topics; one source each; findable in the archive.

Do not pick:

- **one-liners or slogans**: they test memory, not thinking. A skill that captures how they think can lose to plain recall on these;
- **famous events**: the model already knows them, both arms score full marks, nothing is learned. The more famous the person, the more you pick small judgements from long interviews;
- **open questions** any answer fits ("what matters most in a founder?").

From now on these items are test material, not evidence. Their content stays out of `SKILL.md`,
`casebook.md` and `voice.md`; `check` fails on any 8-word overlap with a `What happened` line.
Items stay sealed after validation so future updates can be re-tested.

Fewer than 10 sources in the ledger: skip the holdout. `status` WARNs "no holdout test"; repeat that at delivery.

Until you seal it, `holdout.md` is the `init` placeholder and `status` WARNs "not sealed yet". A partly
filled or malformed holdout FAILs `status`. `check` FAILs on an unsealed holdout once the ledger has ≥ 10 sources.

## 9 · Serial fallback and limits

| Situation | Do this |
|---|---|
| No subagents, or background tasks hang | Run the six tracks in series. Finish a track, save its file and ledger lines, then start the next. Never wait for a notification |
| Context too small (a full build reads several hundred thousand tokens) | Split into sessions: scope → research / holdout → extract / write → validate. Each session starts by reading the files on disk |
| Search tool missing | Use any equivalent (page fetch, browser). With none, switch to user material and ask for it |
| User stops midway | The files on disk are the deliverable so far. The next session resumes from them |

## 10 · When things go wrong

| Problem | Do this |
|---|---|
| A track finds nothing useful after a reasonable search | Move on. Mark it thin in the track's `## Gaps`; it goes into Boundaries |
| Fewer than 10 usable sources | Tell the user now. Fewer models (2–3), longer Boundaries, no holdout |
| Tracks contradict each other | Keep both. It is signal; it becomes a Tension |
| `status` says too few `Differs from prior` items | You are restating common knowledge. Go to full transcripts, early writing, first-hand accounts, critics |
| `status` says primary share < 50% | Replace secondary retellings with the original they retell. One main work: § 4 |
| A quote cannot be traced to an original | Do not use it, not even as paraphrase of something they "said" |
