# CLAUDE.md

## First-time setup

If skills are not yet installed (check with `make list`), prompt the user to run:

```bash
make install
```

Ask if they have existing skills they'd like to import into this repo using `/import-skill`.

## When adding a new skill

After creating a new skill in `skills/<name>/SKILL.md`:

1. Update `README.md` — add the skill to the Skills table (keep alphabetical order)
2. Run `make install` to symlink it
3. Commit both the skill and the README update together
