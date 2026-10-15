# Place

Place assigns a unit its starting state: which of its concepts the learner already has, and which they do not.
It runs as the first step of the session that selects an unplaced unit, never as a separate sweep over the vault.

Every question, hint and explanation goes in the session artifact (`skills/session/SKILL.md` → **Everything goes in the artifact**), including a spot-check outside a full session and questions that look like plain prose.

## Placement is a guess, and it errs low

Four questions cannot establish the true state of fifteen concepts, so do not try.
Ask a few questions spread across the unit, then **infer the rest and mark them `unseen` unless you have a reason not to.**

The costs are asymmetric:

- A concept placed **too low** costs one easy session. The sweep passes it in seconds and records it `seen`.
- A concept placed **too high** unblocks material the learner cannot understand yet, and the session fails for reasons neither of you can see. It also makes every question touching it quiz-eligible, so the failure repeats.

## What to write per concept

Write `unseen` by default, for everything you did not positively observe.
Write `seen` only when the learner produced the concept, or produced something that could only come from holding it.
Never write `unknown`.
`seen` does not mean mastered; depth is the SRS's job.

## Choosing the questions

Ask three to six generative questions, spread across the unit's concept graph rather than clustered at its start.
Sample **across depth bands**: one or two near the roots, one or two in the middle, one near the leaves.
Do not open with the deepest concept; it was always the most likely to fail.
Each question asks the learner to state, derive, apply, or contrast a concept with its neighbour.

**Check each question before asking it.**
A malformed question, such as an ambiguity the source resolves two ways, is the author's error.
Score it out and say so rather than recording a miss.

## Do not infer along the graph

A pass on a concept does **not** license marking its ancestors `seen`.
In one placement, eleven of thirteen passes had a directly observed *miss* somewhere among their ancestors.
People learn out of order, forget foundations while keeping results, and hold a conclusion after losing its derivation.
The concept graph orders your questions; it never writes states.

## Writing back

In `courses/<slug>/units.json`, on the unit:

- `placed`: today's date.
- every entry of `concepts`: a `state`.
- `log`: one entry recording that this was a placement, with the questions asked, so a later reader can tell an observed `seen` from an inferred one.

Leave `srs` alone unless the placement was substantial enough to count as a review.
If it was, set `reps` to 1 and `last_seen` to today, and the unit derives to `learning`.

Write `state` and nothing else on a concept.
Its `claim`, `kind`, `prereqs` and `questions` belong to `skills/knowledge-map/SKILL.md`.
