# A Guide for the AI Agent

This file is primarily technical under-the-belly details for the AI agent running the learning vault. 
If you're the learner, read `README.md` first. 

This vault uses flat files and a few Python scripts. 
The learner brings the sources and may do the reading on their own. 
The vault decides what to study next, teaches at the boundaries of understanding, quizzes what was learned before, and logs the sessions. 

The system's design follows two guiding principles:

1. Desirable difficulty in the material; no friction elsewhere. The learner should struggle with the ideas and knowledge. The learner should not waste time deciding what to study, fact checking everything that the AI says, or doing bookkeeping. 
2. Any source, any duration. The learner can bring a textbook with a full semester-long lesson plan, or a single one-off YouTube video. The learner may study for ten minutes or five hours in one sitting.

## SKILLs: Where to Start

| the learner says                                                   | read |
|--------------------------------------------------------------------|---|
| "let's do a session", "I've got an hour", "what's next"            | `skills/session/SKILL.md` (it calls `place`, `grader` and `tutor`) |
| "explain this", "help me read <paper>", "what's in my learn queue" | `skills/explain/SKILL.md` |
| a new course, a reading list, new sources, re-cut units            | `skills/course/SKILL.md`, then `skills/knowledge-map/SKILL.md` and `skills/bank-generator/SKILL.md` |
| anything about Anki flashcards                                     | `skills/flashcards/SKILL.md` (setup: `SETUP.md` beside it) |
| "gtg", "I've got to go", "end session"                             | `skills/session/SKILL.md` → "gtg", at once, mid-question if need be |

## Universal Rules

1. **Everything the learner reads goes to the session Artifact.** Chat carries turn-taking only. 
2. **Every question is generative.** No multiple choice anywhere. 
3. **Teach broad, then narrow, then synthesize.** (See `skills/tutor/SKILL.md`.)
4. **Refuse rather than improvise.** Do not teach from memory if the ground-truth reading is missing. 
5. `scripts/review.py` **is the only writer of SRS numbers.** Never hand-edit them. 
6. `scripts/check_vault.py` **must report 0 errors** after any structural change and before any merge. 
7. **Three levels of abstraction only:** course, unit, concept. 

## How a session runs

### Curriculum mode

When the learner starts a learning session, `skills/session/SKILL.md` takes over.
Every session is about **one unit**. 
If that unit is blocked by a hard prerequisite, the prerequisite becomes the unit, recursively.

1. **Place:** If the unit has never been assessed, ask a few generative questions spread across its
   concepts, then guess the rest. Placement errs low. (`skills/place/SKILL.md`)
2. **Quiz:** Ask and grade a handful of bank questions from other units.
   (`skills/grader/SKILL.md`)
3. **Study:** First teach the unit's broad picture in plain words. Then, sweep its concepts from the
   `cursor`, fast. Teach at the first friction while returning to the broad picture as each
   concept lands. Close with a synthesis round. (`skills/tutor/SKILL.md`)
4. **Capture:** Write `cursor`, concept states, `srs` and a `log` entry into `units.json`, and
   the session artifact into `sessions/`. Then commit, open a PR and merge it
   to `main`.

A concept that fails cold twice goes back to `unseen`,
which drops its unit out of `learned` and returns it to the study pool on its own.

### Ad-hoc mode

The learner may present you with an ad-hoc paper, article, report, project needs, or any other one-off learning goal that is not part of the existing curriculum. 
In this scenario, use `skills/explain/SKILL.md` instead: it maps the concepts of the material, skips the ones that the vault shows the learner already has, and teaches the rest. 
At the end, it sorts each concept taught into what already exists: nowhere, new flashcards, new concept in an existing unit, or if the topic has come up repeatedly, a new unit. 

### Scheduler

`scripts/session.py` handles all scheduling. It computes an urgency score per unit. 
```
t = days since srs.last_seen
R = (1 + t / (9 · stability)) ^ -1        retrievability
urgency = (1 − R) · priority
```

- **Quiz.** Units are sampled weighted by urgency without replacement. One question is chosen uniformly from that unit's askable set. Default 8 questions; use `-n` to change it. A unit is quiz-eligible only if its priority is above 0, its stage is `learning` or `learned`, and its prerequisites are met. A question is askable only if every concept it is attached to is `seen`. If the question is associated with no particular concept, it is askable as soon as the unit is quiz-eligible. 
- **Study.** One unit is drawn in two stages. First, a _course_ is sampled by its `share` of the learner's curriculum-learning workload. For example, four courses might have shares 3, 3, 2, and 2; this means 30% of sessions will be the first course. Then, within that course, every unit that is not yet `learned`, has priority above 0, has its reading present in the vault, and has its prerequisites met is eligible. All eligible units are sampled in an urgency-weighted manner within the chosen course. 

**Clarifications:**

- This system never computes due dates, so that scheduling is flexible to the learner's schedule. 
- A new unit or an important unit is prioritized, but no unit is discarded, unless the learner explicitly sets its priority to zero. 
- Each course has a default priority, and the learner can override per-unit priorities. This allows the learner to mute material that they are not interested in. Use a default course priority of 5 on a 10-point scale.
- The course draw is i.i.d. across sessions. 
- The second stage adds a small Gaussian to each unit's urgency before weighting, overridable per run with `--noise N`. It reorders units that are close in urgency, so that a small amount of randomness and serendipity is added to the learning schedule, which helps the learner stay engaged.
- A prerequisite edge is satisfied once its source unit reaches `learning`. Suppose `B` depends on `A`, i.e. `A -> B`. The learner can start learning unit B once they have a partial grasp of unit A. This is how learning works in real life. 

**Design decisions:**

- The unit is drawn in a weighted sample, not argmax. This ensures that the curriculum is somewhat randomly shuffled so the learner is not bored by a linear alphabetical walk of the course. 
- Course frequency is explicitly set by the learner via a per-course `share` number, typically constrained to sum to 10 for interpretability. 
- The quiz is not balanced by `share` since its job is to optimally retain already-learned concepts.  Forcing course balance would over-drill thin courses that have only a handful of quiz-eligible units. 
- `units.recent_study_courses()` is display only. It shows the recent course mix so the learner can spot an unlucky run and name a course instead; nothing schedules on it.

## Layout

A course is two files within a directory: `units.json`, `bank.jsonl`, and `sources/`.

```
vault/
  courses/<slug>/
    units.json       # THE course: prose, units, concepts, structure, statistics
    bank.jsonl       # Question bank
    sources/         # PDFs, papers, notes
  courses/_archive/  # Shelved courses, created on first use; not scheduled
  sessions/          # One dated markdown record per session
  BLOCKED.md         # Units temporarily blocked by having no source
  README.md          # Instructions for the learner
  CLAUDE.md          # Instructions for the agent
  flashcards.json    # Flashcard-layer settings
  .claude/hooks/
    session-start.sh # runs check_vault.py and restates the artifact rule at session start
  .mcp.json          # optional MCP servers: anki (AnkiConnect) and raindrop
  skills/
    session/         # THE ENTRY POINT: which components run, in what order
    place/           # guess a unit into seen/unseen, erring low
    tutor/           # sweep, hit friction, teach one reasoning step
    grader/          # mark an answer, then route the result into a write
    knowledge-map/   # cut a unit's concepts and the edges between them
    bank-generator/  # bulk-generate questions from a course's sources
    course/          # create and maintain a course
    flashcards/      # optional Anki cards from sessions and work papers; SETUP.md
    explain/         # ad hoc: teach the gaps in a paper, report or project need, then sort them
  scripts/
    session.py       # the scheduler: quiz draw + study pick
    units.py         # shared access to units.json; stage, urgency, eligibility, review
    review.py        # record one review's outcome — the only writer of the SRS numbers
    explain.py       # open explain sessions, and how often each ad hoc topic has recurred
    check_vault.py   # integrity gate — run after any structural change
    bank_stats.py    # per-course counts, and where the bank or concept coverage is thin
    archive_course.py        # move a course into courses/_archive/ and back
    anki_mix.py              # scatter newly added cards through Anki's new-card queue
    anki_decks.py            # put every Vault card in the subdeck its kind belongs in
    anki_prereview_apply.py  # apply an automated pre-review pass to unseen cards
```

## Scripts TL;DR

```
python3 scripts/session.py                 # what to be quizzed on, and what to study
python3 scripts/session.py -n 12           # a longer quiz
python3 scripts/session.py --course example   # restrict the study pick to one course
python3 scripts/session.py --json          # machine-readable

python3 scripts/review.py example:ex-binary-search partial \
    --seen ex-bs-invariant --cursor ex-bs-log-steps --note "through the invariant"

python3 scripts/check_vault.py             # must report 0 errors
python3 scripts/check_vault.py --warnings  # list the warnings too
```

`review.py` writes all SRS numbers. One call folds a review's outcome into `difficulty`, `stability`, `reps`, `lapses` and `last_seen`, sets concept states, moves the cursor and appends the log entry.

`check_vault.py` is the integrity gate. Run it after any structural change; it must report 0 errors. It checks:

- bank entries: required fields, unique ids, `source_ref` paths that exist;
- `units.json`: headers, reading status, priority and SRS fields;
- concepts: `kind`, `claim`, `state`, ids unique across units, prerequisites that resolve inside the course, no cycles;
- cursors and question links;
- unit prerequisites: they resolve, no cycles;
- unit size: a warning above 25 concepts, an error above 35.

Warnings do not fail the run. Most are `source_ref` formatting issues from question generation. Archived courses are held to a looser bar.

Cross-course dependencies live only as `external_prereqs` phrases on individual concepts. Nothing aggregates them into a course-level graph.

## On the interface

The agent needs write access to this repository. Units, banks, concepts and the learner's progress are all files, and git history is part of the record.

Each session publishes **one Artifact**: a private page with a stable URL. **Everything the learner reads goes on it:** questions, answers, hints, grading, derivations and diagrams. Chat carries only turn-taking: which question is live, that an answer landed, what was written back.

This is forced by the interface. Claude Code renders GitHub-flavoured markdown only, with no LaTeX and no images, so mathematics in chat arrives as raw backslashes and diagrams do not arrive at all.

At capture, the artifact is converted to markdown in `sessions/`. The session narrative lives there; the state it produced lives in `units.json`. Writing one without the other is a bug.

# Data model

## Levels of abstraction (locked)

There are exactly three levels. Do not add a fourth: anything that seems to need one is a unit or a concept cut at the wrong size.

| level | is | example | lives in |
|---|---|---|---|
| **Course** | a broad topic | "Database Internals" | `courses/<slug>/` |
| **Unit** | a subtopic within a course | "Two-pass sort/hash algorithms" | a record in `units.json` |
| **Concept** | one claim or one skill within a unit | "column stores win when … because …"; "the learner can solve telescoping sums of this shape" | an entry in a unit's `concepts` |

- **The unit is the only scheduled object.** It carries its reading, prerequisites, priority, spaced-repetition state, cursor, concept states, questions and history.
- **A course is a list of units** plus a shared question bank and sources directory. It has no state of its own. Two courses may reference the same unit.
- **A concept is a claim or a skill.** A claim is either recalled or not. A skill is fluent, halting or absent. Write skills as capabilities ("the learner can …").

### Unit size

A unit takes one to four hours to cover every concept once: roughly a chapter, or part of a dense one. That is usually 6 to 20 concepts. `check_vault.py` warns above 25 and errors above 35.

Smaller units make the prerequisite graph too fine to maintain by hand. Larger units cannot be finished in a session, so they never reach `learned`.

### What a prerequisite edge means

An edge `A --> B` means: without at least a partial grasp of A, B will not make sense, or the learner will have no idea where to start on it. The same definition applies to units and to concepts.

- **The failure it predicts** is incomprehension or paralysis. "B is easier after A" or "B is usually taught after A" is not an edge.
- **The threshold is partial.** An edge is satisfied once its source unit reaches `learning`. A unit at `unknown` or `new` blocks its dependents; one studied even once does not.

### The two dependency graphs

| edge | used for | notes |
|---|---|---|
| **unit → unit** | eligibility, quiz sampling, study selection | Coarse on purpose. Declared in `units.json`. May cross courses as `<course>:<unit>`. |
| **concept → concept** | the order of the sweep within a session | Mostly a chain with a few branches. Ordering hints only, never gates, so a wrong edge costs only an odd sweep order. A heavily branching concept graph means the unit should be split. |

There is no course-level graph. A cross-course dependency is recorded as `external_prereqs` on the concept that has it, and nothing routes on it.

## Course layout

A course is `units.json`, `bank.jsonl` and `sources/`, and nothing else.

### courses/<slug>/units.json

Pretty-printed JSON, meant to be read and edited by hand: a header plus a `units` array. The example below is illustrative; `courses/example/units.json` is a complete, valid course.

```json
{
  "course": "ir-ranking",
  "title": "Information Retrieval & Ranking",
  "share": 3,
  "default_priority": 5,
  "units": [
    {
      "id": "ir-transformer",
      "title": "The Transformer",
      "reading": {
        "source": "courses/ir-ranking/sources/vaswani-2017-attention.pdf#§3 Model Architecture",
        "status": "present"
      },
      "prereqs": ["ir-seq2seq-attention", "linear-algebra:la-vectors-dot-products"],
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

#### Header

- `share`: how often the course comes up in the study draw, relative to the other live courses. Make the shares sum to 10 so each reads as "sessions out of ten". A course with no eligible unit gives up its slot for that session. `0` keeps a course loaded but never studied. A course without `share` falls back to `default_priority`, and `check_vault.py` warns.
- `default_priority`: the priority of every unit that does not set its own. Priority only ranks a unit against its coursemates. `0` mutes a unit: never studied, never quizzed.
- `sources`: the bibliography, one entry per source, saying what each is for.
- `notes`: free prose about the course: what the sources cover and leave out, where granularity is coarse on purpose, what the bank does not reach, caveats about the material. `skills/bank-generator/SKILL.md` reads it; no script parses it.

#### `reading`

- `status` is `present` or `missing`. A course may exist as a plan before its material arrives, but the tutor refuses to teach a unit whose reading is `missing`.
- `also_read` and `missing_readings` are optional lists, for units that pair a chapter with a paper.

#### `concepts`

An ordered list. The order is the sweep order, topological within the unit.

| field | meaning |
|---|---|
| `id` | unique across the whole course |
| `kind` | `claim` or `skill`; a skill is written "the learner can …" |
| `claim` | what it asserts, in one sentence; the tutor teaches and tests against this |
| `prereqs` | concept ids within this course; ordering hints, never gates |
| `external_prereqs` | optional; what it leans on in another course, as a descriptive phrase (the other course may have no exactly matching concept) |
| `state` | `unknown` (not placed), `unseen` (placed, not yet studied) or `seen` (studied at least once) |
| `questions` | ids of the bank questions that test it |

A question is askable only when every concept it is attached to is `seen`. A question that no concept claims sits in the unit's own `questions` list and is askable once the unit reaches `learning`. The two lists never overlap: `units.unit_questions()` joins them and `units.askable()` filters them.

#### `stage`: derived, never stored

`scripts/units.py` computes a unit's stage from `placed`, `srs.reps` and its concept states, checking in this order:

| stage | condition |
|---|---|
| `unknown` | `placed` is null |
| `learned` | every concept is `seen` |
| `learning` | `srs.reps >= 1` |
| `new` | otherwise: placed, never studied |

- **Demotion:** repeated quiz failure sets the failing concepts back to `unseen`, which drops a `learned` unit to `learning`. That is the whole repair mechanism.
- **No cascade:** `srs.reps` never decreases, so demotion stops at `learning`. Since prerequisite edges are satisfied at `learning`, a failure never blocks units downstream.

#### `srs`: ranked, never due-dated

The memory model is FSRS's, without its scheduler. `difficulty` and `stability` update on each review, and no due date is ever computed, so a long gap creates no backlog. Urgency is computed as in "Scheduler" above.

`units.review(unit, grade)` takes `fail`, `partial` or `pass`. A unit's review spans several questions, so three grades replace FSRS's four buttons. Its update rule has four deliberate properties:

1. **A lapse multiplies stability by 0.4 and never resets it.** A unit learned and forgotten is not the same as one never learned.
2. **Growth is damped by how retrievable the unit already was** (a `(1 − R)` factor). An effortless review teaches the schedule little; an effortful one teaches it a lot.
3. **Difficulty drifts and never jumps.** One bad session is noise.
4. **`lapses` counts every review the learner could not produce cold**, `fail` and `partial` alike, including a unit's first review.

Record reviews with `scripts/review.py`; never hand-edit the numbers.

#### `cursor`

`concept` is where the sweep reached; `note` describes the position for a person. With it a session resumes mid-unit; without it the sweep starts at the first concept. Advance it as the sweep moves, not at the end, so the learner can stop at any moment.

#### `log`

Append-only, one entry per session that touched the unit: `date`, `what` (a sentence a person could act on) and `failed` (concept ids that missed). A demotion records its reason here.

### courses/<slug>/bank.jsonl

One JSON object per question per line. Append-only: sessions refer to questions by `id`, so only rewrite an entry to fix a factual error.

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

- **Every question is generative.** No multiple choice.
- **Factual recall is a question type.** A definition or theorem statement to memorize becomes a question that asks for it ("Define X", "What does Y mean in the definition of Z?", "Contrast the definitions of A and B"). Its spacing comes from the unit's SRS. Anki flashcards are a separate, optional, lighter layer (`skills/flashcards/SKILL.md`).
- `topic` is the legacy course name that matches the id prefix; `course` is the directory slug. `check_vault.py` requires both.
- `type` is a loose tag, not a fixed list (see `skills/bank-generator/SKILL.md`).
- `answer_key` must let a grader check an answer without the source.
- `grading_notes` is optional: other acceptable framings, common near-misses.

### sessions/

One markdown file per session, converted from its artifact: the questions asked, the answers given verbatim, and notes on what was hard.

- **Study and quiz sessions** are named `<YYYY-MM-DD-HHMM>-<unit-id>.md`; a quiz-only session uses `mixed-retention` in place of the unit id. `units.recent_study_courses()` reads the names to display the recent course mix. Nothing schedules on them.
- **Explain sessions** are named `<YYYY-MM-DD-HHMM>-explain-<slug>.md` and open with front matter: `kind`, `title`, `source_kind`, `source`, `topics`, `status`, and `cursor` while `status` is `open`. `scripts/explain.py` reads it to resume open sessions and to count how often each topic recurs; `check_vault.py` validates it.

## Retired

Each of these were previously tried and rejected. Do not reintroduce them. 

| retired                                                       | replaced by                                                             |
|---------------------------------------------------------------|-------------------------------------------------------------------------|
| `cards.jsonl`                                                 | `bank.jsonl`; spacing comes from unit SRS                               |
| `STUDY.md` stride scheduling                                  | per-unit `priority` × retrievability                                    |
| study targets                                                 | set `priority: 0` for unwanted units                                    |
| curriculum plan document                                      | `units.json` _is_ the plan                                              |
| learner profile                                               | the owning unit's `log`, where an observation sits next to its evidence |
| migration log                                                 | git history                                                             |
| map of concepts                                               | concepts fold into the unit that owns them                              |
| course document                                               | `units.json` _is_ the course                                            |
| alphanumeric unit IDs (`ir-A1`, `ir-C2a`)                     | descriptive ids                                                         |
| estimated hours, additional layers of abstraction             | one mode; size is fixed by the unit-size rule                           |
| unit `status`, `placement`                                    | derived `stage`                                                         |