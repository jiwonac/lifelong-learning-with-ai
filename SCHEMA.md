# Data formats

# Levels of abstraction — locked

**This vault has exactly three levels. Do not invent a fourth.** Every file, every skill and
every script operates at one of them, and anything that feels like it needs a new level is a unit
or a concept described at the wrong grain.

| level | is | example | lives in |
|---|---|---|---|
| **Course** | a broad topic | "Database Internals" | `courses/<slug>/` |
| **Unit** | a subtopic within a course | "Two-pass sort/hash algorithms" | a record in `units.json` |
| **Concept** | a distinct claim *or* skill within a unit | "column stores win when… because…"; "the learner can solve telescoping sums of this shape" | an entry in a unit's `concepts` |

**The unit is the only scheduled object.** It carries its own reading, prerequisites, priority,
spaced-repetition state, cursor, concept states, questions and history. Everything the scheduler
needs to answer "what should I study, and what should I be quizzed on" is on the unit record.

A **course is a list of units** plus the material they share — a bank and a sources directory. It is not a scheduling unit and has no state of its own. Two courses may legitimately
reference the same unit: a databases course and an information retrieval course might both want
Fagin's Threshold Algorithm.

A **concept is a claim or a skill.** Both are things to internalize and both are testable, but
they fail differently: a claim is either regenerable or not, while a skill is fluent, halting, or
absent. Write skill concepts as capabilities — *"the learner can …"* — not as facts.

## Unit size

A unit is **one to four hours of study to cover every concept in it once** — roughly a chapter,
or a portion of one where the book is dense. In practice that lands at 6–20 concepts. A unit much
past 25 concepts should be split; `check_vault.py` warns above 25 and errors above 35.

This is the size that makes the rest work: small enough that "study this unit" is a session
rather than a project, large enough that the prerequisite graph over units stays coarse enough
to maintain by hand.

## What a prerequisite edge means

The same definition governs both graphs that matter — units and concepts.

An edge `A --> B` asserts: **without at least a partial grasp of A, B will not make sense, or you
will blank on how to tackle it.**

Two halves of that, and the second is the one people get wrong:

- **The failure it predicts** is either incomprehension ("this sentence is words") or paralysis
  ("I know what is being asked and have no idea where to start"). If neither would happen, there
  is no edge — B being *easier* with A, or *usually taught after* A, is not an edge.
- **The threshold is partial, not complete.** `A --> B` does **not** mean 100% of A must be closed
  before B can begin.

Operationally: **an edge is satisfied once its source unit reaches `learning`.** A unit that is
`unknown` or `new` blocks what depends on it; one that has been studied even once does not.
Requiring completion serializes a curriculum for no reason, and starting B is often what
consolidates A.

## The two dependency graphs

| edge | used for | notes |
|---|---|---|
| **unit → unit** | **the working graph** — eligibility, quiz sampling, study selection | Deliberately coarse. Declared in `units.json`; may cross courses as `<course>:<unit>`. |
| **concept → concept** | **within-session order** — where the sweep goes next | Primarily a linear chain with a few branches. Declared on the concept. **Ordering hints, never gates** — a wrong one costs a slightly odd sweep order, so they do not need to be perfect, only walkable. If a concept graph is heavily non-linear, the unit is probably two units. |

There is no course-level graph. Cross-course dependency is recorded where it is actually
observed — as `external_prereqs` on the concept that has it — and nothing routes on it.

---

# Course layout

```
courses/<slug>/
  units.json     # THE course — units, concepts, structure, state, everything
  bank.jsonl     # every question, generative only
  sources/       # PDFs, papers, notes
sessions/        # one dated markdown record per session, vault-wide
BLOCKED.md       # units removed for having no source; re-add when the reading lands
```

**A course is two files and a directory.** It has no `COURSE.md` and no `map.md`: everything
that was in them either belonged on a unit or was prose, and the prose moved into the header.

## courses/<slug>/units.json

Pretty-printed JSON — one object with a header and a `units` array. **Readable and editable by
hand**; that is why it is not JSONL. The example below is illustrative; `courses/example/units.json`
is a complete, valid course.

```json
{
  "course": "ir-ranking",
  "title": "Information Retrieval & Ranking",
  "default_priority": 5,
  "units": [
    {
      "id": "ir-B2c",
      "title": "The Transformer",
      "reading": {
        "source": "courses/ir-ranking/sources/vaswani-2017-attention.pdf",
        "locator": "§3 Model Architecture",
        "status": "present"
      },
      "prereqs": ["ir-B2b", "linear-algebra:la-vectors-dot-products"],
      "priority": 5,
      "placed": "2026-08-17",
      "srs": {
        "last_seen": "2026-08-14",
        "reps": 3,
        "lapses": 1,
        "difficulty": 6.2,
        "stability": 9.4
      },
      "cursor": {
        "concept": "ir-posenc",
        "note": "self-attention and multi-head done; positional encoding next"
      },
      "concepts": [
        {
          "id": "ir-attn-scaled",
          "kind": "claim",
          "claim": "Scaling by 1/sqrt(d_k) keeps the dot products out of the region where softmax saturates, which is why it is there and not for normalization.",
          "prereqs": ["ir-attn-soft-lookup"],
          "external_prereqs": ["linear-algebra: dot products as similarity"],
          "state": "seen",
          "questions": ["information_retrieval-000451"]
        },
        {"id": "ir-posenc", "kind": "skill", "claim": "the learner can …",
         "prereqs": ["ir-attn-scaled"], "state": "unseen", "questions": []}
      ],
      "questions": ["information_retrieval-000452"],
      "log": [
        {"date": "2026-08-14", "what": "swept to positional encoding", "failed": ["ir-mha"]}
      ]
    }
  ]
}
```

### Header

- **`share`** is how often this course comes up in the study draw, as a ratio against the other
  live courses. Set them so they sum to 10 and each reads directly as *sessions out of ten*.
  A course with no eligible unit in a given session holds no slot, and the rest renormalise over
  what remains. `0` keeps a course loaded but never studied. Optional for back-compat: a course
  without it falls back to `default_priority`, which reintroduces the unit-count bias `share`
  exists to remove, so `check_vault.py` warns.
- **`default_priority`** applies to every unit in the course. A unit overrides it with its own
  `priority`. Since `share` decides how often the *course* comes up, priority now says only how
  much a unit matters against its own coursemates. `0` means **never scheduled and never sampled**
  — the way to mute material that is real but not wanted right now.
- **`sources`** — the bibliography, one entry per source, saying what each is for.
- **`notes`** — free prose about the course as a whole: what the sources cover and deliberately
  do not, where the granularity is intentionally coarse, what the bank does not reach, and any
  caveat about the material (a PDF whose formula layer did not extract, say). Read by
  `skills/bank-generator/SKILL.md`; not parsed by anything.

### `reading`

- `status` is `present` or `missing` — can this unit be run at all. A unit whose reading is not
  in the vault is legal and expected (a course can exist as a plan before it exists as material),
  but the tutor must refuse to run it rather than improvising from nothing.
- `also_read` and `missing_readings` are optional lists, for units that pair a textbook chapter
  with a paper that is (or is not) in the vault.

### `concepts`

An ordered list, and **the order is the sweep order** — topological within the unit.

| field | |
|---|---|
| `id` | unique across the whole course, not just the unit |
| `kind` | `claim` or `skill`. A skill is written as a capability — *"the learner can …"* |
| `claim` | what it asserts, in one sentence. This is what the tutor teaches and tests against. |
| `prereqs` | concept ids **within this course**. Ordering hints for the sweep — never eligibility gates. |
| `external_prereqs` | optional; what this leans on in another course, as a descriptive phrase. The far end is a phrase and not an id because the other course may not have a concept that matches exactly. |
| `state` | `unknown` / `unseen` / `seen` |
| `questions` | bank ids testing this concept |

| concept state | meaning |
|---|---|
| `unknown` | not placed — no information either way |
| `unseen` | placed, and determined not to have been studied |
| `seen` | studied at least once |

A question is **askable** only when every concept it is attached to is `seen` — a question
testing two claims cannot be a fair review while half of what it tests was never studied. A
question the unit owns but no concept claims sits in the unit's own `questions` list and is
askable once the unit reaches `learning`, there being no finer evidence to gate it on. The two
lists are disjoint: `units.unit_questions()` unions them, `units.askable()` filters them.

### `stage` — derived, never stored

A unit's stage is a function of `placed`, `srs.reps` and its concept states, evaluated in this
order:

| stage | condition |
|---|---|
| `unknown` | `placed` is null — never placed |
| `learned` | every concept is `seen` |
| `learning` | `srs.reps >= 1` — studied in at least one session |
| `new` | otherwise — placed, but studied zero times |

Storing it would let it drift from the concept states that define it. `scripts/units.py` computes
it; everything else asks that.

**Demotion is real.** Repeated quiz failure on a `learned` unit sets the failing concepts back to
`unseen`, which drops the unit to `learning` on the next evaluation. That is the whole of the
repair mechanism — there is no separate repair course and no spur.

**A demotion cannot cascade.** `srs.reps` only ever increases, so a unit that has reached
`learning` can never fall back to `new` or `unknown`; demotion moves `learned → learning` and no
further. Since a prerequisite edge is satisfied at `learning`, **nothing downstream is ever
blocked by a failure upstream.** One hard concept failing a review returns its own unit to the
study pool and changes the eligibility of nothing else — which is the behaviour you want, because
the alternative is that a single bad evening withdraws a third of the curriculum.

### `srs` — retrievability-ranked, never due-dated

FSRS's memory model, without its scheduler. `difficulty` and `stability` update per review;
what is *never* computed is a due date, because due dates create backlogs and this vault must
work identically at one hour a week or fifteen.

```
    t = days since srs.last_seen
    R = (1 + t / (9 · stability)) ^ -1        retrievability
    urgency = (1 − R) · priority
```

Ranking by urgency instead of thresholding it means a three-week gap produces no debt — only a
set of units that are all somewhat more urgent than they were, in the same order.

**The update rule is `units.review(unit, grade)`** — `fail` | `partial` | `pass`, three grades
rather than FSRS's four because a unit's review is several questions and the aggregate is not a
button press. Three properties of it are deliberate:

- **A lapse multiplies stability (×0.4); it never resets it.** A unit learned once and lost is
  not in the same state as one never learned, and treating them alike is what makes conventional
  schedulers punishing after a gap.
- **Growth is damped by how retrievable the unit already was** — the gain carries a `(1 − R)`
  term. Reviewing something you would have recalled anyway teaches the schedule little; a review
  that was genuinely effortful teaches it a lot. This is the desirable-difficulty effect, priced
  in.
- **Difficulty drifts, it never jumps.** One bad session on a unit you know is noise.

Record reviews with `scripts/review.py`, never by hand-editing the numbers.

### `cursor`

**The load-bearing field.** `concept` is where the sweep reached; `note` is a human-readable
position. With it a session resumes mid-unit; without it the sweep starts at the unit's first
concept and moves fast until it hits friction.

Advance it **as the sweep moves**, not only at the end of a block. That is what makes stopping at
any moment safe.

### `log`

Append-only. One entry per session that touched the unit: `date`, `what` (a sentence a person
could act on), and `failed` (concept ids that missed). This is where a demotion records *why*.


## courses/<slug>/bank.jsonl

One JSON object per line. Append-only — never rewrite existing entries in place (except to fix a
factual error), since sessions reference questions by `id`.

```json
{
  "id": "topicA-000123",
  "course": "topic-a",
  "topic": "topicA",
  "subtopic": "enzyme kinetics",
  "type": "short_answer",
  "question": "Explain why competitive inhibition can be overcome by increasing substrate concentration, but noncompetitive inhibition cannot.",
  "answer_key": "Competitive inhibitors bind the active site and compete with substrate, so enough substrate outcompetes them; noncompetitive inhibitors bind elsewhere and don't compete with substrate binding, so raising substrate concentration doesn't displace them.",
  "grading_notes": "Accept answers that mention Km/Vmax effects as an alternative framing.",
  "source_ref": "courses/topic-a/sources/biochem_ch7.pdf#section-3",
  "difficulty": "medium",
  "date_generated": "2026-07-03"
}
```

**Every question is generative.** No multiple choice anywhere in this vault — recognition is
handled by the learner's own immersive reading, and every question the system asks requires a
production.

**Factual recall is a question type, not a separate object.** There are no cards. A theorem
statement, a definition or a piece of vocabulary that must be memorized becomes a bank question
that asks for it — *"Define X"*, *"What does Y mean inside the definition of Z?"*, *"Contrast the
definition of A with that of B"*. The spacing that flashcards provide comes from the unit-level
SRS above, not from the question being a different kind of thing.

- `topic` is the legacy name for the course and matches the id prefix; `course` is the slug of
  the directory the question lives in. Both are required — `check_vault.py` rejects an entry
  missing either.
- `type` is a loose tag, not a fixed enum — see `skills/bank-generator/SKILL.md`.
- `answer_key` should let a grader check correctness without going back to the source.
- `grading_notes` is optional — for multiple acceptable framings or common near-misses.


## sessions/

One file per session, `sessions/<YYYY-MM-DD-HHMM>-<unit-id>.md`, converted from that session's
artifact. Holds the questions asked, the answers given, and annotations on what was difficult.

`units.recent_study_courses()` reads these filenames to show the recent course mix at the top of a
session, resolving the `<unit-id>` part by its course prefix. **Nothing schedules on it** — the
course draw is independent of history — so an off-convention name costs a line of context and not
a scheduling decision. A quiz-only session has no unit and is named `mixed-retention`.

The narrative lives here; the state it produced lives in `units.json`. A session that writes one
without the other is a bug.

An **explain session** (`skills/explain/SKILL.md`) studies no unit and is named
`<YYYY-MM-DD-HHMM>-explain-<slug>.md`. Its file opens with front matter (`kind`, `title`,
`source_kind`, `source`, `topics`, `status`, and `cursor` while `status` is `open`), which
`scripts/explain.py` reads to resume open sessions and count how often each topic recurs, and
which `check_vault.py` validates. Its `explain-` prefix matches no course, so it does not count
toward the recent course mix. Any `units.json` writes it makes are concepts added to existing
units, each with a `log` entry.


---

# Retired

Each of these was a real mechanism that is now gone. Do not reintroduce them.

| retired | replaced by |
|---|---|
| `cards.jsonl` | factual-recall **questions** in `bank.jsonl`; spacing comes from unit SRS |
| `spurs.jsonl` | nothing — a discovered gap demotes concepts in the unit that owns them |
| `courses/repair/` | the same demotion; a repaired unit is just a unit |
| `STUDY.md` stride scheduling | per-unit `priority` × retrievability |
| `targets:` and derived disposition | `priority: 0` on units you do not want |
| `plan.md` | `units.json` is the plan |
| `tests/`, `session_log.jsonl` | `sessions/` |
| `units.jsonl` `track` field | nothing — it was a label, never a level |
| `LEARNER.md` | the owning unit's `log`, where an observation sits next to its evidence |
| `MIGRATION.md` | git history |
| `map.md` | concepts fold into the unit that owns them |
| `COURSE.md` | `sources` and `notes` in the `units.json` header; everything else was per-unit |
| track-letter unit ids (`ir-A1`, `ir-C2a`) | descriptive ids |
| `units.jsonl` `mode`, `depth`, `est_hours`, `goal`, `learn` | one workflow, so nothing branches on mode; size is fixed by the unit-size rule |
| unit `status`, `placement` | derived `stage` |
| "areas" (a fourth level between course and unit) | units |
| the 5-rung concept ladder (`gap`/`shaky`/`derivable`/`solid`) | `unseen`/`seen`, with SRS carrying the graded part |
