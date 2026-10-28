## Summary

<!-- What changes and why. Link the issue (for example "Closes #12"). -->

## Type of change

- [ ] Bug fix
- [ ] Guidance improvement
- [ ] New Laravel version or data refresh
- [ ] Feature
- [ ] Tooling or CI
- [ ] Documentation only

## Official sources

<!-- For every claim about Laravel, PHP or Composer behavior: official URL plus commit or tag. Write "n/a" if none. -->

## Checklist

- [ ] `python3 -I skills/laravel-upgrade/scripts/check.py` passes. CI also runs it on Python 3.9 and the latest Python.
- [ ] The safety invariants in `AGENTS.md` are unchanged, or the change is called out and justified above.
- [ ] No hand edits under `references/official/`. New snapshots were added with `tools/add_snapshot.py`, and `tools/verify_sources.py` passes.
- [ ] Scripts stay Python 3.9+ standard library, with no network access in `inventory.py` or `check.py`. Behavior changes have `check.py` fixtures.
- [ ] Related documents are updated together: `SKILL.md` files, `references/`, `README.md`, `skills/laravel-upgrade/README.md`.
- [ ] `CHANGELOG.md` has an entry under Unreleased.
- [ ] No secrets, personal paths, real project names or client data.
