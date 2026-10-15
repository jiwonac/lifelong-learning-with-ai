# Course

Creates and maintains a course: its `units.json` and the sources under it. Use when the user
wants a new course, hands over a curriculum or reading list, adds sources to an existing course,
or wants its units re-cut.

Not a session skill. `skills/session/SKILL.md` runs the studying and writes all the state that
studying produces; this skill owns the structure that exists before any of it.

## What a course is now

**A directory of units plus the material they share** — two files and a directory:

```
courses/<slug>/
  units.json     # THE course — header, units, concepts, structure, state
  bank.jsonl     # every question, generative only
  sources/       # PDFs, papers, notes
```

That is the whole of it. There is no `COURSE.md` and no `map.md`: everything in them either
belonged on a unit or was prose, and the prose moved into the `units.json` header.

A course has **no state**. No status, no stage, no tier, no weight, no cursor, no progress. Every
one of those used to live here and every one of them is now on the unit, because the unit is the
only thing that gets scheduled. When someone asks "how is this course going", the answer is a
distribution over its units' stages, computed from `units.json` — not a field you maintain.

Two courses may legitimately reference the same unit: a databases course and an information
retrieval course might both want Fagin's Threshold Algorithm. That is fine and is a reason the unit, not the course, is the
atom.

See `CLAUDE.md` for every field. This file is about judgement, not format.

## Creating a course

1. **Write the `units.json` header** — `course`, `title`, `default_priority`, plus `sources` and
   `notes` (below). `sources` and `notes` are prose; nothing parses them.
2. **Cut the material into units** in the same file's `units` array.
3. **Check every reading against the vault.** Set `reading.status: "missing"` where the PDF is
   not actually present, and report the list. A course that exists as a plan before it exists as
   material is legal and expected — the tutor refuses to run those units rather than improvising,
   which is the whole reason the field exists. Never quietly generate questions for material you
   do not have.
4. **Leave `concepts` empty.** Concepts come from `skills/knowledge-map/SKILL.md`, not from a
   plan. Plans name readings; concepts name claims; guessing the claims from a chapter title
   produces a course of what the book is *called* rather than what it says.
5. **Leave `srs`, `placed` and `cursor` alone.** Placement writes them, in the first session that
   selects the unit.

There is no `plan.md`. If the user hands over a curriculum document, its content becomes units
directly — `units.json` *is* the plan, and a second human-owned copy of it would drift within a
month.

## Cutting units to size

This is the judgement call the skill exists for, and getting it wrong is expensive in both
directions.

**A unit is one to four hours to cover every concept in it once** — roughly a chapter, or part of
one where the book is dense. In practice that lands at 6–20 concepts. `check_vault.py` warns
above 25 and errors above 35.

That size is not arbitrary. It is the size that makes everything downstream work:

- Small enough that "study this unit" is a **session**, not a project. A unit you cannot finish
  in any plausible sitting turns `learned` into a state nothing ever reaches, and the SRS never
  gets to do its job.
- Large enough that the **prerequisite graph over units stays coarse** enough to maintain by
  hand. Cut to half-hour units and the edges outnumber the units.

Symptoms of a unit cut too big, in rough order of how often they show up:

- More than ~25 concepts. The checker catches this one.
- The concept graph inside it is **heavily non-linear**. A unit's concept graph should be
  primarily a chain with a few branches; a wide graph means you have merged two subjects.
- Its prerequisites are a long list. A unit that needs five other units usually contains material
  belonging to three of them.

Cut a plan item into two units where the *material* has a seam, not where the hour count says so.
Do not split an 8-hour reading into eight units to hit a number — the `cursor` already makes a
long unit safe to stop in the middle of.

## Priority

`default_priority` in the header applies to every unit in the course; a unit overrides it with
its own `priority`. This is the only knob that decides what gets studied, and it replaced
cross-course weights, `targets:` and every derived blocking/deferred disposition.

- **`0` mutes a unit**: never scheduled, never sampled. This is how you park material that is
  real and correctly mapped but not wanted right now — better than deleting it, and better than a
  status field, because the scheduler needs no special case for it.
- Set `default_priority` by how much the user wants this course relative to the others. It is
  compared across courses, so a course everyone agrees is background should sit visibly lower
  rather than being handled by never picking it.

Muting a whole course is `default_priority: 0`. Shelve one for real by moving the directory into `courses/_archive/`, never by deleting it — the bank's questions
are still referenced from `sessions/` and from other courses' units.

## What belongs in the header's `sources` and `notes`

These two fields are the course's only prose, and they exist because they are the live inputs
`skills/bank-generator/SKILL.md` reads. Three things go in them and nothing else:

1. **`sources`** — the bibliography, one entry per source, saying what each is *for*. Which book
   is the spine, which paper is the one authoritative treatment, which set of notes is only a
   supplement.
2. **`notes`: scope** — the subtopics the sources cover, and what the course deliberately
   excludes. Scope is a **floor, not a ceiling** for generation: it says what must be covered,
   not what may be. Record exclusions explicitly, because an unrecorded "we're skipping this"
   gets re-litigated every few months.
3. **`notes`: difficulty calibration** — where this course should skew toward derivation versus
   conceptual coverage, and which material the user considers already engrained.
   `bank-generator` reads this as an instruction about *density*, never about inclusion.

`notes` also absorbs the caveats that have nowhere else to live: where the granularity is
intentionally coarse, what the bank does not reach, a PDF whose formula layer did not extract.

Anything about priority, progress or state does not belong here. Those are per-unit, in the same
file's `units` array. Nothing machine-readable goes in either field — the old status block is
gone, replaced by per-unit `priority`.

## Notes

- Run `python3 scripts/check_vault.py` after any structural change. It validates unit ids,
  prereq resolution and acyclicity, concept kinds, claims and states, concept-prereq resolution
  and acyclicity, cursor targets, `questions` links, unit size, and `reading.status` — though
  note it checks the *value* of that field, not whether the file it names is on disk, so
  verifying the reading really is present is still your job.
- Course slugs are lowercase-hyphenated and stable — they appear in unit ids and in cross-course
  prereqs written `<course>:<unit>`. Renaming one is a migration, not an edit.
- Question ids never change when material moves into a course. Sessions and units join on them,
  and a course-local id would buy nothing.
- A concept id must be unique across the whole course and live in exactly one unit;
  `check_vault.py` errors if two units claim the same one. When you re-cut units, re-check that
  assignment in the same pass.
