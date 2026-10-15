# Bank Generator

Use this skill when the learner asks to generate, regenerate or expand a question bank, for example "generate a question bank for [topic]", "add more questions on [subtopic]", or "bulk up the bank for [topic]".
It is a deliberate, manually invoked action; never run it automatically inside a curriculum session.
(`tutor` may add a few questions mid-session for something uncovered; that is not a generation run.)

## Inputs

- **All files under `courses/<slug>/sources/`**, treated as ground truth. If the topic has no sources yet, ask the learner to add material (textbook excerpts, course notes, wiki pages, lecture transcripts, problem sets) first. Use web search or known canonical sources for well-established topics only if the learner explicitly says to.
- **The existing `courses/<slug>/bank.jsonl`**, if present. Read it fully first, and check new questions against existing ones for semantic overlap, not just exact string match.
- **The `sources` and `notes` fields in the `courses/<slug>/units.json` header.** They are the course's only prose and set scope and density (below). Its `units` array is where finished questions get attached (see "Attaching questions to concepts").

## Scope: what "the topic" actually covers

`sources` is the bibliography and says what each source is for.
`notes` gives scope, difficulty calibration, and caveats about the material.
Read both before generating.

The subtopics in `notes` are a **floor, not a ceiling**.
They list weak spots the learner already knows about, and the learner cannot list gaps they don't know they have.

The generation scope is **(everything listed in `notes`) UNION (everything the source material covers)**:

- Cover the entire source (every chapter or section you have material for), not just the parts that match `notes`.
- Use `notes` to set emphasis and depth, not inclusion. Subtopics it flags, or that its difficulty-calibration section points at, get denser and harder coverage. Unmentioned subtopics still get coverage, possibly at lower density.
- A difficulty-calibration note such as "the basics are engrained, skip them" constrains how to cover basic material, not whether to. Material the learner calls largely mastered still gets a **light pass**: the hardest, most insightful or trickiest problems and sections (starred sections, "extra" callouts, competition-style problems, hidden gems away from the main content), not routine recall.
- When unsure whether something is in scope, include it. A bank missing a whole chapter is worse than one with uneven emphasis.

## Process

1. Read every source file for the topic and map its subtopics and sections. For large sources (a full book, hundreds of pages), use the large-source protocol below instead.
2. Decide a target quantity. Aim for at least 15-25 questions per distinct subtopic, more for subtopics the learner flags as high priority. A textbook chapter may yield 25 to 100 questions or more, depending on scope and relevance. When in doubt, generate more; a thin bank is worse than an oversized one. Ask if the quantity is unspecified and the scope is ambiguous.
3. Generate questions per the quality bar below.
4. Write a real `answer_key` for each question, enough to grade later without re-deriving it, plus `grading_notes` for anything with multiple valid framings.
5. **Self-containedness pass.** Re-read each question in isolation, with no source, lecture or other question available. If it leans on anything not restated inline (a named theorem, algorithm or equation, an exercise or figure number, a setup from "the text"), add that context to the question text. This step is mandatory; see the self-containedness rule in the quality bar.
6. Set `source_ref`. It is shown to the learner when the question is asked and used by the grader to check answers, so it should read cleanly as "<topic>#<book/source> <chapter/section title>", e.g. `courses/system-design/sources/data-intensive-applications.pdf#Ch5 Replication > Leaders and Followers`. Use the real chapter or section title, not just a page number.
7. Append (don't overwrite) new entries to `courses/<slug>/bank.jsonl`, following `CLAUDE.md`. Assign ids as `<topic>-<zero-padded sequential number>`, continuing from the highest existing id. Never rewrite an existing entry except to fix a factual error, because units and past sessions reference questions by id. `check_vault.py` requires every entry to carry `id`, `topic`, `subtopic`, `type`, `question`, `answer_key`, `source_ref`, `difficulty` and `date_generated`, plus a `course` field wherever the id prefix differs from the directory name (for example, when a bank's ids predate the course's slug).
8. Report a short summary: how many questions were added, a breakdown by subtopic and type, and any thin subtopics that need more source material.

## Large-source protocol (books, long PDFs, multi-hundred-page material)

Don't hold a whole book in your own context.
Fan out to cheap (haiku-tier) subagents in a map-reduce pattern, since this is extraction and generation work.
Track state in a temp manifest so the job can resume after an interruption.

1. **Partition.** Split the source into chapter- or section-sized chunks, following its table of contents rather than page counts where a structure exists. Write a manifest such as `courses/<slug>/.progress/<topic>_manifest.json`, listing each chunk's id, page or section range, and status (`pending`/`in_progress`/`done`).
2. **Map.** Spawn one cheap subagent per chunk, in parallel batches with reasonable concurrency. Each subagent:
   - Reads only its chunk.
   - Writes a structured summary of everything covered: every concept, theorem, definition, worked example, exercise type, aside and notable edge case, not just headline concepts. This wide summary feeds question diversity.
   - Drafts candidate questions per the quality bar, each with a precise `source_ref` (chapter, section, page). State the self-containedness rule (restate referenced theorems and equations; no bare exercise numbers in question text) and the markdown-formatting rule directly in each subagent's prompt, because cheap subagents drop them otherwise.
   - Writes its output to a temp file (e.g. `courses/<slug>/.progress/<topic>_chunk<id>.json`) and marks its manifest entry `done`. On resume, re-scan the manifest and dispatch only chunks still `pending`.
3. **Reduce.** Read all chunk outputs yourself; they are short, so this is cheap. Dedupe near-identical questions across chunk boundaries, check coverage balance, and spot-check a sample of answer keys before writing anything to the bank. Cheap subagents can hallucinate answer keys.
4. **Commit and clean up.** Append the vetted questions to `courses/<slug>/bank.jsonl`. Delete this run's `.progress/` temp files once the bank write succeeds.

For small and medium sources that fit comfortably in your context, skip the orchestration and read and generate yourself.

## Factual recall is a question type here

The unit's SRS schedules the whole unit, so anything that must be memorized verbatim (a definition, a theorem statement, notation, a constant, a name) becomes an ordinary bank question that asks for it:

- **"Define X."** / **"State the X theorem precisely."**: the bare production, no scaffolding.
- **"What does Y mean inside the definition of Z?"**: catches definitions that are memorized but inert, where every symbol is recalled and none means anything.
- **"Contrast the definition of A with that of B."**: for pairs that are confusable because their definitions are one clause apart (independent vs. uncorrelated, serializable vs. strict, isomorphism vs. homomorphism).

Write them generatively, like everything else: "define X", never "which of these defines X", and never a cloze deletion of a source sentence, which tests the sentence rather than the idea.

Calibrate in both directions:

- **Keep them a minority.** They connect genuinely fact-shaped content. A bank that collapses into definition prompts is the failure this system exists to avoid.
- **Do not skip them.** A learner who can derive a result but cannot state the theorem it rests on is a real and common case. If a chapter introduces vocabulary that later chapters use without re-explaining, that vocabulary needs recall questions.

Attach these to a concept like any other question.
The same eligibility rule applies, so a definition question is asked only once its concept has been studied.

## Quality bar for questions

- **Generative, always.** No multiple choice and no cloze deletions anywhere in this vault. The learner's own reading handles recognition; every question must require a production. A question whose answer can be pointed at rather than stated does not belong in the bank.
- **Grounded.** Every question must be answerable from the sources, or from canonical knowledge of the field where the sources are thin. No fabricated facts.
- **Cover every facet, not just the core concepts.** Mine worked examples and their variations, footnotes and asides, historical and motivational context, edge cases and exceptions, the source's own exercises, its connections to other topics, and the misconceptions it flags. If your questions could have been written from a one-page summary, go back to the parts a summary leaves out.
- **Diverse in type.** This is a primary quality axis. A chapter-sized batch should draw from most of this list, not lean on 3-4 comfortable types:
  - Definitions / "what is X and why does it matter"
  - Compare & contrast ("how does X differ from Y", "when would you use X vs Y")
  - Explain-in-own-words / mechanism ("why does X happen", "explain the reasoning behind X")
  - Application / scenario ("given this situation, what would you do / predict")
  - Error-spotting / critique ("here's a flawed argument or solution: what's wrong")
  - Short math or coding problems (if the topic involves them), solvable in a few lines or steps, not full projects
  - Short-answer / short-paragraph synthesis questions
  - Definition / statement recall: "define X", "state the X theorem precisely", "what does Y mean inside the definition of Z" (see the factual-recall section above; a minority of the bank)
  - Multi-part or "explain then apply" combos
  - **Proof/derivation questions**: "prove that...", "derive...", "show that...". The point is the logical chain, not a numeric answer.
  - **Estimation / order-of-magnitude / sanity-check questions**: "roughly how does X scale with n", "is this quantity closer to 10 or 10,000, and how do you know without computing exactly". These train the reflex that catches your own errors.
  - **Counterexample construction**: "give an example where X holds but Y fails" / "construct a case that breaks this proposed rule". Here the learner introduces the flaw instead of diagnosing someone else's.
  - **"Design/construct an X satisfying constraints Y and Z"**: open-ended but checkable construction (build an automaton, propose a data structure, sketch an algorithm). The answer key gives one valid construction plus the checkable criteria, since several answers may be correct.
  - **Analogy/transfer questions**: "how does concept X here relate to concept Y from [another topic/subtopic]". These link subtopics to each other.
  - **"Explain to a beginner" / rubber-duck questions**: tests plain-language fluency separately from fluency with formal notation.

  The list is illustrative, not mandatory in exact proportion. Use judgment per topic: a math-heavy topic skews toward problems, proofs and estimation; a conceptual humanities topic skews toward explain, compare, critique and analogy. Default to breadth: if a batch used only 3-4 types, add questions in the skipped types before finalizing.
- **Nontrivial and difficult is the norm.** Roughly half or more of the questions (more where the topic supports it) should require real thinking: combining two ideas, spotting a non-obvious consequence, working a multi-step derivation, constructing something new, or applying a concept where the source didn't spell it out. Shallow recall and definition questions are a minority, mainly for fact-shaped content (dates, names, exact statements of notation).
- **Time-boxed difficulty.** Someone who studied the material recently should solve a typical question within a few minutes, and the hardest within about 10 minutes. Nontrivial means it takes real thought, not real time. If a question needs a fresh page of derivation or more than about 10 minutes even for someone fluent, split it into a shorter, sharper question or cut it.
- **Gist-recall questions for math-flavored topics.** Ask "what family of technique applies to a problem shaped like X", "what's the key trick for solving Y", "given this problem's shape, what's your first move and why". These train fast recognition ("this is a Lagrange multiplier situation", "this is an AM-GM problem"), which is usually the bottleneck when math skills go rusty.
- **Non-redundant.** Don't reword the same fact 10 times. Vary the angle, the cue and the depth.
- **Fully self-contained, with no dangling references.** A question must be answerable without seeing any other question, the source text or lecture context:
  - Never reference a named theorem, algorithm, definition or equation without restating its content inline or giving enough of a reminder that no lookup is needed. Bad: "Why does step 3 of the algorithm fail on disconnected graphs?" Good: "Dijkstra's algorithm relies on greedily finalizing the closest unvisited vertex. Why does this greedy strategy fail to find shortest paths when edge weights can be negative?" Name the thing, restate what it does, then ask.
  - Don't write "using the formula from section 4.2, show that...". Write the formula out, or name it with enough of its statement that no page-flip is needed.
  - Numbered references to source material (exercise numbers, figure numbers, "problem 12") never appear in the question text. They are fine in `source_ref` for grading and citation.
- **Markdown-clean formatting.** Questions and answer keys are rendered as markdown:
  - Use LaTeX-style math consistently (`$...$` inline, `$$...$$` display) or, if the renderer doesn't support LaTeX, plain but unambiguous notation (`x^2`, `sqrt(x)`, `sum_{i=1}^n`). Pick one convention per bank.
  - Use code fences for code and pseudocode. Describe diagrams, state machines and graphs in a renderable structure (a small markdown table of transitions, an adjacency list, an indented tree or ASCII sketch), not prose that assumes an image.
  - Use markdown lists or tables for multi-part questions and structured answer keys, so a grader can scan the structure at a glance.

## Attaching questions to concepts

A concept is what finds a question, so every new question gets attached.
After appending to `bank.jsonl`, write each new id into the `questions` list of the concept it tests in `courses/<slug>/units.json`.
If no concept covers it, because the concept layer is thin or the question spans the whole unit, put the id in the **unit's own `questions` list**, which holds exactly those.
The two lists are disjoint; `units.unit_questions()` unions them.

Attachment decides when a question may be asked.
`units.askable()` serves a concept-attached question only once every concept it is attached to is `seen`, since a question testing two claims is not a fair review while half of it was never studied.
A question in the unit's own list rides on the unit's stage instead.
An unattached question is not lost, only blunter: it becomes askable when the unit does, not when the specific thing it tests has been studied.

`check_vault.py` errors on an id that resolves to no bank entry, so attach after appending, never before.

## Notes

- If sources are sparse, say so rather than padding with generic questions. Flag thin coverage on a subtopic; don't hide it.
- When expanding an existing bank, focus on under-represented subtopics and types rather than adding evenly everywhere.
