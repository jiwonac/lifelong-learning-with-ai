# Curriculum session

The vault has two kinds of session: the curriculum session in this file, and the ad-hoc session (`skills/ad-hoc/SKILL.md`).
This file is the default entry point.
Use it whenever the user sits down to study ("let's do a session", "I've got an hour", "what's next", "I just listened to X") and whenever they hand back work.

Run an ad-hoc session instead when the user brings one thing to understand: a paper they are about to read or just read, an autoresearch or literature-review report, or a project task ("explain this", "I don't follow this report", "what's in my learn queue").
A work paper the user wants carded ("card this paper", "which papers should I card") is an ad-hoc session that only cards it, run from `skills/flashcards/SKILL.md` → "Work papers".

Everything else in this vault is a component.
This file decides which components run and in what order.

## The three rules that shape everything

1. **Maximize struggle in the material; remove it everywhere else.**
   Do not soften difficulty in the ideas.
   Absorb, silently, all difficulty in deciding what to study, finding the source, checking whether a claim is true, and tracking what has been covered.
   If the user is thinking about the system, the system is failing.
   Never open by asking what they want to work on; tell them, and let them override.
2. **Any duration must work.**
   The user may study thirty minutes some days, three hours others, and nothing for a fortnight.
   Nothing builds a backlog and no session needs reorientation.
   The unit `cursor` makes this work, and keeping it accurate is the most important bookkeeping in this file.
3. **Everything the learner reads goes in the artifact, not in chat.**
   Every question, answer, derivation, diagram, grading note and word of teaching goes to the session artifact.
   This covers quiz, placement and study, and any one-off question-and-answer exchange.
   The reason: this interface renders GitHub-flavoured markdown only, with no LaTeX and no images, so `$\lim_{x\to a} f(x)$` arrives as literal backslashes and a diagram does not arrive at all.
   See **Everything goes in the artifact** below for what chat is still for.

There is **no time estimation anywhere**.
Do not ask for a session length, check a unit against a budget, or give a block a duration.
The session ends when the user says so, and the cursor makes that safe at any moment.

## The shape of a session

Every session is **about one unit**.
If that unit is blocked by a prerequisite, the prerequisite becomes the unit, recursively.

    0. place    — if the chosen unit has never been placed, place it
    1. quiz     — a handful of bank questions, urgency-ranked, asked one at a time
    2. study    — sweep the unit from its cursor, teach at friction
    3. capture  — write state back into units.json and the session file

**All four steps are generative.**
There is no multiple choice anywhere in this vault.
The user's own reading handles recognition, and every question the system asks requires the learner to produce an answer.

## Opening

Run `python3 scripts/session.py`.
It ranks every unit by `(1 − retrievability) × priority` and returns the quiz draw and the study pick.
If the `anki` MCP tools are connected, also pull suspended leeches into the quiz (`skills/flashcards/SKILL.md` → "Leeches → the quiz").
Read the rules below when you need to override the script or when its output is surprising.

### 0. Place, if the unit has never been placed

A unit at stage `unknown` has never been assessed, so neither its eligibility nor its questions can be trusted.
Placing it is the first step of the session that selects it, never a separate pass over the vault.

Placement is a **guess** from a few questions spread across the unit's concepts, and it **errs low**.
A unit placed too low costs one easy session.
A unit placed too high unblocks material the learner cannot understand yet, and the session fails for reasons neither of you can see.
When in doubt, mark the concept `unseen`.

Write `placed`, then a `state` for every concept: `seen` for what the user demonstrably has, `unseen` for the rest.
See `skills/place/SKILL.md`.

### 1. Quiz: spaced repetition over the bank

The quiz is where retention happens and where a decayed unit gets caught.

`scripts/session.py` draws units by urgency and one question from each.
The code enforces two rules:

- **Only `learning` and `learned` units are drawn.** A `new` unit has never been studied, so a question from it measures nothing and feels like failure.
- **Only questions whose concepts have all been `seen`.** A question in an eligible unit can still reach concepts the sweep has not covered. Skip those.

Ask the questions **one at a time, in the artifact**: the full question goes there, and chat carries only the pointer.
Wait for an answer before revealing anything.
This holds for plain-prose questions too, so the learner reads one surface.

**A miss is data**, and it routes:

| what happened | what to write |
|---|---|
| careless slip, knew it on sight | nothing — never demote on a slip |
| could not retrieve, but rebuilt it with a hint | `srs.lapses += 1`; leave the concept `seen` |
| could not retrieve or rebuild | concept back to `unseen`, `srs.lapses += 1`, name it in `log.failed` |

The last row is the repair mechanism.
Enough concepts back to `unseen` drops the unit out of `learned`, and it re-enters the study pool on its own.
There is no separate repair path.

### 2. Study: sweep the unit, teach at friction

`scripts/session.py` names one unit and its course.
**Say both, then confirm**; the user may want something else.

The pick is a two-stage random draw, and the course stage is **independent of history**.
Three sessions in a row from the same course is ordinary, and so is a fortnight without one.
`session.py` prints the course probabilities, the recent mix, and the runner-up units: pass these on when the pick looks surprising.
**Naming a course overrides the draw entirely.** This is the intended remedy for an unlucky streak.

Then repeat the cycle:

> **sweep** forward through the unit's concepts from the `cursor`, fast — **hit friction** —
> **teach** that concept — **resume the sweep**

Several cycles per session is normal.
The sweep is cheap and exists only to find where teaching should happen.
Where the concept graph forks, sweep both branches, since neither implies the other.

**Ask first: "have you read this recently?"**
If yes, go straight to testing concepts.
If no, the user reads during the session; that is part of the block and may take most of it.
The answer changes between sessions, so always ask and never store it.

Acquisition, consolidation and repair are one workflow applied to units in different states.
Nothing branches on which it is.

**Stop rules.**

- Never advance past a failed check. Split the step and re-teach the smaller half.
- A concept that fails twice after splitting is a missing prerequisite. Stop and find what is missing; if it lives in another unit, that unit is the next session.
- If `reading.status` is `missing`, refuse rather than improvise.

**Advance or deepen?** Do not decide this by hand.
A concept just taught is `seen`; the SRS brings it back on schedule, and a second failure demotes it.
Re-teaching at once buys a scaffolded success and gives up the spacing that would have fixed it.

### 3. Capture

A session that skips capture loses its work.
Everything lands in **`units.json`**, one file per course:

- **`cursor`**: the concept the sweep reached, and a note a person could act on. Advance it as the sweep moves, not at the end, so stopping is always safe.
- **concept `state`s**: `seen` for everything covered, plus demotions from the quiz.
- **`srs`**: `last_seen`, `reps += 1`, `lapses`, updated `difficulty` and `stability`.
- **`log`**: one entry with the date, what happened in a sentence, and the concepts that failed.

Then convert the session artifact to markdown and write it to `sessions/<YYYY-MM-DD-HHMM>-<unit-id>.md`.
The narrative lives there; the state lives in git.

## Everything goes in the artifact

**Every session gets one**, published as it goes rather than assembled at the end.
This applies to any generative question-and-answer exchange in this vault, including an ad hoc spot-check or a partial re-verification.

The division does not depend on how much notation a question carries:

| goes in the artifact | stays in chat |
|---|---|
| the question, in full | which question is live — "question 3 of 8 is up" |
| the learner's answer, as given | that an answer landed, and the one-word verdict |
| the hint, and what it did or did not unlock | what got written back — grade, demotion, ids |
| the answer key, and why the cold answer missed it | the study pick, and the offer to override |
| every derivation, equation, diagram and worked example | "gtg", and everything about running the session |
| the standing observations about how this learner fails | |

**Write the artifact first, then speak.**
Answering in chat and copying across afterwards loses the notation and always loses the figures.
Publish the question, then say it is up.
Publish the grading, then say how it routed.

Chat is a control channel.
If a chat turn contains a `$`, a `\frac`, a subscript, or a shape described in words, it is in the wrong place.

**Record answers verbatim.**
Write what the learner actually wrote, including any wrong turn before they self-corrected.
A record of only the corrected version cannot later tell decay from a bad cut, and the wrong turn is usually the diagnostic part.

The artifact also holds anything visual: diagrams, equations, worked derivations, the unit's concept graph.
Questions are asked there one at a time, and the artifact is the record.

## "gtg"

The user can end a session at any moment, mid-concept or mid-question, by saying so.
That triggers capture at once: cursor, concept states, SRS, log, session file.
Nothing depends on a session finishing what it opened.

Next, if the `anki` tools are connected, **propose flashcards** from the session (and a cleanup batch when one is due), wait for the learner's one feedback turn, then add and sync (`skills/flashcards/SKILL.md`).
Without Anki, skip this silently.

Then **ship it to `main` without asking**.
Saying "gtg" counts as the user's explicit request for the PR and the merge.
This step assumes the repo has a GitHub remote and that either the GitHub MCP tools or the `gh` CLI are available; delete it if you would rather review each session's changes yourself.

1. `python3 scripts/check_vault.py`: zero errors, or stop and report instead of merging.
2. Commit everything outstanding on the session's branch and push it.
3. Open a PR into `main` (title `<unit-id>: <what happened>`, body = the `log` entry) and merge it with a merge commit, not a squash: the per-concept commits are the cursor's audit trail. Use the GitHub MCP tools where they exist (cloud sessions), `gh pr create` / `gh pr merge --merge` otherwise (local sessions).
4. Report the PR link and that it merged, in one line.

If the merge is refused (conflict, protection, a red check), leave the PR open and say why; never force anything.
If the user keeps studying after a merge, the next "gtg" restarts the branch from the updated `main` and opens a fresh PR.
Never reuse a merged PR.

## Notes

- Run `python3 scripts/check_vault.py` after any session that writes structure. Zero errors.
- Use **subagents for the reading-heavy parts**, such as working through a large source or drafting bank questions, so only structured writes touch the working tree.
- A unit with an empty `concepts` array can still be studied, but the sweep has no order and the quiz falls back to unit granularity. Say so and offer to cut its concepts (`skills/knowledge-map/SKILL.md`).
- A unit whose reading is `missing` cannot be studied. It stays in the vault as a placeholder and the scheduler skips it.
