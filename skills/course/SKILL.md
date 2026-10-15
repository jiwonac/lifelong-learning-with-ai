# Course

Creates and maintains a course: its `units.json` and its sources.
Use it when the learner wants a new course, hands over a curriculum or reading list, adds sources to a course, or wants its units re-cut.
It is not a session skill; `skills/session/SKILL.md` writes all the state studying produces.

The layout, every field, and the fact that a course has no state of its own are in CLAUDE.md ("Layout" and "Data model").
This file covers judgement, not format.

## Creating a course

1. **Write the `units.json` header** (fields in CLAUDE.md → "Header"). `sources` and `notes` are prose; nothing parses them.
2. **Cut the material into units** in the same file's `units` array.
3. **Check every reading against the vault.** Set `reading.status: "missing"` where the PDF is not actually present, and report the list. Never quietly generate questions for material you do not have.
4. **Leave `concepts` empty.** Concepts come from `skills/knowledge-map/SKILL.md`. Guessing claims from a chapter title produces a course of what the book is *called* instead of what it says.
5. **Leave `srs`, `placed` and `cursor` alone.** Placement writes them in the first session that selects the unit.

If the learner hands over a curriculum document, turn its content directly into units.
`units.json` is the plan; a second human-owned copy would drift within a month.

## Cutting units to size

Unit size is the main judgement call in this skill.
A unit takes one to four hours to cover every concept once; the concept counts, checker limits and reasons are in CLAUDE.md → "Unit size".

Signs a unit is too big, from most to least common:

- More than ~25 concepts. The checker catches this one.
- A heavily non-linear concept graph. A unit's graph should be mostly a chain with a few branches; a wide one means two subjects were merged.
- A long prerequisite list. A unit that needs five other units usually contains material belonging to three of them.

Split where the *material* has a seam, not where the hour count says so.
Do not split an 8-hour reading into eight units to hit a number; the `cursor` already makes it safe to stop mid-unit.

## Priority

A unit's own `priority` overrides the header's `default_priority`.

- Use `0` to park a unit that is correctly mapped but not wanted now. It beats deleting the unit.
- How often a course is studied is set by its `share`, not by priority (`CLAUDE.md` → "Header").
- `share: 0` stops a course being studied but keeps its learned units in the quiz.
- `default_priority: 0` mutes the whole course: never studied, never quizzed.

To shelve a course, move it into `courses/_archive/` with `python3 scripts/archive_course.py archive <slug>`.
Never delete it, because `sessions/` and other courses' units still reference its bank questions.

## What belongs in the header's `sources` and `notes`

`skills/bank-generator/SKILL.md` reads these two fields as live input.
They hold three things and nothing else:

1. **`sources`**: one entry per source, saying what each is *for*: which book is the spine, which paper is the authoritative treatment, which notes are only a supplement.
2. **`notes`: scope**: the subtopics the sources cover, and what the course deliberately excludes. Scope is a floor, not a ceiling, for generation. Record exclusions explicitly, because an unrecorded "we're skipping this" gets re-argued every few months.
3. **`notes`: difficulty calibration**: where the course should lean toward derivation versus conceptual coverage, and which material the learner already knows well. `bank-generator` reads this as an instruction about density, never about inclusion.

`notes` also holds caveats with no other home: where granularity is intentionally coarse, what the bank does not reach, or a PDF whose formulas did not extract.
Priority, progress, state and anything machine-readable stay out of both fields.

## Notes

- `check_vault.py` checks only the *value* of `reading.status`, not whether the file is on disk, so verifying the reading is present is your job.
- Course slugs are lowercase-hyphenated and stable. They appear in unit ids and in cross-course prereqs (`<course>:<unit>`), so renaming one is a migration, not an edit.
- Question ids never change when material moves into a course. Sessions and units join on them.
- When you re-cut units, re-check that each concept id belongs to exactly one unit (`skills/knowledge-map/SKILL.md` → "Maintenance").
