# Bank Generator

Use this skill when the learner asks to generate, regenerate or expand a question bank, for example "generate a question bank for [topic]", "add more questions on [subtopic]", or "bulk up the bank for [topic]".
Never run it automatically inside a curriculum session.
(`tutor` may add a few questions mid-session for something uncovered; that is not a generation run.)

## Inputs

- **All files under `courses/<slug>/sources/`**, treated as ground truth. If the topic has no sources yet, ask the learner to add material first. Use web search or known canonical sources only if the learner explicitly says to.
- **The existing `courses/<slug>/bank.jsonl`**, if present. Read it fully first, and check new questions against existing ones for semantic overlap, not just exact string match.
- **The `sources` and `notes` fields in the `units.json` header**, which set scope and density (below).

## Scope: what "the topic" actually covers

The subtopics in `notes` are a **floor, not a ceiling**: the learner cannot list gaps they don't know they have.
Generate over (everything listed in `notes`) UNION (everything the source material covers):

- Cover every chapter or section you have material for.
- Use `notes` to set emphasis and depth, not inclusion. Subtopics it flags get denser and harder coverage; unmentioned ones still get coverage, possibly at lower density.
- Material the learner calls largely mastered still gets a **light pass**: the hardest, most insightful or trickiest problems and sections (starred sections, "extra" callouts, competition-style problems, hidden gems away from the main content), not routine recall.
- When unsure whether something is in scope, include it. A bank missing a whole chapter is worse than one with uneven emphasis.

## Process

1. Read every source file for the topic and map its subtopics and sections. For large sources (a full book, hundreds of pages), use the large-source protocol below instead.
2. Decide a target quantity. Aim for at least 15-25 questions per distinct subtopic, more for subtopics the learner flags as high priority. A textbook chapter may yield 25 to 100 questions or more. When in doubt, generate more. Ask if the quantity is unspecified and the scope is ambiguous.
3. Generate questions per the quality bar below, each with a real `answer_key` and `grading_notes` for anything with multiple valid framings.
4. **Self-containedness pass (mandatory).** Re-read each question in isolation, with no source, lecture or other question available, and inline any context it leans on (see the quality bar).
5. Set `source_ref` as "<topic>#<book/source> <chapter/section title>", e.g. `courses/system-design/sources/data-intensive-applications.pdf#Ch5 Replication > Leaders and Followers`. The learner sees it and the grader checks against it, so use the real chapter or section title, not just a page number.
6. Append new entries to `courses/<slug>/bank.jsonl`. Assign ids as `<topic>-<zero-padded sequential number>`, continuing from the highest existing id. `check_vault.py` requires `id`, `topic`, `subtopic`, `type`, `question`, `answer_key`, `source_ref`, `difficulty` and `date_generated`, plus `course` wherever the id prefix differs from the directory name.
7. Attach each new id (below).
8. Report how many questions were added, a breakdown by subtopic and type, and any thin subtopics that need more source material.

## Large-source protocol (books, long PDFs, multi-hundred-page material)

Don't hold a whole book in your own context.
Fan out to cheap (haiku-tier) subagents in a map-reduce pattern, and track state in a manifest so the job can resume after an interruption.

1. **Partition.** Split the source into chapter- or section-sized chunks, following its table of contents rather than page counts where a structure exists. Write a manifest such as `courses/<slug>/.progress/<topic>_manifest.json`, listing each chunk's id, page or section range, and status (`pending`/`in_progress`/`done`).
2. **Map.** Spawn one cheap subagent per chunk, in parallel batches with reasonable concurrency. Each subagent:
   - Reads only its chunk.
   - Writes a structured summary of everything covered: every concept, theorem, definition, worked example, exercise type, aside and notable edge case, not just headline concepts.
   - Drafts candidate questions per the quality bar, each with a precise `source_ref` (chapter, section, page). State the self-containedness and markdown-formatting rules directly in each subagent's prompt, because cheap subagents drop them otherwise.
   - Writes its output to a temp file (e.g. `courses/<slug>/.progress/<topic>_chunk<id>.json`) and marks its manifest entry `done`. On resume, dispatch only chunks still `pending`.
3. **Reduce.** Read all chunk outputs yourself. Dedupe near-identical questions across chunk boundaries, check coverage balance, and spot-check a sample of answer keys, since cheap subagents can hallucinate them.
4. **Commit and clean up.** Append the vetted questions to the bank. Delete this run's `.progress/` temp files once the bank write succeeds.

For sources that fit comfortably in your context, skip the orchestration.

## Quality bar for questions

- **Generative, always** (see `CLAUDE.md`). No multiple choice and no cloze deletions. A question whose answer can be pointed at rather than stated does not belong in the bank.
- **Grounded.** Every question must be answerable from the sources, or from canonical knowledge of the field where the sources are thin. No fabricated facts.
- **Cover every facet.** Mine worked examples and their variations, footnotes and asides, historical and motivational context, edge cases and exceptions, the source's own exercises, its connections to other topics, and the misconceptions it flags. If your questions could have been written from a one-page summary, go back to the parts a summary leaves out.
- **Diverse in type.** This is a primary quality axis. A chapter-sized batch should draw from most of this list, not lean on 3-4 comfortable types:
  - Compare & contrast ("how does X differ from Y", "when would you use X vs Y")
  - Explain-in-own-words / mechanism ("why does X happen")
  - Application / scenario ("given this situation, what would you do / predict")
  - Error-spotting / critique ("here's a flawed argument or solution: what's wrong")
  - Short math or coding problems, solvable in a few lines or steps
  - Short-paragraph synthesis questions
  - Definition / statement recall (see "Factual recall" below)
  - Multi-part or "explain then apply" combos
  - Proof/derivation: "prove that...", "derive...", "show that...". The point is the logical chain, not a numeric answer.
  - Estimation / order-of-magnitude / sanity-check: "roughly how does X scale with n", "is this closer to 10 or 10,000, and how do you know without computing exactly".
  - Counterexample construction: "give an example where X holds but Y fails".
  - "Design/construct an X satisfying constraints Y and Z" (an automaton, a data structure, an algorithm). The answer key gives one valid construction plus the checkable criteria.
  - Analogy/transfer: "how does concept X here relate to concept Y from [another subtopic]".
  - "Explain to a beginner": plain-language fluency, separate from fluency with formal notation.

  Skew by topic: math-heavy topics toward problems, proofs and estimation; conceptual topics toward explain, compare, critique and analogy. If a batch used only 3-4 types, add questions in the skipped types before finalizing.
- **Nontrivial and difficult is the norm.** Roughly half or more of the questions should require real thinking: combining two ideas, spotting a non-obvious consequence, working a multi-step derivation, constructing something new, or applying a concept where the source didn't spell it out.
- **Time-boxed difficulty.** Someone who studied the material recently should solve a typical question within a few minutes, and the hardest within about 10 minutes. If a question needs a fresh page of derivation or more than about 10 minutes even for someone fluent, split it or cut it.
- **Gist-recall questions for math-flavored topics.** Ask "what family of technique applies to a problem shaped like X", "what's your first move and why". These train fast recognition ("this is a Lagrange multiplier situation"), which is usually the bottleneck when math skills go rusty.
- **Non-redundant.** Vary the angle, the cue and the depth instead of rewording the same fact.
- **Fully self-contained.** A question must be answerable without seeing any other question, the source text or lecture context:
  - Never reference a named theorem, algorithm, definition or equation without restating its content inline. Bad: "Why does step 3 of the algorithm fail on disconnected graphs?" Good: "Dijkstra's algorithm relies on greedily finalizing the closest unvisited vertex. Why does this greedy strategy fail to find shortest paths when edge weights can be negative?"
  - Exercise numbers, figure numbers and "problem 12" never appear in the question text. They are fine in `source_ref`.
- **Markdown-clean formatting.** Questions and answer keys are rendered as markdown:
  - Use LaTeX-style math (`$...$` inline, `$$...$$` display) or, if the renderer doesn't support LaTeX, plain but unambiguous notation (`x^2`, `sqrt(x)`, `sum_{i=1}^n`). Pick one convention per bank.
  - Use code fences for code and pseudocode. Describe diagrams, state machines and graphs in a renderable structure (a transition table, an adjacency list, an indented tree or ASCII sketch), not prose that assumes an image.
  - Use markdown lists or tables for multi-part questions and structured answer keys.

### Factual recall

Factual recall is a question type (see `CLAUDE.md` → "bank.jsonl").
Three shapes:

- **"Define X."** / **"State the X theorem precisely."**: the bare production, no scaffolding.
- **"What does Y mean inside the definition of Z?"**: catches definitions that are memorized but inert.
- **"Contrast the definition of A with that of B."**: for pairs whose definitions are one clause apart (independent vs. uncorrelated, serializable vs. strict).

Keep them a minority, mainly for fact-shaped content (definitions, theorem statements, notation, constants, names, dates).
Do not skip them either: if a chapter introduces vocabulary that later chapters use without re-explaining, that vocabulary needs recall questions.

## Attaching questions to concepts

After appending to `bank.jsonl`, write each new id into the `questions` list of the concept it tests in `units.json`, following `skills/knowledge-map/SKILL.md` → "Attaching questions".
If no concept covers it, because the concept layer is thin or the question spans the whole unit, put the id in the unit's own `questions` list.
Attach after appending, never before: `check_vault.py` errors on an id with no bank entry.

## Notes

- If sources are sparse, say so rather than padding with generic questions. Flag thin coverage on a subtopic; don't hide it.
- When expanding an existing bank, focus on under-represented subtopics and types rather than adding evenly everywhere.
