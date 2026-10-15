# Curriculum session

The vault has two kinds of session: the curriculum session in this file, and the ad-hoc session
(`skills/ad-hoc/SKILL.md`). This is the default entry point. Use it whenever the user sits down
to study ("let's do a session", "I've got an hour", "what's next", "I just listened to X") and
whenever they hand back work.

Run an ad-hoc session instead when the user brings one thing to understand: a paper they are
about to read or just read, an autoresearch or literature-review report, or a project task
("explain this", "I don't follow this report", "what's in my learn queue"). A work paper the user
wants carded ("card this paper", "which papers should I card") is an ad-hoc session that only
cards it, run from `skills/flashcards/SKILL.md` → "Work papers".

Everything else in this vault is a component. This file decides which components run and in what
order.

## The three rules that shape everything

**1. Maximize struggle in the material; eliminate it everywhere else.** Difficulty in the ideas
is the point and must not be softened. Difficulty in deciding what to study, finding the source,
checking whether a claim is true, tracking what's been covered — that is pure waste and this
skill absorbs it silently. If the user is thinking about the system, the system is malfunctioning.
Never open by asking what they want to work on; open by telling them, and let them override.

**2. Any duration must work.** The user studies in whatever gaps exist — thirty minutes some days,
three hours others, nothing for a fortnight. Nothing accumulates a backlog and no session requires
reorientation. That is what the unit `cursor` is for, and keeping it good is the single most
important bookkeeping act in this file.

**3. Everything the learner reads goes in the artifact, not in chat.** Every question, every
answer, every derivation, every diagram, every grading note and every word of teaching is written
to the session artifact. Quiz, placement and study alike, and any one-off question-and-answer
exchange too. The reason is not taste: **this interface renders GitHub-flavoured markdown and
nothing else** — no LaTeX, no image surface — so `$\lim_{x\to a} f(x)$` arrives as literal
backslashes and a diagram does not arrive at all. A session conducted in chat is not slightly
worse-looking; its mathematics is unreadable and its figures do not exist. See **Everything goes
in the artifact** below for what chat is still for.

There is **no time estimation anywhere**. No session length is asked for, no unit is checked
against a budget, no block has a duration. The session ends when the user says it ends, and the
cursor makes that safe at any moment.

## The shape of a session

Every session is **about one unit**. If that unit turns out to be blocked by a prerequisite, the
prerequisite becomes the unit, and so on down. That recursion is the whole curriculum.

    0. place    — if the chosen unit has never been placed, place it
    1. quiz     — a handful of bank questions, urgency-ranked, asked one at a time
    2. study    — sweep the unit from its cursor, teach at friction
    3. capture  — write state back into units.json and the session file

**All four steps are generative.** No multiple choice anywhere in this vault: recognition is
handled by the user's own immersive reading, and every question the system asks requires a
production. There is no separate "generative close" because there is nothing non-generative to
distinguish it from.

## Opening

Run `python3 scripts/session.py`. It ranks every unit by `(1 − retrievability) × priority` and
returns the quiz draw and the study pick. If the `anki` MCP tools are connected, also pull suspended
leeches into the quiz (`skills/flashcards/SKILL.md` → "Leeches → the quiz"). Read the rules below when you need to override it or
when it says something surprising.

### 0. Place, if the unit has never been placed

A unit at stage `unknown` has never been assessed, so nothing about it can be trusted — not its
eligibility, not its questions. Placing it is the opening move of the session that selects it,
not a separate pass over the vault.

Placement is a **guess**, made from a few questions spread across the unit's concepts, and it
**errs low**. A unit placed too low costs one easy session. A unit placed too high unblocks
material that cannot be understood yet and produces a session that fails for reasons neither of
you can see. When in doubt, mark the concept `unseen`.

Write `placed`, then a `state` for every concept: `seen` for what the user demonstrably has,
`unseen` for the rest. See `skills/place/SKILL.md`.

### 1. Quiz — spaced repetition over the bank

Not a warm-up, not a formality: this is where retention actually happens, and where a decayed
unit gets caught.

`scripts/session.py` draws units by urgency and one question from each. Two rules make the draw
honest, and both are enforced in code rather than left to judgement:

- **Only `learning` and `learned` units are drawn.** A `new` unit has been studied zero times, so
  a question from it would be a test of never-learned material — which measures nothing and feels
  like failure.
- **Only questions whose concepts have all been `seen`.** Within an eligible unit, a question can
  still reach concepts the sweep never got to. Those are skipped, not asked.

Ask them **one at a time, in the artifact** — the question published there in full, chat carrying
only the pointer to it. Wait for an answer before revealing anything. This holds for a plain-prose
question as much as a notation-heavy one: the learner should be reading one surface, not deciding
each turn which of two to look at.

**A miss is data, not a failure**, and it routes:

| what happened | what to write |
|---|---|
| careless slip, knew it on sight | nothing — never demote on a slip |
| could not retrieve, but rebuilt it with a hint | `srs.lapses += 1`; leave the concept `seen` |
| could not retrieve or rebuild | concept back to `unseen`, `srs.lapses += 1`, name it in `log.failed` |

That last row **is** the repair mechanism. Enough concepts back to `unseen` drops the unit out of
`learned`, and it re-enters the study pool on its own. There is no repair course, no spur, and no
second code path.

### 2. Study — sweep the unit, teach at friction

One unit. `scripts/session.py` names it and its course; **say both, then confirm** — the user may
want something else, and honouring that costs nothing.

The pick is a two-stage random draw, and the course stage is **independent of history**. A run of
three sessions from the same course is ordinary, not a malfunction, and neither is a fortnight without
one. `session.py` prints the course probabilities, the recent mix, and the runners-up the unit was
drawn over: pass those on when the pick looks surprising. **Naming a course overrides the draw
entirely** — that is the intended remedy for an unlucky streak, and it is cheaper than any
scheduler that could not produce one.

Then the repeating cycle:

> **sweep** forward through the unit's concepts from the `cursor`, fast — **hit friction** —
> **teach** that concept — **resume the sweep**

Several cycles per session is normal. Passes cost seconds; the expensive part is the teaching,
and the sweep exists only to find where it should happen. Where the concept graph forks, sweep
both branches — parallel branches are parallel precisely because neither implies the other.

**Ask first: "have you read this recently?"** If yes, go straight to concept-testing. If no, the
user reads *during the session* — that is part of the block, not a prerequisite to it, and it may
take most of it. The answer changes between sessions, so it is established by asking and never
stored.

There is **one workflow**. Acquisition, consolidation and repair are the same activity applied to
units in different states; nothing branches on which it is.

**Stop rules.** Never advance past a failed check — split the step and re-teach the smaller half.
A concept that fails twice after splitting is a missing prerequisite, not a hard concept: stop,
find what is missing, and if it lives in another unit, that unit is the next session. If
`reading.status` is `missing`, refuse rather than improvise.

**Advance or deepen?** Don't decide this by hand. A concept just taught is `seen`; the SRS brings
it back on its own schedule, and a second failure demotes it. Re-teaching immediately buys a
scaffolded success and forgoes the spacing that would have fixed it.

### 3. Capture

Non-negotiable; a session that skips this loses its work. Everything lands in **`units.json`** —
one file per course, one place for all state:

- **`cursor`** — the concept the sweep reached and a note a person could act on. Advance it *as
  the sweep moves*, not at the end, so stopping is always safe.
- **concept `state`s** — `seen` for everything covered, demotions from the quiz.
- **`srs`** — `last_seen`, `reps += 1`, `lapses`, updated `difficulty` and `stability`.
- **`log`** — one entry: date, what happened in a sentence, and the concepts that failed.

Then the session artifact is converted to markdown and written to
`sessions/<YYYY-MM-DD-HHMM>-<unit-id>.md`. The narrative lives there; the state lives in git.

## Everything goes in the artifact

**Every session gets one**, published as it goes rather than assembled at the end. This applies to
any generative question-and-answer exchange run through this vault, not only a full
place/quiz/study/capture pass: an ad hoc spot-check or a partial re-verification gets one too.

The division is absolute, and it is not a matter of how much notation a particular question
happens to carry:

| goes in the artifact | stays in chat |
|---|---|
| the question, in full | which question is live — "question 3 of 8 is up" |
| the learner's answer, as given | that an answer landed, and the one-word verdict |
| the hint, and what it did or did not unlock | what got written back — grade, demotion, ids |
| the answer key, and why the cold answer missed it | the study pick, and the offer to override |
| every derivation, equation, diagram and worked example | "gtg", and everything about running the session |
| the standing observations about how this learner fails | |

**Write the artifact first, then speak.** The habit that fails is answering in chat and copying
the good parts across afterwards, which reliably loses the notation and always loses the figures.
Publish the question, then say it is up. Publish the grading, then say how it routed.

Chat is a control channel. If a chat turn contains a `$`, a `\frac`, a subscript or a shape being
described in words, it is in the wrong place.

**Verbatim answers.** Record what the learner actually wrote, not a tidied paraphrase — including
the wrong turn they took before self-correcting. A session record that only shows the corrected
version cannot tell decay from a bad cut later, and the wrong turn is usually the diagnostic part.

It is also where anything visual goes: diagrams, equations, worked derivations, the unit's
concept graph. That is what replaced the old practice of composing a test document to be solved
in another application — the questions are asked here, one at a time, and the artifact is the
record rather than the medium.

## "gtg"

The user can end a session at any moment by saying so, mid-concept and mid-question. That
triggers capture immediately: cursor, concept states, SRS, log, session file. Nothing downstream
depends on a session finishing what it opened.

Next, if the `anki` tools are connected, **propose flashcards** from the session (and a cleanup
batch when one is due), wait for the learner's one feedback turn, add and sync
(`skills/flashcards/SKILL.md`). Without Anki, skip this silently.

Then **ship it to `main` without asking**. This is the vault's standing instruction, and saying
"gtg" counts as the user's explicit request for the PR and the merge. It assumes the repo has a
GitHub remote and that either the GitHub MCP tools or the `gh` CLI are available; delete this
step if you would rather review each session's changes yourself.

1. `python3 scripts/check_vault.py` — zero errors, or stop and report instead of merging.
2. Commit everything outstanding on the session's branch and push it.
3. Open a PR into `main` (title `<unit-id>: <what happened>`, body = the `log` entry) and merge it
   with a merge commit, not a squash: the per-concept commits are the cursor's audit trail. Use the GitHub MCP tools where they exist (cloud
   sessions), `gh pr create` / `gh pr merge --merge` otherwise (local sessions).
4. Report the PR link and that it merged, in one line.

If the merge is refused (conflict, protection, a red check), leave the PR open and say why; never
force anything. If the user keeps studying after a merge, the next "gtg" restarts the branch from
the updated `main` and opens a fresh PR — a merged PR is never reused.

## Notes

- Run `python3 scripts/check_vault.py` after any session that writes structure. Zero errors.
- **Subagents for the reading-heavy parts** — working through a large source, drafting bank
  questions — so only structured writes touch the working tree.
- A unit with an empty `concepts` array can still be studied, but the sweep has no order and the
  quiz falls back to unit granularity. Say so and offer to cut its concepts
  (`skills/knowledge-map/SKILL.md`).
- A unit whose reading is `missing` cannot be studied. It stays in the vault as an honest
  placeholder and the scheduler skips it.
