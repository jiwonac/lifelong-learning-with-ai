# Curriculum session

The vault has two kinds of session: the curriculum session in this file, and the ad-hoc session (`skills/ad-hoc/SKILL.md`).
This file is the default entry point.
Use it whenever the user sits down to study ("let's do a session", "I've got an hour", "what's next", "I just listened to X") and whenever they hand back work.

Run an ad-hoc session instead when the user brings one thing to understand: a paper, an autoresearch or literature-review report, or a project task ("explain this", "I don't follow this report", "what's in my learn queue").
A work paper the user wants carded ("card this paper", "which papers should I card") is an ad-hoc session that only cards it, run from `skills/flashcards/SKILL.md` → "Work papers".

Everything else in this vault is a component.
This file decides which components run and in what order.

## The three rules that shape everything

1. **Maximize struggle in the material; remove it everywhere else.**
   Silently absorb all difficulty in deciding what to study, finding the source, checking claims, and tracking coverage.
   Never open by asking what they want to work on; tell them, and let them override.
2. **Any duration must work.**
   Nothing builds a backlog and no session needs reorientation.
   The unit `cursor` makes this work, and keeping it accurate is the most important bookkeeping in this file.
3. **Everything the learner reads goes in the artifact, not in chat.**
   This covers quiz, placement, study, and any one-off question-and-answer exchange.
   See **Everything goes in the artifact** below.

There is **no time estimation anywhere**.
Do not ask for a session length, check a unit against a budget, or give a block a duration.
The session ends when the user says so.

## The shape of a session

Every session is **about one unit**; a unit blocked by a prerequisite hands the session to that prerequisite, recursively.
Every step is generative (`CLAUDE.md` → Universal Rules).

    0. place    — if the chosen unit has never been placed, place it
    1. quiz     — a handful of bank questions, urgency-ranked, asked one at a time
    2. study    — sweep the unit from its cursor, teach at friction
    3. capture  — write state back into units.json and the session file

## Opening

Run `python3 scripts/session.py` for the quiz draw and the study pick.
If the `anki` MCP tools are connected, also pull suspended leeches into the quiz (`skills/flashcards/SKILL.md` → "Leeches → the quiz").
Read the rules below when you need to override the script or when its output is surprising.

### 0. Place, if the unit has never been placed

A unit at stage `unknown` gets placed as the first step of the session that selects it, never in a separate pass over the vault.
Follow `skills/place/SKILL.md`.

### 1. Quiz: spaced repetition over the bank

Ask the drawn questions **one at a time, in the artifact**, with only a pointer in chat.
Wait for an answer before revealing anything.
Grade and route each answer with `skills/grader/SKILL.md`.

### 2. Study: sweep the unit, teach at friction

**Name the unit and its course, then confirm**; the user may want something else.

The course stage of the draw ignores history, so three sessions in a row from one course is ordinary.
When the pick looks surprising, pass on what `session.py` prints: the course probabilities, the recent mix, and the runner-up units.
**Naming a course overrides the draw entirely.** This is the intended remedy for an unlucky streak.

Then teach with `skills/tutor/SKILL.md`: it owns the "have you read this recently?" question, the sweep-and-teach cycle and the stop rules. Refuse a unit whose reading is `missing` (`CLAUDE.md` rule 4).

**Advance or deepen? Do not decide this by hand.**
A concept just taught is `seen`; the SRS brings it back on schedule, and a second failure demotes it.
Re-teaching at once buys a scaffolded success and gives up the spacing that would have fixed it.

### 3. Capture

A session that skips capture loses its work.
Record the review with `scripts/review.py`, which writes `cursor`, concept states (including quiz demotions), `srs` and the `log` entry into `units.json`.
Advance the cursor as the sweep moves, not at the end.
Then convert the artifact to markdown in `sessions/`, named as in `CLAUDE.md` → "sessions/".

## Everything goes in the artifact

**Every session gets one**, published as it goes rather than assembled at the end.
This applies to any generative question-and-answer exchange in this vault, including an ad hoc spot-check or a partial re-verification.
The terminal renders no LaTeX and no images, so notation arrives as literal backslashes and diagrams do not arrive at all.

The split does not depend on how much notation a question carries:

| goes in the artifact | stays in chat |
|---|---|
| the question, in full | which question is live: "question 3 of 8 is up" |
| the learner's answer, as given | that an answer landed, and the one-word verdict |
| the hint, and what it did or did not unlock | what got written back: grade, demotion, ids |
| the answer key, and why the cold answer missed it | the study pick, and the offer to override |
| every derivation, equation, diagram and worked example, including the unit's concept graph | "gtg", and everything about running the session |
| the standing observations about how this learner fails | |

**Write the artifact first, then speak.**
Publish the question, then say it is up.
Publish the grading, then say how it routed.
If a chat turn contains a `$`, a `\frac`, a subscript, or a shape described in words, it is in the wrong place.

**Record answers verbatim**, including any wrong turn before the learner self-corrected.
The wrong turn is usually the diagnostic part, and without it a later reader cannot tell decay from a bad cut.

## "gtg"

The user can end a session at any moment, mid-concept or mid-question.
That triggers capture at once: cursor, concept states, SRS, log, session file.

Next, if the `anki` tools are connected, **propose flashcards** from the session (and a cleanup batch when one is due), wait for the learner's one feedback turn, then add and sync (`skills/flashcards/SKILL.md`).
Without Anki, skip this silently.

Then **ship it to `main` without asking**; saying "gtg" counts as the user's request for the PR and the merge.
This step assumes a GitHub remote and either the GitHub MCP tools or the `gh` CLI; delete it if you would rather review each session's changes yourself.

1. `python3 scripts/check_vault.py`: zero errors, or stop and report instead of merging.
2. Commit everything outstanding on the session's branch and push it.
3. Open a PR into `main` (title `<unit-id>: <what happened>`, body = the `log` entry) and merge it with a merge commit, not a squash: the per-concept commits are the cursor's audit trail. Use the GitHub MCP tools where they exist (cloud sessions), `gh pr create` / `gh pr merge --merge` otherwise (local sessions).
4. Report the PR link and that it merged, in one line.

If the merge is refused (conflict, protection, a red check), leave the PR open and say why; never force anything.
If the user keeps studying after a merge, the next "gtg" restarts the branch from the updated `main` and opens a fresh PR.
Never reuse a merged PR.

## Notes

- Use **subagents for the reading-heavy parts**, such as a large source or drafting bank questions, so only structured writes touch the working tree.
- A unit with an empty `concepts` array can still be studied, but the sweep has no order and the quiz falls back to unit granularity. Say so and offer to cut its concepts (`skills/knowledge-map/SKILL.md`).
