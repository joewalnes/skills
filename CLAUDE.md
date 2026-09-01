# CLAUDE.md

## First-time setup

If skills are not yet installed (check with `make list`), prompt the user to run:

```bash
make install
```

Ask if they have existing skills they'd like to import into this repo using `/import-skill`.

## Bug tracking

Bugs and tasks are tracked in `TODO.md`. Use `/todo` to add entries and `/bug-bash` to work through them.

## Engineering diary

Maintain `DIARY.md` — add an entry when making significant changes, architectural decisions, or non-obvious tradeoffs. Latest entries at top. Write in narrative form, not bullet dumps. Focus on *why* and *context*, not *what* (that's in the commits).

## Code quality

Run `/scorecard` periodically — after completing a feature, before major PRs, or when onboarding to assess health. Address critical findings before moving on.

## Commits

Break work into small atomic commits — one logical change per commit. Don't bundle unrelated changes. A bug fix, a new feature, and a refactor are three commits, not one.

## Documentation

Update `README.md` (and any relevant docs) before committing if the change affects:
- Public API, CLI interface, or configuration
- Setup/installation steps
- Feature behavior visible to users

## When adding a new skill

After creating a new skill in `skills/<name>/SKILL.md`:

1. Update `README.md` — add the skill to the Skills table (keep alphabetical order)
2. Run `make install` to symlink it
3. Commit both the skill and the README update together

### Scripts

When a skill needs a helper script (not a one-off command in a Bash tool call), write it in **Python or Perl, not bash**. Both are always installed; bash is not portable — macOS ships `/bin/bash` 3.2 (no associative arrays, various POSIX-only gaps), which has caused real bugs (a `declare -A` skill script silently failed on this exact machine). Reserve bash for short inline commands, not committed script files.

### Skill frontmatter

Every SKILL.md must have `name` and `description`. Add `argument-hint` if the skill accepts arguments — it shows in autocomplete.

`allowed-tools` is optional and **enforced** — it restricts which tools Claude can use without asking permission while the skill is active. Use it for read-only or limited-scope skills (e.g. sitrep). Omit it to use normal permission settings.

Don't use `user_invocable: true` — it's the default. Only use `user_invocable: false` for background-knowledge skills that shouldn't appear in the `/` menu.

## Evolving preferences

When the user expresses a coding preference, convention, or correction during a session, offer to encode it into this CLAUDE.md file so it persists across sessions. Examples: naming conventions, preferred libraries, architecture patterns, things to avoid.

## Mistake retrospectives

When you make a mistake (especially forgetting something the user asked for):
1. Acknowledge it directly
2. Identify the root cause — why did this happen? (e.g. no checklist, unclear convention, missing rule)
3. Suggest a concrete project change to prevent recurrence (add a rule to CLAUDE.md, add a pre-commit check, create a checklist in the relevant skill)
Don't just apologize — fix the system.
