# Place

Place assigns a unit its starting state: which of its concepts the learner already has, and which they do not.
It runs as the first step of the session that selects an unplaced unit, never as a separate sweep over the vault.

A unit at stage `unknown` has never been assessed, so nothing about it can be trusted.
It cannot be quizzed, because no question from it is fair.
Studying it means starting from concept one, wherever the gap actually is.
Placement makes it schedulable.

## Everything you write goes in the artifact

Publish every question, hint, derivation, diagram and word of explanation to the session artifact.
Chat carries only the pointer and the turn-taking.
The interface renders GitHub-flavoured markdown with no LaTeX and no images, so notation sent to the terminal arrives as literal backslashes and a figure does not arrive at all.
`skills/session/SKILL.md` -> **Everything goes in the artifact** is the full rule.
It applies here too, including to questions that look like plain prose.

## Placement is a guess, and it errs low

Four questions cannot establish the true state of fifteen concepts, so do not try.
Ask a few questions spread across the unit, then **infer the rest and mark them `unseen` unless you have a reason not to.**

The costs are asymmetric:

- A concept placed **too low** costs one easy session. The sweep passes it in seconds, records it `seen`, and moves on.
- A concept placed **too high** unblocks material the learner cannot understand yet, and the session fails for reasons neither of you can see. It also makes every question touching it eligible for the quiz, so the failure repeats.

So when in doubt, `unseen`.

## The three states

| state | means | when to write it |
|---|---|---|
| `unknown` | not placed | only before placement — never write this |
| `unseen` | placed, and not studied | the default; everything you did not positively observe |
| `seen` | studied at least once | the learner produced it, or produced something that could only come from holding it |

`seen` does not mean mastered.
It means the material has been through the learner's head at least once, which is what the quiz needs to know before it may ask about it.
Depth is the SRS's job.

## Choosing the questions

Ask three to six generative questions, spread across the unit's concept graph rather than clustered at its start.
Sample **across depth bands**: one or two near the roots, one or two in the middle, one near the leaves.
Opening with the deepest concept tells you almost nothing, because it was always the most likely to fail.

**No multiple choice.**
The learner's own reading handles recognition.
Every placement question requires the learner to state, derive, apply, or contrast a concept with its neighbour.

**Check each question before asking it.**
A malformed question, such as four equivalent options or an ambiguity the source resolves two ways, is the author's error.
Score it out and say so rather than recording a miss, since a miss on a malformed question corrupts the placement.

**Publish the artifact.**
Any exchange of generative questions and answers, including an ad hoc spot-check outside a full session, gets a published artifact with the questions, the answers, and any heavy notation.
Keep it live as the exchange happens, as in `skills/session/SKILL.md`.

## Do not infer along the graph

A pass on a concept does **not** license marking its ancestors `seen`.
In one placement, eleven of thirteen passes had a directly observed *miss* somewhere among their ancestors.
People learn out of order, forget foundations while keeping results, and hold a conclusion after losing its derivation.

The concept graph orders your questions.
It never writes states.

## Writing back

In `courses/<slug>/units.json`, on the unit:

- `placed`: today's date.
- every entry of `concepts`: a `state`.
- `log`: one entry recording that this was a placement, with the questions asked. A later reader must be able to tell an observed `seen` from an inferred one.

Leave `srs` alone unless the placement was substantial enough to count as a review.
If it was, set `reps` to 1 and `last_seen` to today, and the unit derives to `learning`.

Write `state` and nothing else on a concept.
Its `claim`, `kind`, `prereqs` and `questions` are structure and belong to `skills/knowledge-map/SKILL.md`.
