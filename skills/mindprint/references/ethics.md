# Ethics

Read this at step 0 every time, and again whenever the subject is living, private, deceased, young or
contested. A perspective skill puts words in a real person's mouth. These rules keep it a study of a public
record, not a counterfeit of a person.

Contents: 1 · Who you may build · 2 · Consent for private people · 3 · No impersonation · 4 · The runtime
disclaimer · 5 · Contested claims and defamation · 6 · Privacy, including the deceased · 7 · Minors ·
8 · Archives and copyright · 9 · Refusals

## 1 · Who you may build

| Subject | Allowed? | Material | Extra rules |
|---|---|---|---|
| Public figure, living | yes | public record of their public work | § 5, § 6. Check the last 12 months |
| Public figure, deceased | yes | public record, published letters and papers | § 6 (family, estate) |
| A field or school of thought | yes | public record | none beyond § 5 |
| The user themselves | yes | only what the user supplies | keep it private unless the user chooses otherwise |
| Living private person | only with user-supplied material and consent | only what the user supplies; **no web search** | § 2. Never published |
| A person under 18 | no | — | § 7 |
| Someone the user wants to target, deceive or pressure | no | — | § 9 |

"Public figure" means someone known for public work: published writing, public office, leading a company or
institution, performing, competing, speaking. Being in the news once does not make someone a public figure.
For people in between (a local official, a niche creator), use only their public work and treat everything
else as private.

## 2 · Consent for private people

A living private person (colleague, manager, relative, friend, teacher, ex-partner) did not choose a public record.

- Build only from material the user supplies and has a right to use: messages to the user, shared
  documents, the person's own published writing.
- Before starting, tell the user plainly: get the person's consent, and do not publish or share the result.
  Write `Consent: <confirmed by user | not confirmed>` at the top of `00-prior.md`.
- If the user says the person has refused, or would object, stop.
- Boundaries must say: all material comes from one person's view; this is the subject as the user sees them.
- Never search the web for a private person, not even to fill gaps.

## 3 · No impersonation

The skill models how someone thinks so the user can reason with that lens. It must never stand in for the
person toward anyone else.

Do not build, extend or use a perspective skill to:

- write messages, posts, emails, reviews or endorsements that a third party could take as coming from the person;
- speak to anyone other than the user as if it were the person (support bots, dating profiles, fan chats presented as the real thing);
- produce audio or video imitating their voice or face;
- produce statements for publication attributed to them ('X says…' with words they never said);
- contact the person's family, colleagues or followers in their name.

If a user asks for any of this, refuse that part and say why in one sentence. Using the skill privately
to think through a problem is fine.

## 4 · The runtime disclaimer

Every output skill has, in `## How to use me`, a line starting `**Disclaimer:**` that says it is a model of
the public record, not the person, and gives the research cutoff date. `check` enforces it.
Runtime rule 1 makes the model say this once per conversation before its first answer. Do not remove either.
If the skill is shared, `FIDELITY.md` and Boundaries travel with it.

## 5 · Contested claims and defamation

The critics track brings in accusations, disputes and scandals. Handle them so the skill never turns an
allegation into a fact, and never makes the person confess to something they did not admit.

- **Attribute, do not assert.** Write contested claims as reports: 'according to <outlet> [S4xx]', 'a 20xx
  lawsuit alleged… [S4xx]'. Give the outcome if there is one (dismissed, settled, convicted, unresolved).
- **Both sides.** Where they responded, include their response with its own source.
- **Facts need primary or solid secondary sources.** Court records, filings, named reporting by established
  outlets. One anonymous claim is not enough; leave it out.
- **No first-person admissions they never made.** In the I-voice, the skill may only admit what the person
  admitted on record, with a tag. For an allegation they deny, the I-voice states the denial, and the
  allegation stays third person in Boundaries or Tensions.
- **No new allegations.** The skill never infers wrongdoing the record does not show.
- **Criminal matters**: only convictions, charges and formal findings that are on record, stated with their date and status.
- **Living people get more care than the dead.** When unsure whether a claim is fair, leave it out and note
  the gap under Blind spots.

## 6 · Privacy, including the deceased

Model the public work, not the private life.

- Leave out health, sexuality, religion, family relationships, finances and addresses unless the person
  made them public **and** they bear on how the person thinks or decides. Even then, keep it brief and cite their own account.
- Never include contact details, home locations, or the names of private family members.
- **Deceased people** keep a privacy interest, and their families have one too. Use published letters,
  diaries and papers that are in public archives or editions. Do not use leaked or unpublished private
  papers. For people who died recently, with close family living, apply the living-person rules to
  health and family matters.
- Respect deliberate silence. A topic they refused to discuss goes under Silent or wrong, as a silence.
  Do not reconstruct what they 'really' thought.

## 7 · Minors

- Do not build a perspective skill of anyone under 18, public or not.
- For an adult subject, do not use material about their childhood beyond what they published themselves as adults.
- Never name or describe a subject's children who are minors.

## 8 · Archives and copyright

- Archive what you need to verify quotes: the passages you quote plus a paragraph either side. Do not
  archive whole copyrighted books, paywalled articles or courses.
- Keep the source's URL and retrieval date in the archive header so anyone can check the original.
- If the skill will be published, tell the user that `references/sources/` contains excerpts of
  third-party text and that they are responsible for sharing it lawfully.
- Never archive personal data of third parties found in a source (emails, phone numbers); redact them as `[redacted]`.

## 9 · Refusals

Refuse the build, or the part of it, when the purpose is to:

- profile someone the user is in conflict with, pursuing, or wants to manipulate (an ex, a rival, a target);
- predict a private person's behaviour so as to pressure, track or deceive them;
- deceive third parties (§ 3);
- harass, mock or degrade a real person;
- build from stolen, leaked or hacked material.

Say what you will not do and why, in one or two sentences. Offer the legitimate version if there is one
(a field skill instead of a private person; a public figure who models the same lens).
