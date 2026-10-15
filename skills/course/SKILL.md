# Course

Creates and maintains a course: its `units.json` and its sources.
Use it when the learner wants a new course, hands over a curriculum or reading list, adds sources to a course, or wants its units re-cut.

This is not a session skill.
`skills/session/SKILL.md` runs studying and writes all the state studying produces.
This skill owns the structure that exists before that.

## What a course is

A course is a directory of units plus the material they share:

```
courses/<slug>/
  units.json     # THE course — header, units, concepts, structure, state
  bank.jsonl     # every question, generative only
  sources/       # PDFs, papers, notes
```

The course's prose lives in the `units.json` header.

A course has **no state**: no status, stage, tier, weight, cursor or progress.
All of those live on the unit, because the unit is the only thing that gets scheduled.
"How is this course going" is answered by the distribution of its units' stages, computed from `units.json`.

Two courses may reference the same unit.
For example, a databases course and an information retrieval course might both want Fagin's Threshold Algorithm.
This is one reason the unit, not the course, is the atom.

See `CLAUDE.md` for every field.
This file covers judgement, not format.

## Creating a course

1. **Write the `units.json` header**: `course`, `title`, `default_priority`, plus `sources` and `notes` (below). `sources` and `notes` are prose; nothing parses them.
2. **Cut the material into units** in the same file's `units` array.
3. **Check every reading against the vault.** Set `reading.status: "missing"` where the PDF is not actually present, and report the list. A course may exist as a plan before its material arrives; the tutor refuses to run those units instead of improvising. Never quietly generate questions for material you do not have.
4. **Leave `concepts` empty.** Concepts come from `skills/knowledge-map/SKILL.md`. Plans name readings and concepts name claims; guessing claims from a chapter title produces a course of what the book is *called* instead of what it says.
5. **Leave `srs`, `placed` and `cursor` alone.** Placement writes them in the first session that selects the unit.

If the learner hands over a curriculum document, turn its content directly into units.
`units.json` is the plan; a second human-owned copy would drift within a month.

## Cutting units to size

Unit size is the main judgement call in this skill, and mistakes in either direction are expensive.

**A unit takes one to four hours to cover every concept once.**
That is roughly a chapter, or part of one where the book is dense, and usually 6–20 concepts.
`check_vault.py` warns above 25 concepts and errors above 35.

This size makes the rest of the system work:

- Small enough that "study this unit" is a **session**, not a project. A unit no one can finish in a sitting never reaches `learned`, and the SRS never gets to work.
- Large enough that the **prerequisite graph over units stays coarse** enough to maintain by hand. With half-hour units, the edges outnumber the units.

Signs a unit is too big, from most to least common:

- More than ~25 concepts. The checker catches this one.
- The concept graph inside it is **heavily non-linear**. A unit's concept graph should be mostly a chain with a few branches; a wide graph means two subjects were merged.
- A long list of prerequisites. A unit that needs five other units usually contains material belonging to three of them.

Split a plan item into two units where the *material* has a seam, not where the hour count says so.
Do not split an 8-hour reading into eight units to hit a number; the `cursor` already makes it safe to stop mid-unit.

## Priority

`default_priority` in the header applies to every unit in the course, and a unit can override it with its own `priority`.
Priority is the only setting that decides what gets studied.

- **`0` mutes a unit**: it is never scheduled or sampled. Use this to park material that is correctly mapped but not wanted now. It beats deleting the unit, and the scheduler needs no special case for it.
- Set `default_priority` by how much the learner wants this course relative to others. It is compared across courses, so a background course should sit visibly lower.

Mute a whole course with `default_priority: 0`.
To shelve a course, move its directory into `courses/_archive/`; never delete it, because `sessions/` and other courses' units still reference its bank questions.

## What belongs in the header's `sources` and `notes`

These two fields are the course's only prose.
`skills/bank-generator/SKILL.md` reads them as live input.
They hold three things and nothing else:

1. **`sources`**: the bibliography, one entry per source, saying what each is *for*. Which book is the spine, which paper is the authoritative treatment, which notes are only a supplement.
2. **`notes`: scope**: the subtopics the sources cover, and what the course deliberately excludes. Scope is a **floor, not a ceiling** for generation: it says what must be covered, not what may be. Record exclusions explicitly, because an unrecorded "we're skipping this" gets re-argued every few months.
3. **`notes`: difficulty calibration**: where the course should lean toward derivation versus conceptual coverage, and which material the learner already knows well. `bank-generator` reads this as an instruction about *density*, never about inclusion.

`notes` also holds caveats with no other home: where granularity is intentionally coarse, what the bank does not reach, or a PDF whose formulas did not extract.

Priority, progress and state do not belong here; they are per-unit, in the `units` array.
Nothing machine-readable goes in either field.

## Notes

- Run `python3 scripts/check_vault.py` after any structural change. It validates unit ids, prereq resolution and acyclicity, concept kinds, claims and states, concept-prereq resolution and acyclicity, cursor targets, `questions` links, unit size, and `reading.status`. It checks only the *value* of `reading.status`, not whether the file is on disk, so verifying the reading is present is your job.
- Course slugs are lowercase-hyphenated and stable. They appear in unit ids and in cross-course prereqs written `<course>:<unit>`. Renaming one is a migration, not an edit.
- Question ids never change when material moves into a course. Sessions and units join on them.
- A concept id must be unique across the whole course and belong to exactly one unit; `check_vault.py` errors if two units claim the same one. When you re-cut units, re-check that assignment in the same pass.
