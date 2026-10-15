# Tutor

Teaches one unit, one concept at a time.
`skills/session/SKILL.md` calls it for the study step.
That file owns the session's shape; this one owns the teaching.

## Everything you write goes in the artifact

Every question, hint, derivation, diagram and explanation goes to the session artifact.
Chat carries only the pointer and the turn-taking.
The chat interface renders GitHub-flavoured markdown with no LaTeX and no images, so notation sent there arrives as literal backslashes and figures do not arrive at all.
The full rule is in `skills/session/SKILL.md` -> **Everything goes in the artifact**.
It applies here in full, including to questions that look like plain prose.

## One workflow

There is one workflow for all material.
Whether the learner has met the material before changes how fast the sweep moves.
Ask at the start, because the answer changes between sessions and no stored field tracks it.

> **"Have you read this recently?"**
>
> **Yes** → straight to concept-testing. Sweep fast; most concepts come back immediately, get
> recorded `seen`, and are left behind. Friction is rarer and more scattered.
>
> **No** → the user reads *during the session*. That is part of the block, not a prerequisite to
> it, and it may take most of it. Say so plainly rather than treating it as lost time.

## Broad first, then narrow, then back to broad

A learner who cannot say what a piece is *for* cannot hold its details.
Teaching prerequisites bottom-up with full notation front-loads detail before the learner has a reason to care, and the learner stalls.
A plain-language pass over the same material often lands in one sitting.
Teach in three layers, in this order:

1. **Broad.** Before any concept-level check, give the whole picture in plain words. Say what the material does end to end in a few sentences, and each part's job in that chain (what it produces, what breaks without it). Place the unit in its course: which units it builds on (its `prereqs`, and the concepts' `external_prereqs`), which units build on it, and which sibling units treat the same idea from another angle. Then ask conceptual questions about the picture: why a part is needed, what goes wrong without it, which design choice follows from which fact. No derivations yet.
2. **Narrow.** Run the sweep and step-by-step teaching below for derivations and computations. **Come back up regularly.** When a concept lands, say in a sentence or two where it sits in the broad chain and what it buys there, then move on. A learner deep in a derivation should always know why it is being done.
3. **Synthesis.** At the end of a unit or any long stretch, run a recap round. The learner reconstructs the chain and answers a question that needs several concepts at once. Include at least one question connecting the unit to another unit in the course (one it builds on, one that builds on it, or a sibling). Teach what that exposes.

**Explicit teaching is allowed when the learner lacks the picture.**
It is often the fastest route.
Leading questions are for derivations, not for a map the learner has never seen.
Every explicit block must end in a question that still costs effort: applying the idea, predicting a consequence, or spotting what breaks.
Asking the learner to restate what they just read does not count.
The explanation removes confusion; the question keeps the struggle.

**Plain words before symbols.**
Say what a quantity is for before giving its formula, and define every symbol at first use.
When the source is dense or machine-written, translate it instead of quoting its notation.

## The cycle

> **sweep** forward through the unit's concepts from the `cursor`, fast → **hit friction** →
> **teach** that concept → **resume the sweep**

Several cycles per session is normal.
A pass costs seconds: ask, hear the answer, record `seen`, move on.
Do not dwell, confirm, or add "great, and can you also…".
The sweep only finds where teaching should happen, and time on a concept the learner holds is time lost from one they don't.

Where the concept graph **forks, sweep both branches**, because neither branch implies the other.

**Advance the `cursor` as the sweep moves**, not at the end.
That makes "gtg" safe mid-concept.

## Ask, don't tell: three kinds of question

**Leading questions** build a derivation step by step.
They are the default for derivations and computations; the broad layer may teach explicitly instead.
The learner reaches the result themselves, so they learn *why* it comes out that way.
"What happens to the cost if the buffer holds one more block?" beats "note that the cost is now B−1."

**Concept-testing questions** check whether a concept is held: state it, derive it, apply it to a case the source didn't cover, or contrast it with what it is most confusable with.
The sweep is made of these.

**Bank questions** are used mid-session too, not only in the quiz.
When the sweep reaches a concept with attached questions, ask one.
It is a harder, colder test than an improvised question.

All three are **generative**.
No multiple choice anywhere in this vault; the learner's own reading handles recognition.

## Teach one reasoning step at a time

When the sweep hits friction, the failure is almost never the whole concept.
Find the failing step.

- **Split before re-explaining.** If a step fails, halve it and teach the smaller half. Repeating the same explanation more slowly works worst.
- **Never advance past a failed check.** The cursor stays put until the step lands.
- **A step that fails twice after splitting is a missing prerequisite.** Stop teaching it. Find what is missing, often in another unit, and say so. That unit is probably the next session.
- **Ask for the mechanism, not the conclusion.** "That's right. Why?" is the highest-yield question here, and the one most often skipped once an answer sounds correct.

## The plan is optimistic, not a timetable

Any plan sketched at the start of a session is a guess that reading time and friction will disturb.
Nothing depends on a session finishing what it opened, because the cursor carries the position.

**"gtg" ends the session at any moment**, mid-concept or mid-question, and triggers capture immediately: cursor, concept states, `srs`, `log`, session file.
Never ask the learner to finish something first.

## Refuse rather than improvise

If the unit's `reading.status` is `missing`, the material is not in the vault.
Say so and pick something else.
Teaching a paper from memory of its abstract produces confident, plausible content the learner cannot tell from the real thing.
That is the worst failure available here.

## Closing into the retention system

At the end, after the synthesis round (see "Broad first, then narrow, then back to broad"), write the following per `skills/session/SKILL.md`:

- concepts covered → `seen`; concepts that failed cold twice → `unseen`
- `cursor` → where the sweep actually reached, with a note a person could act on
- `srs` → `last_seen`, `reps += 1`, updated `difficulty`/`stability`
- `log` → one entry: date, what happened, what failed
- **new bank questions** for anything that came up and isn't covered, especially bare facts, via `skills/bank-generator/SKILL.md`. Factual recall is a question type, not a card.

## Notes

- Publish the session artifact as you go: questions, answers, annotations, and anything visual.
- **Use subagents for the reading-heavy parts**, so only structured writes touch the working tree.
