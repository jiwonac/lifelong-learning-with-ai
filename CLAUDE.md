# Learning vault: agent guide

This file is for the agent running the vault. `README.md` is for the learner and holds only what
they need to use it; everything about how the vault works, what the rules are and what the files
mean is here. When the two disagree, fix whichever is wrong rather than following either blindly.

The vault is a study system built from files and a few scripts, driven from Claude Code with write
access to this repository. The learner brings the sources and does the reading; the vault decides
what to study next, teaches at the point where understanding stops, quizzes what was covered
before, and records the result.

Two principles shape everything:

1. **Maximize struggle in the material and eliminate it everywhere else.** Difficulty in the ideas
   is the point. Difficulty in deciding what to study, finding the source, checking whether a
   claim is true, or tracking what has been covered is waste, and the vault absorbs it. If the
   learner is thinking about the system, the system is malfunctioning.
2. **Any duration must work.** Thirty minutes some days, three hours others, nothing for a
   fortnight. Nothing accumulates a backlog, and no session needs reorientation to start.

## Where to start

| the learner says | read |
|---|---|
| "let's do a session", "I've got an hour", "what's next" | `skills/session/SKILL.md` (it calls `place`, `grader` and `tutor`) |
| "explain this", "help me read <paper>", "what's in my learn queue" | `skills/explain/SKILL.md` |
| a new course, a reading list, new sources, re-cut units | `skills/course/SKILL.md`, then `skills/knowledge-map/SKILL.md` and `skills/bank-generator/SKILL.md` |
| anything about Anki cards, work papers, vocabulary | `skills/flashcards/SKILL.md` (setup: `SETUP.md` beside it) |
| "gtg", "I've got to go", "end session" | `skills/session/SKILL.md` → "gtg", at once, mid-question if need be |

## Rules that apply everywhere

- **Everything the learner reads goes in the session Artifact; chat carries turn-taking only.**
  See "On the interface" below and `skills/session/SKILL.md`.
- **Every question is generative.** No multiple choice anywhere.
- **Teach broad, then narrow, then synthesize** (`skills/tutor/SKILL.md`).
- **Refuse rather than improvise.** A unit whose reading is not in the vault is not taught from
  memory; explain sessions name a source for every explanation.
- **`scripts/review.py` is the only writer of SRS numbers.** Never hand-edit them.
- **`scripts/check_vault.py` must report 0 errors** after any structural change and before any
  merge.
- **Three levels only**: course, unit, concept. Do not invent a fourth.

## How a session runs

When the learner says "let's do a session" (or "I've got an hour", or "what's next"),
`skills/session/SKILL.md` takes over. Every session is about **one unit**; if that unit is
blocked by a prerequisite, the prerequisite becomes the unit, and that recursion is the whole
curriculum.

1. **Place** — if the unit has never been assessed, a few generative questions spread across its
   concepts, then guess the rest. Placement errs low on purpose (`skills/place/SKILL.md`).
2. **Quiz** — a handful of bank questions from other units, asked one at a time in the artifact
   (`skills/grader/SKILL.md` marks and routes them).
3. **Study** — give the unit's broad picture in plain words, sweep its concepts from the
   `cursor`, fast, teach at the first friction while returning to the broad picture as each
   concept lands, and close with a synthesis round (`skills/tutor/SKILL.md`).
4. **Capture** — write `cursor`, concept states, `srs` and a `log` entry into `units.json`, and
   the session artifact into `sessions/`. Saying "gtg" then commits, opens a PR and merges it
   to `main`, gated on `check_vault.py` reporting zero errors.

**Every question in this vault is generative.** No multiple choice anywhere — recognition is what
the learner's own reading is for.

**Repair is not a separate mechanism.** A concept that fails cold twice goes back to `unseen`,
which drops its unit out of `learned` and returns it to the study pool on its own.

### Ad hoc needs: explain sessions

A paper the learner is about to read, an autoresearch report full of unfamiliar concepts, or a project
task is not a unit, and the scheduler never sees it. When the learner says "explain this",
`skills/explain/SKILL.md` runs instead: it maps the concepts the material depends on, skips the
ones the vault shows the learner already has, and teaches the rest. At the end it sorts each concept
taught into what already exists: nowhere, a flashcard, a concept on an existing unit, or, once a
topic has come up in more than one explain session, a new unit. Nothing new is scheduled, so
there is no ad hoc backlog. With the optional Raindrop integration, things to understand later
wait under the `learn` tag in Raindrop, which nothing surfaces unless the learner asks.

### What the scheduler actually does

`scripts/session.py` is the entire scheduler. It computes one number per unit —

```
t = days since srs.last_seen
R = (1 + t / (9 · stability)) ^ -1        retrievability
urgency = (1 − R) · priority
```

— and draws from that one ranking twice:

- **Quiz.** Units are sampled *weighted by urgency, without replacement* (not top-N: top-N would
  serve the same handful every session and never interleave), then one question is chosen
  uniformly from that unit's askable set. Default 8 questions; `-n` changes it. A unit is
  quiz-eligible only if its priority is above 0, its stage is `learning` or `learned`, and its
  prerequisites are met. A question is askable only if **every** concept it is attached to is
  `seen` — or, for a question the unit owns that no concept claims, as soon as the unit itself is
  quiz-eligible, there being no finer evidence to gate it on.
- **Study.** One unit, drawn in **two stages**, from those that are not `learned`, have priority
  above 0, have their reading present in the vault, and have their prerequisites met.

  **Which course** comes first, and it is settled by `share` — a course-header field that reads as
  *sessions out of ten*. For example, four courses might have shares 3, 3, 2 and 2; they sum to
  10 on purpose so the numbers can be read straight off. A course with no eligible unit this
  session holds no slot, and the remaining shares renormalise over whatever is left.

  **Which unit** comes second, urgency-weighted inside that course only. Splitting the draw is
  what makes `share` mean what it says: a single weighted draw ties a course's frequency to how
  many units it happens to have eligible, so an 80-unit course drowns a 25-unit one unless the
  priorities are bent to compensate. Choosing the course first takes unit count out of the
  question, and `priority` goes back to being only a within-course weight.

`urgency` **ranks and never thresholds.** No due date is computed anywhere, which is why a
three-week gap produces no debt — only a set of units that are all somewhat staler, in the same
order. A unit that has never been reviewed has `R = 0`, so new material is maximally urgent among
things that are eligible at all.

**Priority is per unit**, defaulting to the course's `default_priority`, and it now says only how
much this unit matters *against its own coursemates*. `0` still means never scheduled and never
sampled — the way to mute material that is real but not wanted right now. Courses normally sit
at `default_priority: 5`; how often a course comes up is `share`'s job, not priority's.

### The course draw is independent across sessions

Courses are drawn i.i.d. at those probabilities (30/30/20/20 in the example above), with no memory of what the last
few sessions were. That is a deliberate choice against the obvious alternative. A *deficit* scheme,
weighting each course by its target minus what the last ten sessions actually served, makes every
window of ten land exactly on the shares; it was built, measured and then removed. It buys that
exactness by turning the rotation into a cycle the learner could recite, and it needs a session history to
read.

Independence gives the right long-run frequency and a genuinely uncertain next session. The cost is
streaks: over ten sessions a course with `share: 3` comes back anywhere from none to eight times,
standard deviation about 1.5. **That cost is small here because naming a course overrides the draw
in one sentence** — a scheduler that cannot produce an unlucky run also cannot produce a surprise,
and the run is the cheaper of the two problems to fix.

### Noise on the unit, not on the course

The second stage adds a small Gaussian to each unit's urgency before weighting — `units.UNIT_NOISE`,
default sigma `0.25` against a 0–5 range, overridable per run with `session.py --noise N`. It
reorders units that are already close and does not promote a cold unit over a due one. Its one
visible effect is at the bottom: a unit reviewed today has urgency exactly 0 and was therefore
unreachable, and the noise gives it about a 1% chance instead. The quiz draw does not use it, since
there the urgency ranking is the entire claim being made.

### Why the scheduler is built this way

These choices were each tried the other way first; do not reintroduce the alternatives.

- **The study pick is a weighted draw, not an argmax.** Many eligible units sit at exactly the same
  urgency (never reviewed, so `R = 0` and urgency equals priority), and an argmax with a
  tie-break then walks the curriculum in alphabetical order and never interleaves. Top-1 is
  top-N with N = 1, which is the failure the quiz's weighted draw already exists to avoid.
- **Course frequency is set by `share`, not by bending priorities.** Priorities tuned to offset
  unit counts work, but nobody reading the numbers later can tell why a large course sits at 2
  and a small one at 10.
- **The course draw is independent, not deficit-scheduled.** A deficit scheme hits every ten-session
  window exactly and turns the rotation into a recitable cycle. Independence was measured to give
  P(same course twice running) of about 0.27 for a 3-of-10 share, matching the i.i.d.
  prediction; naming a course fixes an unlucky run.
- **The quiz is not balanced by `share`.** Its job is to return what has been studied, and forcing
  course balance would over-drill thin courses that have only a handful of quiz-eligible units.
  It stays urgency-weighted and evens out as the other courses are studied.
- **`units.recent_study_courses()` is display only.** `session.py` prints the recent course mix so
  an unwanted run is visible, but nothing schedules on it, so session filenames are not
  load-bearing.

**A prerequisite edge is satisfied once its source unit reaches `learning`** — partial grasp, not
completion. Requiring completion would serialize a curriculum for no reason.

## Layout

**A course is two files and a directory.** There is no `COURSE.md` and no `map.md`: everything
in them either belonged on a unit or was prose, and the prose moved into the `units.json` header.

```
vault/
  courses/<slug>/
    units.json       # THE course — header prose, units, concepts, structure, all state
    bank.jsonl       # every question, generative only
    sources/         # PDFs, papers, notes (yours; none are included)
  courses/example/   # a one-unit example course with its own notes and five questions
  courses/_archive/  # shelved courses, created on first use; moved, never deleted; not scheduled
  sessions/          # one dated markdown record per session, vault-wide (starts empty)
  BLOCKED.md         # template: units removed for having no source; re-add when the reading lands
  README.md          # for the learner: what the vault is and how to use it
  CLAUDE.md          # for the agent: this file; rules, layout, scheduler and data formats
  flashcards.json    # flashcard-layer settings: last cleanup date, vocabulary sorting page URL
  vocabulary/
    sort.html        # the word-sorting page, published as an Artifact
    sources/         # where to fetch the public word lists (the lists are not included)
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
    flashcards/      # optional Anki cards from sessions, work papers and vocabulary; SETUP.md
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
    vocab.py                 # vocabulary candidates: word lists → pool → sorting page → verdicts
```

Inside `units.json`, the header carries `sources` (the bibliography) and `notes` (scope,
difficulty calibration, and any caveat about the material) — the two parts of the old `COURSE.md`
that were load-bearing, and what `bank-generator` reads. Each unit carries its own `concepts`
array, in sweep order, each entry `{id, kind, claim, prereqs, external_prereqs?, state,
questions}`. Concept `prereqs` **order the sweep and gate nothing**, so a wrong one costs a
slightly odd sweep order and nothing else; that is what makes thousands of them cheap to keep.
`external_prereqs` holds cross-course dependencies as descriptive phrases, because the far end
may have no exactly-matching concept to point at.

## Running the scripts

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

`review.py` is the **only** thing that should write the SRS numbers. It folds one review's
outcome into `difficulty`, `stability`, `reps`, `lapses` and `last_seen`, sets concept states,
moves the cursor and appends the log entry, in one call.

`check_vault.py` is the gate: run it after anything that writes structure, and it must stay at
zero errors. It validates bank fields and ids, `source_ref` paths against the filesystem,
`units.json` headers and every unit's reading status, priority and SRS fields, each concept's
`kind`, `claim` text and `state`, that no concept id appears in two units, that concept
prerequisites resolve within their course and the concept graph is acyclic, cursor targets,
question links in both the concept and unit lists, and unit prerequisite resolution and
acyclicity. It also enforces unit size — a warning above 25 concepts, an error above 35.

Warnings are informational and do not fail the run. Most are `source_ref`-format issues from
question generation; archived courses are exempt from the stricter bar a live course is held to.

Cross-course dependencies are no longer summarised anywhere. They live as `external_prereqs`
on individual concepts, and their far end is a descriptive phrase rather than an
id, so nothing can resolve them into a course-level graph without hand work. The script that
used to print one read the map files and was deleted with them; it was reference-only, so no
session depended on it.

## On the interface

Everything runs through Claude Code with write access to this repo. That write access is the
requirement: the banks, the units, the concepts and the learner model are all files, and git
history is itself part of the record. A read-only setup would terminate every loop here at the point
where it needs to record what it learned about you.

Each session publishes **one Artifact** — a private page with a stable URL — and **everything the
learner reads goes on it**: the questions, their answers, the hints, the grading, every derivation
and every diagram. This is forced rather than chosen. The Claude Code interface renders
GitHub-flavoured markdown and nothing else, so `$\lim_{x\to a} f(x)$` reaches the learner as
literal backslashes and a figure cannot reach them at all. A session run in the terminal does not
merely look worse; its mathematics is unreadable and its diagrams do not exist. Chat is left with
turn-taking — which question is live, that an answer landed, what was written back.

The artifact is converted to markdown into `sessions/` at capture. The narrative lives there; the
state it produced lives in `units.json`. A session that writes one without the other is a bug.

# Data model

## Levels of abstraction (locked)

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

### Unit size

A unit is **one to four hours of study to cover every concept in it once** — roughly a chapter,
or a portion of one where the book is dense. In practice that lands at 6–20 concepts. A unit much
past 25 concepts should be split; `check_vault.py` warns above 25 and errors above 35.

This is the size that makes the rest work: small enough that "study this unit" is a session
rather than a project, large enough that the prerequisite graph over units stays coarse enough
to maintain by hand.

### What a prerequisite edge means

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

### The two dependency graphs

| edge | used for | notes |
|---|---|---|
| **unit → unit** | **the working graph** — eligibility, quiz sampling, study selection | Deliberately coarse. Declared in `units.json`; may cross courses as `<course>:<unit>`. |
| **concept → concept** | **within-session order** — where the sweep goes next | Primarily a linear chain with a few branches. Declared on the concept. **Ordering hints, never gates** — a wrong one costs a slightly odd sweep order, so they do not need to be perfect, only walkable. If a concept graph is heavily non-linear, the unit is probably two units. |

There is no course-level graph. Cross-course dependency is recorded where it is actually
observed — as `external_prereqs` on the concept that has it — and nothing routes on it.

## Course layout

**A course is two files and a directory.** It has no `COURSE.md` and no `map.md`: everything
that was in them either belonged on a unit or was prose, and the prose moved into the header.

### courses/<slug>/units.json

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

#### Header

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

#### `reading`

- `status` is `present` or `missing` — can this unit be run at all. A unit whose reading is not
  in the vault is legal and expected (a course can exist as a plan before it exists as material),
  but the tutor must refuse to run it rather than improvising from nothing.
- `also_read` and `missing_readings` are optional lists, for units that pair a textbook chapter
  with a paper that is (or is not) in the vault.

#### `concepts`

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

#### `stage` — derived, never stored

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

#### `srs` — retrievability-ranked, never due-dated

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

**`lapses` counts every review the learner could not produce cold**: `fail` and `partial` alike,
and a unit's first review too. It is a fact about the review, counted independently of the
stability update. First reviews matter most here, because a unit can be placed high without ever
having been studied, and its first real review is the one worth recording.

Record reviews with `scripts/review.py`, never by hand-editing the numbers.

#### `cursor`

**The load-bearing field.** `concept` is where the sweep reached; `note` is a human-readable
position. With it a session resumes mid-unit; without it the sweep starts at the unit's first
concept and moves fast until it hits friction.

Advance it **as the sweep moves**, not only at the end of a block. That is what makes stopping at
any moment safe.

#### `log`

Append-only. One entry per session that touched the unit: `date`, `what` (a sentence a person
could act on), and `failed` (concept ids that missed). This is where a demotion records *why*.

### courses/<slug>/bank.jsonl

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

### sessions/

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

## Retired

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
