# Bank Generator

Use this skill when the user asks to (re)generate or expand a question bank for a topic —
e.g. "generate a question bank for [topic]", "add more questions on [subtopic]", "bulk up
the bank for [topic]." This is a deliberate, occasional, manually-invoked action — never run
it automatically inside a study session. (`tutor` does add the odd question mid-session for
something that came up uncovered; that is a handful of entries, not a generation run.)

## Inputs

- All files under `courses/<slug>/sources/` — treat these as ground truth. If the user hasn't added
  sources for the topic yet, ask them to add material (textbook excerpts, course notes, wiki
  pages, lecture transcripts, problem sets) before generating, or offer to use web search /
  known canonical sources for well-established topics if they explicitly say to.
- The existing `courses/<slug>/bank.jsonl`, if present — read it fully first so you don't
  regenerate near-duplicate questions. Check new questions against existing ones for semantic
  overlap, not just exact string match.
- The `sources` and `notes` fields in the `courses/<slug>/units.json` header — the course's only
  prose, and the instruction about scope and density (below). Its `units` array is also where
  finished questions get attached (see "Attaching questions to concepts").

## Scope: what "the topic" actually covers

The `units.json` header carries the course's prose: `sources` (the bibliography, saying what
each source is *for*) and `notes` (scope, difficulty calibration, and any caveat about the
material). Read both before generating; they are the only course-level instruction there is.

The subtopics `notes` lists are a **floor, not a ceiling**. They document what the user has
already identified as a personal weak spot, not an exhaustive boundary of what's fair game. The
user can't list gaps they don't know they have, so treating that section as the sole target
silently drops content.

The real scope for generation is: **(everything listed in `notes`) UNION (everything the
source material actually covers)**. Concretely:
- Generate full coverage across the entire source (every chapter/section you have material
  for), not just the parts that match the scope bullets.
- Use `notes` to set *emphasis and depth*, not inclusion/exclusion — subtopics it flags
  explicitly (or that its difficulty-calibration section points at) should get denser, harder
  coverage; subtopics it doesn't mention still deserve coverage, just not necessarily at the
  same density.
- If `notes` has a difficulty-calibration paragraph (e.g. "the basics are engrained, skip
  them"), that note constrains *how* to cover the unmentioned/basic material, not *whether*
  to. For material the user has flagged as largely mastered, a **light pass is still
  required**: pull out the hardest, most insightful, or trickiest problems/sections (starred
  sections, "extra" callouts, competition-style problems, general "hidden gems" that stray
  from the obvious/main content) rather than skipping the material outright or drowning it in
  routine recall. The goal is "don't waste density on what's already solid," not "pretend
  this material doesn't exist."
- If in doubt about whether something is in scope, err toward including it — the failure mode
  of a bank that's missing a whole chapter's worth of content is worse than one with slightly
  uneven emphasis.

## Process

1. Read every source file for the topic. Build a mental map of subtopics/sections. For large
   sources (a full book, hundreds of pages), use the large-source protocol below instead of
   reading everything into your own context.
2. Decide a target quantity. Default to enough for real long-term sampling breadth — aim for
   at least 15-25 questions per meaningfully distinct subtopic, more for topics the user
   flags as high-priority. A textbook chapter may results in anywhere from 25 to 100 questions
   or even more, depending on the scope & relevance — when in doubt, generate more rather
   than less; a thin, narrow bank is a worse failure mode than an oversized one. Ask if unspecified and
   the scope is ambiguous.
3. Generate questions per the quality bar below.
4. For each question, write a real `answer_key` sufficient for grading later without
   re-deriving it from scratch, plus `grading_notes` for anything with multiple valid framings.
5. **Self-containedness pass.** Before committing each question, re-read it in isolation (as
   if it were the only thing on the page, no source/lecture/other-question context available)
   and check whether it leans on anything not restated inline — a named theorem/algorithm/
   equation, a exercise/figure number, an assumed setup from "the text." If it does, add the
   missing context directly into the question text (restate the theorem, spell out the
   equation, describe the setup) rather than leaving a dangling reference. This is a mandatory
   editing step, not just a drafting guideline — see the self-containedness rule under the
   quality bar below for the bar to hit.
6. Set `source_ref` so it can double as a priming annotation later (shown to the user when a
   question is asked, and used by the grader to check an answer against the source) — it should
   read cleanly as
   "<topic>#<book/source> <chapter/section title>", e.g.
   `courses/system-design/sources/data-intensive-applications.pdf#Ch5 Replication > Leaders and Followers`.
   Use the real chapter/section title from the source, not just a page number.
7. Append (don't overwrite) new entries to `courses/<slug>/bank.jsonl`, following
   `SCHEMA.md`. Assign IDs as `<topic>-<zero-padded sequential number>`, continuing from the
   highest existing ID. Never rewrite an existing entry in place except to fix a factual error —
   units and past sessions reference questions by id. `check_vault.py` requires every entry to
   carry `id`, `topic`, `subtopic`, `type`, `question`, `answer_key`, `source_ref`, `difficulty`
   and `date_generated`, plus a `course` field wherever the id prefix differs from the directory
   name (for example, when a bank's ids predate the course's slug).
8. Report back a short summary: how many questions added, breakdown by subtopic and type, and
   any gaps in the sources you noticed (subtopics that were thin and might need more source
   material for good question coverage).

## Large-source protocol (books, long PDFs, multi-hundred-page material)

Don't try to hold a whole book in your own context. Fan out to cheap subagents (haiku-tier —
these are extraction/generation tasks, not deep reasoning tasks) in a distributed
map-reduce style, and use a temp metadata file to track state so the job survives being
interrupted/resumed.

1. **Partition.** Split the source into chapter- or section-sized chunks (use the book's own
   table of contents/structure — don't chunk blindly by page count if a logical structure
   exists). Write a manifest to a temp file, e.g.
   `courses/<slug>/.progress/<topic>_manifest.json`, listing each chunk with an id, its
   page/section range, and status (`pending`/`in_progress`/`done`).
2. **Map.** Spawn one cheap subagent per chunk (batched in parallel, not all at once if the
   book is huge — respect reasonable concurrency). Each subagent's job:
   - Read only its assigned chunk.
   - Produce a structured summary of everything covered: every concept, theorem, definition,
     worked example, exercise type, aside, and notable edge case — not just headline
     concepts. This summary is what feeds diversity in the next step, so it should be a wide
     net, not a tight one.
   - Draft candidate questions for its chunk per the quality bar below, tagged with precise
     `source_ref` (chapter/section/page). Explicitly remind each subagent in its prompt of
     the self-containedness rule (name/restate referenced theorems/equations, no bare
     exercise-number references in question text) and the markdown-formatting rule — these
     are easy for a cheap subagent to drop if not stated directly in its instructions.
   - Write its output to a temp file (e.g. `courses/<slug>/.progress/<topic>_chunk<id>.json`)
     and update the manifest entry to `done`. This makes the job resumable — if interrupted,
     re-scan the manifest and only dispatch subagents for chunks still `pending`.
3. **Reduce.** Once all chunks are done, read all the chunk outputs yourself (these are
   short structured summaries/questions, not raw book text, so this is cheap). Dedupe near-
   identical questions across chunk boundaries, check cross-chunk coverage balance, and spot
   check a sample of subagent-drafted answer keys for correctness before committing anything
   to the real bank (cheap subagents can hallucinate on answer keys — verify, don't trust
   blindly).
4. **Commit & clean up.** Append the vetted questions to `courses/<slug>/bank.jsonl`.
   Delete the `.progress/` temp files for this run once the bank write succeeds.

For small/medium sources (a handful of files, well under what fits comfortably in your own
context), skip the orchestration overhead and just do the read-and-generate yourself.

## Factual recall is a question type here

There are no flashcards in this vault. `cards.jsonl` is gone, and the spacing it provided now
comes from the **unit's** SRS, which schedules the whole unit rather than each fact. So anything
that has to be memorized verbatim — a definition, a theorem statement, a piece of notation, a
constant, a name — becomes an ordinary bank question that asks for it:

- **"Define X."** / **"State the X theorem precisely."** — the bare production, no scaffolding.
- **"What does Y mean inside the definition of Z?"** — the one that catches memorized-but-inert
  definitions, where every symbol is recalled and none of them mean anything.
- **"Contrast the definition of A with that of B."** — for the pairs that are confusable exactly
  because their definitions are one clause apart (independent vs. uncorrelated, serializable vs.
  strict, isomorphism vs. homomorphism).

Write them **generatively, like everything else** — "define X", never "which of these defines X",
and never a cloze deletion of a sentence from the source, which tests the sentence rather than
the idea.

Two calibration points, because this type is easy to get wrong in both directions:

- **These are a minority, not the bulk.** They are connective tissue for genuinely fact-shaped
  content. A bank that collapses into definition prompts is the failure mode the whole system
  exists to avoid.
- **But do not skip them.** Nothing else in the vault covers bare facts now, and a learner who
  can derive a result while being unable to state the theorem it rests on is a real and common
  state. If a chapter introduces vocabulary that later chapters use without re-explaining, that
  vocabulary needs recall questions.

Attach these to a concept like any other question; the same eligibility rule applies, so a
definition question is only ever asked once the concept it defines has been studied.

## Quality bar for questions

- **Generative, always.** No multiple choice anywhere in this vault, and no cloze deletions.
  Recognition is handled by the learner's own immersive reading; every question the system asks
  must require a production. A question whose answer can be pointed at rather than stated does
  not belong in the bank.
- **Grounded**: every question must be answerable from the sources (or common canonical
  knowledge of the field if sources are thin on a point) — no fabricated facts.
- **Cover every facet, not just the core concepts.** A source is more than its headline
  theorems/definitions. Deliberately mine: worked examples and their variations, footnotes
  and asides, historical/motivational context, edge cases and exceptions to general rules,
  the exercises/problems the source itself poses, connections it draws to other topics, and
  places where the source flags common misconceptions. If your question set could have been
  written from a one-page summary of the source, you haven't gone deep enough — go back and
  pull from the parts of the text that don't show up in a summary.
- **Diverse in type — push hard for this, it's a primary quality axis, not an afterthought.**
  A chapter-sized batch should visibly draw from most of the repertoire below, not lean on
  3-4 comfortable types. Rotate through:
  - Definitions / "what is X and why does it matter"
  - Compare & contrast ("how does X differ from Y", "when would you use X vs Y")
  - Explain-in-own-words / mechanism ("why does X happen", "explain the reasoning behind X")
  - Application / scenario ("given this situation, what would you do / predict")
  - Error-spotting / critique ("here's a flawed argument or solution — what's wrong")
  - Short math or coding problems (if the topic involves them) — solvable in a few
    lines/steps, not full projects
  - Short-answer / short-paragraph synthesis questions
  - Definition / statement recall — "define X", "state the X theorem precisely", "what does Y
    mean inside the definition of Z" (see the factual-recall section above; a minority of the
    bank, but the only thing covering bare facts now that cards are gone)
  - Multi-part or "explain then apply" combos
  - **Proof/derivation questions**: "prove that...", "derive...", "show that..." — standard
    in any math/CS/physics course, distinct from a generic "math problem" in that the point
    is the logical chain, not a numeric answer.
  - **Estimation / order-of-magnitude / sanity-check questions**: "roughly how does X scale
    with n", "is this quantity closer to 10 or 10,000, and how do you know without
    computing exactly" — trains the intuition-checking reflex that catches your own errors.
  - **Counterexample construction**: "give an example where X holds but Y fails" / "construct
    a case that breaks this proposed rule" — a distinct skill from error-spotting (you're
    the one introducing the flaw, not diagnosing someone else's).
  - **"Design/construct an X satisfying constraints Y and Z"** — open-ended-but-checkable
    construction tasks (build an automaton, propose a data structure, sketch an algorithm)
    where the answer key gives one valid construction plus the checkable criteria, since
    multiple correct answers may exist.
  - **Analogy/transfer questions**: "how does concept X here relate to concept Y from
    [another topic/subtopic]" — builds cross-topic connective tissue rather than treating
    each subtopic as an island.
  - **"Explain to a beginner" / rubber-duck questions**: forces plain-language fluency
    separate from formal-notation fluency — you can manipulate the symbols but can you
    actually explain the idea.
    This list is illustrative, not exhaustive or mandatory in exact proportion — use judgment
    per topic (e.g. a math-heavy topic skews toward problems/proofs/estimation; a conceptual
    humanities topic skews toward explain/compare/critique/analogy). But default to breadth:
    if you notice a batch only used 3-4 types, deliberately go back and add questions in types
    you skipped before finalizing.
- **Nontrivial and difficult should be the norm, not a minority carve-out.** Aim for roughly
  half or more of questions (higher for topics that support it) to require actual thinking —
  combining two ideas, spotting a non-obvious consequence, working through a multi-step
  derivation, constructing something new, or applying a concept somewhere the source didn't
  spell out directly. Shallow recall/definition questions should be the minority, present
  mainly as connective tissue or for genuinely fact-shaped content (dates, names, exact
  statements of notation) — not the default mode. Don't let the bank collapse into
  all-shallow-recall; the point of this system is retention through active problem-solving.
- **Time-boxed difficulty**: every question should be solvable by someone who has studied
  the material recently — within a few minutes for typical questions, and no more than
  ~10 minutes even for the hardest ones. Nontrivial does not mean long or research-y; it
  means it takes real thought to execute, not real time. If a question would take a fresh
  page of derivation or more than ~10 minutes even for someone fluent in the material, split
  it into a shorter, sharper question or cut it.
- **For math-flavored topics, include "gist recall" questions** aimed at building an
  intuition library, not just mechanical fluency: "what family of technique applies to a
  problem shaped like X", "what's the key trick/insight for solving Y", "given this
  problem's shape, what's your first move and why". These train fast pattern-matching
  (recognizing "oh, this is a Lagrange multiplier situation" or "this is an AM-GM problem")
  rather than rote step-execution — that recognition step is usually the actual bottleneck
  when math skills go rusty.
- **Non-redundant**: don't just reword the same fact 10 times. Vary the angle, the cue, and
  the depth (some shallow recall, some genuine synthesis/application).
- **Fully self-contained — no dangling references.** A question must be answerable without
  seeing any other question, the source text, or lecture context. Concretely:
  - Never reference a named theorem/algorithm/definition/equation without either restating
    its content inline or giving enough of a reminder that no external lookup is needed.
    Bad: "Why does step 3 of the algorithm fail on disconnected graphs?" Good: "Dijkstra's
    algorithm relies on greedily finalizing the closest unvisited vertex. Why does this
    greedy strategy fail to find shortest paths when edge weights can be negative?" — name
    the thing, then restate what it does, then ask the question.
  - Same discipline for equations/theorems: don't write "using the formula from section 4.2,
    show that...". Either write the formula out, or name it precisely enough (with enough
    of its statement) that no page-flip is required.
  - Numbered references to source material (exercise numbers, figure numbers, "problem 12")
    should never appear in the question text itself — those are fine internally in
    `source_ref` for grading/citation purposes, but the question a person actually reads
    must stand alone.
- **Markdown-clean formatting.** Questions and answer keys are rendered as markdown, so:
  - Use LaTeX-style inline/display math consistently (`$...$` for inline, `$$...$$` for
    display) or, if the target renderer doesn't support LaTeX, plain-but-unambiguous
    notation (`x^2`, `sqrt(x)`, `sum_{i=1}^n`) — pick one convention per bank and stay
    consistent within it.
  - Use code fences for code/pseudocode, and describe diagrams/state-machines/graphs in a
    structured, renderable way (a small markdown table of transitions, an adjacency list, an
    indented tree/ASCII sketch) rather than prose that assumes an image the reader can't see.
  - Use markdown lists/tables for multi-part questions or structured answer keys instead of
    run-on paragraphs — a grader (human or Claude) should be able to scan the structure at a
    glance.

## Attaching questions to concepts

A question is only worth generating if something can find it, and what finds it is a concept.
After appending to `bank.jsonl`, write each new id onto the concept it tests, in that concept's
`questions` list in `courses/<slug>/units.json`. Where the unit has no concept that covers it —
because the concept layer is thin, or because the question spans the unit rather than any one
claim — put the id in the **unit's own `questions` list**, which holds exactly those. The two
lists are disjoint; `units.unit_questions()` unions them.

Attachment is what decides when a question may be asked. `units.askable()` serves a
concept-attached question only once every concept it is attached to is `seen` — a question
testing two claims cannot be a fair review while half of what it tests was never studied — and a
question in the unit's own list rides on the unit's stage instead. So an unattached question is
not lost, only blunter: it becomes askable as soon as the unit does, rather than when the
specific thing it tests has been studied.

`check_vault.py` errors on an id that resolves to no bank entry, so attach after appending, never
before.

## Notes

- If sources are sparse, say so explicitly rather than padding with generic questions — thin
  coverage on a subtopic should be flagged, not hidden.
- If the user asks to expand an existing bank, focus generation on under-represented
  subtopics/types rather than adding evenly everywhere.
