---
name: import-skill
description: Discover and import Claude Code skills into this shared repo
argument-hint: [skill name, path, or "browse"]
---

# Import Skill

Discover existing Claude Code skills from your machine and import them into this shared skills repository.

## How to Invoke

```
/import-skill                        # browse all discoverable skills
/import-skill browse                 # same — show what's available
/import-skill my-cool-skill          # import a specific skill by name
/import-skill ~/project/.claude/skills/refactor   # import from explicit path
```

## Discovery

When invoked with no argument or `browse`, scan all discovery sources and present a table of importable skills.

### Discovery Sources

Scan these locations. This repo lives at the path of the current working directory — its parent directory is the base directory where sibling projects are checked out.

1. **Global skills** — `~/.claude/skills/*/SKILL.md` (skip any that are symlinks pointing back into this repo)
2. **Sibling project skills** — `../*/.claude/skills/*/SKILL.md` (every directory alongside this one that contains a `.claude/skills/` dir)
3. **Sibling project commands** — `../*/.claude/commands/*.md` (older command format, still importable)

When scanning sibling directories, skip `node_modules`, `.git`, `build`, `dist`, and other common non-project directories.

For each discovered skill, extract:
- **Name** — directory name (or filename without `.md` for commands)
- **Description** — from frontmatter `description:` field
- **Source** — which project/location it came from (show relative path like `../backend`)
- **Status** — whether this repo already has a skill with the same name

### Browse Output

Present a table like:

```
Found 5 importable skills (excluding 3 already in this repo):

  Name            Source                    Description
  ─────────────   ───────────────────────   ──────────────────────────────────
  deploy          ../backend                Run deployment pipeline with checks
  lint-fix        ../frontend               Auto-fix lint errors and commit
  db-migrate      ~/.claude/skills          Generate and run DB migrations
  review-pr       ../backend                Review a PR with structured feedback
  test-plan       ../api-service            Generate test plan from requirements

Already in this repo: deploy (different version), hello-world, sitrep

Import one?
```

Skip skills that are identical to ones already in this repo. Flag skills with the same name but different content as "(different version)".

## Import Process

### Step 1: Resolve Source

If the user specified a skill by name or picked one from browse:
1. If it's a path, look for `SKILL.md` inside it (or treat it as a direct file path)
2. If it's a name, search the discovery sources above
3. Read the source SKILL.md
4. Show the user: name, description, source location, and line count
5. If a skill with the same name exists in `skills/`, show a diff summary and ask: rename, overwrite, or skip?

### Step 2: Review for Portability

Check the skill for things that won't transfer to a shared/global context:
- **Hardcoded paths** — Absolute paths to the source project
- **Project-specific references** — References to specific repos, file structures, or tooling unique to the source
- **Local tool assumptions** — Assuming specific CLIs, languages, or frameworks are available

Present a brief summary of what the skill does and any portability issues. Ask the user to confirm before proceeding.

### Step 3: Create the Skill

1. Create `skills/<name>/SKILL.md` with the (possibly adapted) content
2. Validate frontmatter has at minimum: `name`, `description`
3. Ensure the SKILL.md has:
   - A top-level heading matching the skill's purpose
   - A "How to Invoke" section with examples
   - `---` separators between major sections

### Step 4: Install and Confirm

1. Run `make install` to symlink the new skill
2. Update `README.md` — add the skill to the Skills table (alphabetical order)
3. Tell the user:
   - Where the skill was created
   - What changes were made (if any)
   - That it's now available as `/skill-name`
   - Remind them to commit when ready

## Guidelines

- **Don't over-edit.** Import the skill, don't rewrite it. Only change what's necessary for portability.
- **Preserve intent.** If the skill was written for a specific workflow, keep that workflow intact.
- **Flag, don't fix.** If something looks project-specific but you're not sure, flag it for the user rather than silently changing it.
- **One at a time.** If the user wants to import multiple skills, confirm each individually.
- **Skip symlinks back to this repo.** Global skills that are already symlinks into this repo's `skills/` directory should be excluded from discovery — they're already here.
