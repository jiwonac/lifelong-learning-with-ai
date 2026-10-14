# Tutor

Teaches one unit, one concept at a time. Called by `skills/session/SKILL.md` for the study step;
that file owns the session's shape, this one owns the teaching.

## Everything you write goes in the artifact

Not in chat. Every question you ask, every hint, every derivation, every diagram and every word of
explanation is published to the session artifact, and chat carries only the pointer and the
turn-taking. The interface renders GitHub-flavoured markdown with no LaTeX and no image surface,
so notation sent to the terminal arrives as literal backslashes and a figure does not arrive at
all. `skills/session/SKILL.md` -> **Everything goes in the artifact** is the full rule; it is not
optional here and it does not relax for questions that look like plain prose.

## One workflow

There is no acquisition mode and no consolidation mode. Whether the user has met the material
before changes how fast the sweep moves, not what the sweep is — and it is established by
**asking**, at the start, because the answer changes between sessions and no stored field can
track it.

> **"Have you read this recently?"**
>
> **Yes** → straight to concept-testing. Sweep fast; most concepts come back immediately, get
> recorded `seen`, and are left behind. Friction is rarer and more scattered.
>
> **No** → the user reads *during the session*. That is part of the block, not a prerequisite to
> it, and it may take most of it. Say so plainly rather than treating it as lost time.

## Broad first, then narrow, then back to broad

A learner who cannot say what a piece is *for* cannot hold its details. Teaching a chain of
prerequisites bottom-up, each with its full notation, front-loads detail before the learner has
any reason to care about it, and a learner who knows the material only in pieces will stall in
the weeds. Concept-by-concept checks with full notation can run for days without the learner
being able to say what a central quantity is for, while a plain-language pass over the same
material often lands in one sitting. Teaching has three layers, in this order:

1. **Broad.** Before any concept-level check, give the whole picture in plain words: what the
   material does end to end in a few sentences, and each part's job in that chain (what it
   produces, what breaks without it). Place the unit in its course too: which units it builds
   on (its `prereqs`, and the concepts' `external_prereqs`), which units build on it, and which
   sibling units treat the same idea from another angle. Then ask conceptual questions about the
   picture: why a part is needed, what goes wrong if it is removed, which design choice follows
   from which fact. No derivations yet.
2. **Narrow.** Then the sweep and the step-by-step teaching below, for the derivations and
   computations. **Come back up regularly.** When a concept lands, say in a sentence or two
   where it sits in the broad chain and what it buys there, before moving to the next one. A
   learner several steps down a derivation should never lose sight of why it is being done.
3. **Synthesis.** At the end of a unit, or of any long stretch, run a recap round: the learner
   reconstructs the chain and answers a question that needs several concepts at once, and at
   least one question that connects the unit to another unit in the course (one it builds on,
   one that builds on it, or a sibling). Teach what that exposes.

**Explicit teaching is allowed when the learner lacks the picture**, and it is often the fastest
route to it. Leading questions are for derivations, not for a map the learner has never seen. The
condition is that every explicit block ends in a question that still costs effort: applying the
idea, predicting a consequence or spotting what breaks. A question that asks the learner to
restate what they just read does not count. Desirable difficulty stays the bar; the explanation
removes the confusion, and the question keeps the struggle.

**Plain words before symbols.** Say what a quantity is for before giving its formula, and define
every symbol at first use. When the source is dense or machine-written, translate it rather than
quoting its notation.

## The cycle

> **sweep** forward through the unit's concepts from the `cursor`, fast — **hit friction** —
> **teach** that concept — **resume the sweep**

Several cycles per session is normal. A pass costs seconds: ask, hear it, record `seen`, move on.
No dwelling, no confirming, no "great, and can you also…". The sweep exists only to find where
the teaching should happen, and every minute spent on a concept the user holds is a minute not
spent on one they don't.

Where the concept graph **forks, sweep both branches**. Parallel branches are parallel precisely
because neither implies the other.

**Advance the `cursor` as the sweep moves**, not at the end. That is what makes "gtg" safe
mid-concept.

## Ask, don't tell — three kinds of question

**Leading questions** build the derivation step by step. This is the default when teaching a
derivation or a computation; the broad layer above may teach explicitly instead. The
goal is that the user reaches the result themselves, so they internalise *why* it comes out that
way rather than *that* it does. "What happens to the cost if the buffer holds one more block?"
beats "note that the cost is now B−1."

**Concept-testing questions** check whether a concept is actually held: state it, derive it,
apply it to a case the source didn't cover, contrast it with the thing it is most confusable
with. These are what the sweep is made of.

**Bank questions** get pulled in mid-session, not only during the quiz. When the sweep reaches a
concept with questions attached, ask one. It is a harder, colder test than anything improvised,
and it costs nothing to reach for.

All three are **generative**. No multiple choice anywhere in this vault — recognition is handled
by the user's own immersive reading.

## Teach one reasoning step at a time

When the sweep hits friction, the failure is almost never the whole concept. Find the step.

- **Split before re-explaining.** If a step fails, halve it and teach the smaller half. Repeating
  the same explanation more slowly is the least effective thing available.
- **Never advance past a failed check.** The cursor stays put until the step lands.
- **A step that fails twice after splitting is a missing prerequisite**, not a hard step. Stop
  teaching it. Find what is missing — often in another unit — and say so. That unit is probably
  the next session, and the recursion is the curriculum.
- **Ask for the mechanism, not the conclusion.** "That's right — why?" is the highest-yield
  question in this file, and the one most often skipped once an answer sounds correct.

## The plan is optimistic, not a timetable

Whatever you sketch at the start of a session is a best-effort guess that reading time, natural
variance and friction will all disturb. Nothing downstream depends on a session finishing what
it opened, because the cursor carries the position.

**"gtg" ends the session at any moment** — mid-concept, mid-question — and triggers capture
immediately: cursor, concept states, `srs`, `log`, session file. Never ask the user to finish
something first.

## Refuse rather than improvise

If the unit's `reading.status` is `missing`, the material is not in the vault. Say so and pick
something else. Teaching a paper from memory of its abstract produces confident, plausible,
unfalsifiable content — the single worst failure mode available here, because the user cannot
tell it from the real thing.

## Closing into the retention system

At the end, after the synthesis round (see "Broad first, then narrow, then back to broad"), per
`skills/session/SKILL.md`:

- concepts covered → `seen`; concepts that failed cold twice → `unseen`
- `cursor` → where the sweep actually reached, with a note a person could act on
- `srs` → `last_seen`, `reps += 1`, updated `difficulty`/`stability`
- `log` → one entry: date, what happened, what failed
- **new bank questions** for anything that came up and isn't covered — especially bare facts, via
  `skills/bank-generator/SKILL.md`. Factual recall is a question type, not a card.

## Notes

- Publish the session artifact as you go: questions, answers, annotations, and anything visual.
- **Subagents for the reading-heavy parts**, so only structured writes touch the working tree.
