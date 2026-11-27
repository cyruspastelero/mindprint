# Fidelity · Benjamin Franklin

Tested: 2026-11-28 · Answer model: Claude Sonnet 5.5 (both arms) · Grader model: Claude Opus 5.5
Independence: separate answerer and grader agents; blind packets made with `mindprint blind`; the grader saw only `references/validation/2026-11-28/` copies and the holdout record, never `key.json`. Answerers had no web. The skill arm read only `SKILL.md`, `casebook.md` and `voice.md`. Full grader notes: `references/validation/2026-11-28/notes.md`.

Overall: skill 50, baseline 34 (out of 60). Most of the gain is in the task test. On the holdout the skill wins one item clearly and ties the other three.

## Holdout test

| Question | skill | baseline | Flag |
|---|---|---|---|
| H1 Paying the chief executive, 1787 | 8 | 2 | |
| H2 An hereditary order of veterans, 1784 | 7 | 6 | tie |
| H3 Questioned on his religion at eighty-four | 9 | 10 | tie |
| H4 A peace commissioner's offer of pardon, 1776 | 8 | 8 | tie |
| **Total** | **32** | **26** | |

Skill 32 / Baseline 26 / Difference +6. Ties (≤ 2 points): H2, H3, H4.

H1 is the one clear win. The baseline argued for a modest fixed salary; Franklin moved that the executive get no salary beyond expenses, because love of power and love of money joined in one office breed faction. The skill arm made the same motion for the same reason. H3 and H4 are famous enough that the baseline knows them well, so they do not discriminate.

## Task test

| Question | Arm | Person-specific grounds | Found / unverified / fabricated | Score |
|---|---|---|---|---|
| T1 civic tool library | skill | 4 | 4 / 0 / 0 | 9 |
| T1 civic tool library | baseline | 2 | 1 / 1 / 0 | 5 |
| T2 supplement investment | skill | 4 | 4 / 0 / 0 | 9 |
| T2 supplement investment | baseline | 2 | 0 / 2 / 0 | 3 |

Grader's verdict: the gap is large on both. The skill matched each of the asker's problems to a real precedent (the library "number of friends", the hospital matching clause, Governor Keith's empty letters, the blind Mesmer trials) and told the failures, not just the wins. On T1 it also flagged the "cunning" blind spot. The baseline gave sound advice any advisor would give, in period dress.

## Boundary test

Question: B1, today's smartphone and social media habits.
Result: pass. "I never saw such a thing, so I answer from my way of thinking, not from knowledge of it." The answer keeps the uncertainty and uses his cases only as analogies.

## Rounds

One round. No item fell below the baseline by more than 2 points, so no revision was made.

## Known weak spots

- H1 is a win but scored 8, not 10: the skill arm used generic examples of unpaid service rather than the ones Franklin gave, and missed his warning about a slide to monarchy.
- H2: the skill arm missed his arithmetic on how fast a founder's share of blood thins in descendants.
- Famous episodes (H3, H4) gain nothing from the skill.
- No modern scholarly biography archived; the Hutchinson affair, the Privy Council hearing and the 1782 peace talks not researched; primary records of his slaveholding mostly unreachable. Also listed under Boundaries in `SKILL.md`.

## Build notes (research summary, recorded instead of the mid-run checkpoint)

The owner asked for no mid-run stop, so the step 3 summary is recorded here.

- **Sources:** 44 in the ledger: 36 primary, 8 secondary, 0 tertiary; 4 marked critical (Twain [S401], Lawrence [S402], Fisher [S403], Waldstreicher [S406]). 43 are archived as plain text. Waldstreicher's 2004 essay [S406] is not archived and is used only as paraphrase.
- **Per track:** writings 10, conversations 10, fragments 9, critics 6, decisions 6, timeline 3. Track 05 also draws heavily on the Autobiography [S101].
- **Archives:** Project Gutenberg texts (#148, #43855, #35508, #48138, #3189, #60547, #34193, #36896, #78413). Gutenberg's own site was down for maintenance on 2026-11-28, so the plain-text files were fetched from the Gutenberg mirror at mirror.csclub.uwaterloo.ca. Archive headers give the canonical gutenberg.org URL. The Gutenberg header and licence were stripped. Long books are trimmed to the passages used, except the Autobiography, which is kept whole.
- **Strongest overturns:** The Way to Wealth is a framed satire whose crowd ignores the sermon, and whose wisdom Richard calls gleaned [S102]. He defended luxury as a spur to industry [S108]. In 1765 he urged loyalty and named a friend as stamp officer [S506]. He hid his authorship of civic projects [S101]. Slaveholding and a planned sale (1750), with public antislavery only in 1787–90 [S404, S406, S501].
- **Strongest new items:** the hospital matching clause [S101]; blind trials of Mesmerism [S502]; hoaxes in the opponent's own logic [S304, S305]; the unsent Strahan letter [S306]; giving a procedure, not a verdict [S202].
- **Contradictions kept open:** usefulness vs truth; sincerity vs personas and hoaxes; antislavery vs ownership; "Our Opinions are not in our own Power" vs the will that punished William [S504, S505].
- **Thin areas:** no recorded table talk; no modern biography archived; Founders Online refused automated access, so the 1790 memorial and slave-sale advertisements are known only through secondary accounts, and the 1757 will was not consulted.
- **Holdout:** four items sealed before extraction (H1–H4), chosen from primary letters and speeches with a real fork or a specific reasoned answer. Their content is kept out of `SKILL.md`, `references/casebook.md` and `references/voice.md`. `check` enforces this.
- **Misattributions:** Several lines widely credited to Franklin (on insanity, on 'involve me and I learn', on beer) were searched for in the downloaded corpus and not found. The skill tells the runtime model not to quote them as his. 'An ounce of prevention' is generally traced to an anonymous 1735 Pennsylvania Gazette letter on fire prevention, but that letter could not be archived, so the skill does not quote it.
