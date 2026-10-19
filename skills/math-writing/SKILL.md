# Math writing

How to write teaching prose: lessons, explanations, worked examples and grading notes on the session page.
The model is Jay Cummings's *Proofs: A Long-Form Mathematics Textbook* (2021); the page numbers below cite it. If you own a copy, put the PDF at `skills/math-writing/reference/cummings-proofs.pdf` so the agent can open the cited pages; it is not distributed with this repo.
Copy its method, not its humor: the reader meets one new thing at a time, with plenty of examples, and nothing is left for the reader to reconstruct.
When unsure how to pace a passage, open the pages cited below and imitate them.

For teaching prose this skill replaces the chat-style examples in `skills/clear-writing/SKILL.md`.
Clear-writing's bans still hold: no padding, no em dashes, no decorative metaphors, no announced significance.
A physical model that the lesson reuses throughout (dominoes for induction, boxes for sets) is not a decorative metaphor; it is a teaching tool.

## One new thing at a time

- Introduce at most one new term or symbol per paragraph, and give it a picture or examples before the next one (pp. 73–75, 82–86).
- Introduce symbols in batches of at most three, give each an English reading, and follow at once with a worked instance (pp. 157–158).
- Spread one formal idea over several short paragraphs; never pack it into one sentence. Cummings gives the implication truth table three pages (pp. 164–167).
- When an earlier symbol or definition returns, restate its meaning inline ("Recall that ...") instead of citing it (pp. 13, 125).
- Give just enough of a side idea when it is needed, and say that the rest comes later (p. 58, footnote).

## The shape of a lesson

A lesson on one concept moves through these beats, spread over as many 350-word blocks as it needs.
Skip a beat when the learner already holds it.

1. **Concrete cases with outcomes:** an application from the learner's field, a picture of the whole problem, or small numbers (pp. 1–2, 42).
2. **The name,** in words first, then the symbol (pp. 167–168).
3. **The definition, then three to six instances,** each checked against the definition in words, ending with an edge case. Add one non-example drawn the same way, naming the clause it violates (pp. 43, 249).
4. **The claim in "if P then Q" form,** with P and Q said in words (pp. 37, 44).
5. **The idea:** one paragraph stating the key insight, with scratch work showing how the argument was found (pp. 5, 44, 183).
6. **The derivation,** each step with a one-clause reason, split into labeled parts when long; each part ends by saying what it established (pp. 53–54, 202).
7. **A recap** in two or three plain sentences (p. 7).
8. **One extension:** a second view, why each assumption is needed, or a variant that breaks the result (pp. 88, 130).

## Sentences that keep the context

- Every sentence makes one claim a reader could check, with a concrete subject and verb. If you cannot say which thing does what to which, the sentence is not ready.
- Never string concepts together into a sentence that sounds technical but asserts nothing ("the estimator leverages the curvature structure of the posterior geometry"). Name the quantity, the operation and the result instead.
- Each sentence builds on the one before it. Do not drop context between sentences or between blocks; recall it.
- Before a displayed formula, name the operation in a clause ("Adding the two equations,"); after it, say what it shows ("So the variance is 1/6") (p. 54).
- Cite the justification for each step by name, even if it was cited three lines earlier (pp. 53–54).
- Announce the plan before a multi-step derivation (p. 112).
- Ask the reader's question aloud, then answer it in the next sentence ("What does it mean for a to divide b? The definition tells us.") (p. 53).
- Mark restatements with "That is," or "Said differently,".
- The prose should still read sensibly with every formula replaced by "blah" (Knuth).

## Look-alikes, mistakes and surprises

- Separate look-alikes with a minimal pair that differs in one feature, and ask for a prediction before resolving it (pp. 160, 169, 256).
- Name the common mistake as "a common mistake is ...", and show one concrete case where it fails (pp. 171, 199, 257).
- When a convention is a definition rather than a theorem, say so plainly, then still give an intuition for it (pp. 165–166).
- For a counterintuitive result, escalate through cases, state the likely wrong prediction, reveal the result, restate it, and say the surprise is warranted (pp. 283–289).
- Map a new framework onto one the reader already knows, symbol by symbol, with a picture (p. 161). Use the learner's home field as the known framework when it fits.
- When one structural idea recurs across definitions, name it once and point back to it each time (pp. 248, 252, 254).

## Pictures

- Draw a diagram whenever the idea has a visual intuition.
- Introduce each diagram in the sentence just before it ("Here is the posterior after one score:"), and label its parts with the steps of the argument (pp. 265, 288).
- In a sequence of diagrams, change one thing per frame (pp. 88–89, 119–123).
- Keep the argument complete without the picture; the picture shows, the words prove (p. 7).

## Main line and side layers

The main line holds the cases, the definition, the claim, the idea, the derivation and the recap.
Reminders, extra algebra, history and optional rigor go in a collapsible `<details>` box beside the step they serve.

## Checking a draft

Before publishing a block, answer three questions for each paragraph:

1. What is the one new thing in it?
2. Which earlier sentence does each sentence build on?
3. Does every symbol have a meaning stated on this page?

Rewrite any paragraph that fails one of them.
