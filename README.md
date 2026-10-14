# Learning Vault

This is a custom learning system that I created to equip AI agents with learning science principles and a structured personal learning curriculum. 
I use it to learn new courses for my PhD and for personal projects. 

## General Principles

This system 

## Old Introduction

A study system built out of files and a handful of scripts, driven from Claude Code with write
access to this repo. You bring the sources and do the reading; the vault decides what to study
next, teaches at the point where understanding actually stops, quizzes what you covered before,
and records the result.

The principle everything here follows: **maximize struggle in the material, and eliminate it
everywhere else.** Difficulty in the ideas is the point. Difficulty in deciding what to study,
finding the source, checking whether a claim is true, or tracking what's been covered is waste,
and the system absorbs it. If you are thinking about the system, the system is malfunctioning.

The second constraint, which shapes more of the design than the first: **any duration must
work.** Thirty minutes some days, three hours others, nothing for a fortnight. Nothing here
accumulates a backlog and no session needs reorientation to start.

## Getting started

1. Clone the repository (or make your own copy of it) and open it in Claude Code with write
   access. The scripts are standard-library Python 3, so there is nothing to install.
2. Run `python3 scripts/check_vault.py`. It must report 0 errors. The SessionStart hook in
   `.claude/hooks/` runs it at the start of every session too.
3. Run `python3 scripts/session.py` to see what the scheduler would pick. The repository ships
   with one example course, `courses/example/`: a single unit on binary search, with short
   original notes and five bank questions. Say "let's do a session" to try a full session on it,
   and delete the course once you have your own.
4. Add a course by asking Claude for one; `skills/course/SKILL.md` covers creating it and
   cutting it into units. Put your readings (PDFs, papers, notes) in `courses/<slug>/sources/`.
   No sources are included in this repository. Do not commit copyrighted books or papers to a
   public repository: keep your copy private, or keep `sources/` out of git.
5. Optionally, set up Anki flashcards and the Raindrop.io paper integration with
   `skills/flashcards/SETUP.md`. Without them, sessions skip every flashcard step and nothing
   else changes.

Sessions put everything you read on a published Artifact page (see "On the interface" below), so
they need a Claude Code setup where the Artifact tool is available. Ending a session with "gtg"
commits, opens a pull request and merges it into `main`. That step assumes the repository has a
GitHub remote and that the `gh` CLI is logged in (or the GitHub MCP tools are connected); without
them, commit by hand or remove the step from `skills/session/SKILL.md`.

## Three levels, locked

| level | is | lives in |
|---|---|---|
| **Course** | a broad topic — "Database Internals" | `courses/<slug>/` |
| **Unit** | a subtopic — "Two-pass sort/hash algorithms" | a record in `units.json` |
| **Concept** | one claim or one skill | an entry in a unit's `concepts`, in `units.json` |

Do not invent a fourth. Anything that seems to need one is a unit or a concept cut at the wrong
grain. `SCHEMA.md` is authoritative for all of this.

**The unit is the only scheduled object.** It carries its own reading, prerequisites, priority,
spaced-repetition state, cursor, concept states, questions and history — everything the scheduler
needs. A **course is a list of units** plus the material they share (a bank and a sources
directory); it has no state of its own. A unit is **one to four hours to cover every concept in
it once**, which in practice is 6–20 concepts.

A unit's **stage** is derived from its own data, never stored: `unknown` (never placed) → `new`
(placed, studied zero times) → `learning` (studied at least once) → `learned` (every concept
seen). Concept states are `unknown | unseen | seen`. There is no mastery ladder; depth is the
SRS's job.

## How a session runs

Say "let's do a session" (or "I've got an hour", or "what's next") and
`skills/session/SKILL.md` takes over. Every session is about **one unit**; if that unit is
blocked by a prerequisite, the prerequisite becomes the unit, and that recursion is the whole
curriculum.

1. **Place** — if the unit has never been assessed, a few generative questions spread across its
   concepts, then guess the rest. Placement errs low on purpose (`skills/place/SKILL.md`).
2. **Quiz** — a handful of bank questions from other units, asked one at a time in chat
   (`skills/grader/SKILL.md` marks and routes them).
3. **Study** — give the unit's broad picture in plain words, sweep its concepts from the
   `cursor`, fast, teach at the first friction while returning to the broad picture as each
   concept lands, and close with a synthesis round (`skills/tutor/SKILL.md`).
4. **Capture** — write `cursor`, concept states, `srs` and a `log` entry into `units.json`, and
   the session artifact into `sessions/`. Saying "gtg" then commits, opens a PR and merges it
   to `main`, gated on `check_vault.py` reporting zero errors.

**Every question in this vault is generative.** No multiple choice anywhere — recognition is what
your own reading is for.

**Repair is not a separate mechanism.** A concept that fails cold twice goes back to `unseen`,
which drops its unit out of `learned` and returns it to the study pool on its own.

### Ad hoc needs: explain sessions

A paper you are about to read, an autoresearch report full of unfamiliar concepts, or a project
task is not a unit, and the scheduler never sees it. Say "explain this" and
`skills/explain/SKILL.md` runs instead: it maps the concepts the material depends on, skips the
ones the vault shows you already have, and teaches the rest. At the end it sorts each concept
taught into what already exists: nowhere, a flashcard, a concept on an existing unit, or, once a
topic has come up in more than one explain session, a new unit. Nothing new is scheduled, so
there is no ad hoc backlog. With the optional Raindrop integration, things to understand later
wait under the `learn` tag in Raindrop, which nothing shows you unless you ask.

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
exactness by turning the rotation into a cycle you could recite, and it needs a session history to
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
  SCHEMA.md          # authoritative data formats and the three locked levels
  DECISIONS.md       # dated design decisions and why
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
