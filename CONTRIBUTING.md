# Contributing

## Set up

```bash
git clone https://github.com/cyruspastelero/mindprint.git
cd mindprint
python3 -I -m unittest discover -s tests -v
claude --plugin-dir "$PWD"      # load your working copy instead of the installed plugin
```

No dependencies. The CLI and tests use the Python standard library (3.9 or newer).

## What goes where

| Change | Where |
| --- | --- |
| A file format, heading or rule the CLI checks | `docs/SPEC.md` first, then `scripts/mindprint.py`, its tests, `references/template.md` and the example |
| How a step is done | `skills/mindprint/references/<step>.md` |
| When the agent should stop, ask or refuse | `skills/mindprint/SKILL.md` or `references/ethics.md` |
| A new check | `scripts/mindprint.py` plus a test named for the behaviour, e.g. `test_quote_missing_from_archive_fails` |
| A new example persona | `examples/<slug>-mind/`, built with mindprint, passing `check`, with `FIDELITY.md` filled in |

## Rules for example personas

- Every quote must be checkable: archive the source as plain text in `references/sources/`.
- Prefer people whose words are in the public domain, or sources you may redistribute.
- No living private individuals. See `skills/mindprint/references/ethics.md`.
- Report validation results as they came out, including the losses.

## Commits

Conventional commits (`feat:`, `fix:`, `docs:`, `test:`, `chore:`). One logical change per PR.
The PR description says why, and how you checked it.
