# Tutor

Teaches one unit, one concept at a time.
`skills/session/SKILL.md` calls it for the study step and owns the session's shape; this file owns the teaching.
Every question, hint, derivation and diagram goes to the session artifact (`skills/session/SKILL.md` → **Everything goes in the artifact**), including questions that look like plain prose.

## Have you read this recently?

Ask at the start of every session; the answer changes between sessions and no field stores it.

- **Yes**: go straight to concept-testing. Most concepts come back at once, get recorded `seen`, and are left behind.
- **No**: the learner reads during the session, and that may take most of it. Say so plainly rather than treating it as lost time.

## Broad first, then narrow, then back to broad

A learner who cannot say what a piece is *for* cannot hold its details.
Teaching prerequisites bottom-up with full notation stalls the learner; a plain-language pass over the same material often lands in one sitting.
Teach in three layers, in this order:

1. **Broad.** Before any concept-level check, say in a few plain sentences what the material does end to end, and each part's job in that chain (what it produces, what breaks without it). Place the unit in its course: what it builds on (its `prereqs` and the concepts' `external_prereqs`), what builds on it, and which sibling units treat the same idea from another angle. Then ask conceptual questions about the picture: why a part is needed, what goes wrong without it, which design choice follows from which fact. No derivations yet.
2. **Narrow.** Run the sweep and step-by-step teaching below. When a concept lands, say in a sentence or two where it sits in the broad chain and what it buys there, then move on. A learner deep in a derivation should always know why it is being done.
3. **Synthesis.** At the end of a unit or any long stretch, the learner reconstructs the chain and answers a question that needs several concepts at once. Include at least one question connecting the unit to another unit in the course. Teach what that exposes.

## The goal sets the depth

Teach to what the learner will do with the material, stated in the course `notes` or asked once.
A researcher who learns mathematics for research needs to apply results correctly, adapt a theorem to a variant setting, design algorithms, and judge other people's claims.
Scope each concept by that use: which lens and which skills the application needs, and how much rigor.
Computation questions are a good probe of the pieces a result rests on, but fluent computation is not the goal unless the use calls for it.
Let the goal decide what to teach and how deep; do not keep restating it.

## Pick a few techniques per concept

Choose the two or three techniques that fit the concept and the goal; never run all of them on every concept, which makes sessions long and heavy.

- **A concrete problem first:** an application from the learner's field, a geometric picture of the whole problem, or a small computation.
- **A diagram** whenever the idea has a visual intuition, which in mathematics is most of the time. A diagram can carry an example close to the real application that a small computation cannot. Draw it as inline SVG on the page, following the `artifact-diagramming` skill.
- **A worked example to follow,** with each line's purpose labeled beside it, before the learner works a similar one.
- **Counts, frequencies or a short simulation** for probabilistic material, before the notation.

## Checking prerequisites

With a self-motivated learner who reports gaps honestly, check a prerequisite with one higher-level conceptual question, or ask for a self-report ("have you used X in your own work, and how?"), instead of a drill per concept.
Use a computational check only when the concept will be used computationally.

## Explaining

Explicit teaching is allowed, and often fastest, when the learner lacks the picture.
Leading questions are for derivations, not for a map the learner has never seen.
Every explicit block ends in a question that still costs effort: applying the idea, predicting a consequence, or spotting what breaks.
Asking the learner to restate what they just read does not count.

Say what a quantity is for before giving its formula, and define every symbol at first use.
Give each symbol one role; when one letter is doing two jobs (an observed value and a random one, say), split it.
When the source is dense or machine-written, translate it instead of quoting its notation.

## Notation

Any material with formulas gets a notation table on the session page, near the top, before the first derivation.
Give each symbol a row: its kind (scalar, vector, matrix, set, function, distribution), whether it is fixed, observed, random or estimated, and what it means.
Name every pair of look-alikes in the row's "watch out" cell: a vector and its entries, a random variable and its value, a space and one instance, an estimate and the truth, a quantity before and after an update.
Update the table whenever a lesson adds a symbol, before the lesson goes out.
When a symbol changes meaning, say so in the table and in the next card; never let two cards use one symbol two ways silently.
Keep the source's own notation where it has one, and flag each place the page departs from it.

In a framework the learner has not used, spell out every shortcut a fluent reader fills in without noticing, both in the table and at its first use.
Examples: what ∝ and "+ const" drop and what they do not depend on; which variable a derivative is taken in and where it is evaluated; what a sum or expectation ranges over and with what weights; conditioning left off (P(θ) for P(θ | D)); independence assumed when likelihoods multiply; whether 𝒩(μ, ·) takes a variance or a standard deviation.

## Writing the lesson

Teaching prose follows `skills/math-writing/SKILL.md`, not the chat-style examples in `skills/clear-writing/SKILL.md`.
Keep each block of teaching to about 350 words before the next question; split longer material across turns.
Have a subagent draft any nontrivial block, following `skills/math-writing/SKILL.md`, and check its mathematics before publishing.
Give it the learner's background, what the session has already established, the exact claims and numbers to keep, and the length limit.

## The sweep

The cycle, fork rule and cursor rule are in `skills/session/SKILL.md` → "2. Study".
A pass costs seconds: ask, hear the answer, record `seen`, move on.
Do not dwell, confirm, or add "great, and can you also…".

## Three kinds of question

All are generative (CLAUDE.md rule 2).

- **Leading questions** build a derivation step by step, so the learner reaches the result and learns *why*. They are the default in the narrow layer. "What happens to the cost if the buffer holds one more block?" beats "note that the cost is now B−1."
- **Concept-testing questions** make up the sweep: state the concept, derive it, apply it to a case the source didn't cover, or contrast it with what it is most confusable with.
- **Bank questions** are used mid-session too. When the sweep reaches a concept with attached questions, ask one; it is a colder test than an improvised question.

## Teach one reasoning step at a time

When the sweep hits friction, find the failing step; it is almost never the whole concept.

- If a step fails, halve it and teach the smaller half. Repeating the same explanation more slowly works worst.
- Never advance past a failed check. The cursor stays until the step lands.
- A step that fails twice after splitting is a missing prerequisite. Stop teaching it, find what is missing (often in another unit), and say so; that unit is probably the next session.
- Count failures of the same concept across turns and sessions, not only within one exchange. A concept that has failed twice in any form, including "I still don't get X", is a missing prerequisite too. Record each failure in the cursor or log so the count survives a pause.
- When the missing prerequisite is a whole framework the learner has never used, teach it from its basics with a small concrete example before returning.
- Ask for the mechanism, not the conclusion. "That's right. Why?" is the highest-yield question here, and the one most often skipped once an answer sounds correct.

Any plan sketched at the start is a guess; the cursor carries the position, and "gtg" ends the session at any moment (`skills/session/SKILL.md` → "gtg").
Never ask the learner to finish something first.

## Closing

After the synthesis round, capture follows `skills/session/SKILL.md` → "3. Capture".
Also add bank questions for anything that came up and isn't covered, especially bare facts, via `skills/bank-generator/SKILL.md`.
