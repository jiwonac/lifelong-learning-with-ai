# Place

Assigns a unit its starting state: which of its concepts the learner already has, and which they
do not. Runs as the opening move of the session that selects an unplaced unit — never as a
separate sweep over the vault.

A unit at stage `unknown` has never been assessed, so nothing about it can be trusted. It cannot
be quizzed (no question from it is fair), and studying it means starting from concept one whether
or not that's where the gap is. Placement is what converts it into something schedulable.

## Everything you write goes in the artifact

Not in chat. Every question you ask, every hint, every derivation, every diagram and every word of
explanation is published to the session artifact, and chat carries only the pointer and the
turn-taking. The interface renders GitHub-flavoured markdown with no LaTeX and no image surface,
so notation sent to the terminal arrives as literal backslashes and a figure does not arrive at
all. `skills/session/SKILL.md` -> **Everything goes in the artifact** is the full rule; it is not
optional here and it does not relax for questions that look like plain prose.

## Placement is a guess, and it errs low

You will not establish the true state of fifteen concepts with four questions, and you should not
try. Ask a few questions spread across the unit, then **infer the rest and mark them `unseen`
unless you have a reason not to.**

The asymmetry is the point:

- A concept placed **too low** costs one easy session. The sweep passes it in seconds, records it
  `seen`, and moves on. Cheap.
- A concept placed **too high** unblocks material that cannot be understood yet, and produces a
  session that fails for reasons neither of you can see. It also makes every question touching it
  eligible for the quiz, so the failure repeats.

So when in doubt, `unseen`. The sweep is fast enough that over-placing is nearly free to correct
and under-placing is not.

## The three states

| state | means | when to write it |
|---|---|---|
| `unknown` | not placed | only before placement — never write this |
| `unseen` | placed, and not studied | the default; everything you did not positively observe |
| `seen` | studied at least once | the learner produced it, or produced something that could only come from holding it |

`seen` is not "mastered" and not "solid" — those rungs do not exist any more. It means the
material has been through the learner's head at least once, which is exactly what the quiz needs
to know before it is allowed to ask about it. Depth is the SRS's job, not placement's.

## Choosing the questions

Three to six, generative, spread across the unit's concept graph rather than clustered at its
start. Sample **across depth bands** — one or two near the roots, one or two in the middle, one
near the leaves. A placement that opens with the deepest concept in the unit tells you almost
nothing, because it was always the most likely to fail.

**No multiple choice.** Recognition is handled by the learner's own reading. Every placement
question requires a production: state it, derive it, apply it, contrast it with its neighbour.

**Write the questions carefully, and check them before asking.** A malformed question — four
options that are all equivalent, an ambiguity the source resolves two different ways — is the
author's error, not the learner's. Score it out and say so rather than recording a miss. A miss recorded on a
malformed question corrupts the placement.

**Publish the artifact.** This runs the same rule as `skills/session/SKILL.md`: any exchange of
generative questions and answers, placement or otherwise — including an ad hoc spot-check outside
a full session — gets a published artifact carrying the questions, the answers, and any notation
too heavy for terminal text, kept live as it happens rather than assembled afterward.

## Do not infer along the graph

A pass on a concept does **not** license marking its ancestors `seen`. Inferring along the
graph was tried and failed: in one placement, eleven of thirteen passes had a directly observed
*miss* somewhere among their ancestors. People learn out of order, forget the
foundations and keep the results, and hold the conclusion while having lost the derivation.

The concept graph orders your questions. It never writes states.

## Writing back

In `courses/<slug>/units.json`, on the unit:

- `placed` — today's date.
- every entry of `concepts` — a `state`.
- `log` — one entry recording that this was a placement, with the questions asked. The provenance
  matters: a later reader must be able to tell an observed `seen` from an inferred one.

Leave `srs` alone unless the placement was substantial enough to count as a review — if it was,
`reps` becomes 1 and `last_seen` today, and the unit derives to `learning`.

Write `state` and nothing else on a concept. Its `claim`, `kind`, `prereqs` and `questions` are
structure and belong to `skills/knowledge-map/SKILL.md`.
