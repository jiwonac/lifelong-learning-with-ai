# Knowledge Map

Cuts and maintains the **concept layer inside `courses/<slug>/units.json`** — the `concepts`
array on each unit, holding what each concept claims, what it depends on, and which bank
questions test it. Use when the user asks to build or refresh a course's concepts, when a course
gains sources, or when `place`/`tutor` hits a unit whose `concepts` is still empty.

There is no separate map file. A concept lives on the unit that owns it, in sweep order:

```json
{"id": "ir-attn-scaled", "kind": "claim",
 "claim": "Scaling by 1/sqrt(d_k) keeps the dot products out of the region where softmax saturates, which is why it is there and not for normalization.",
 "prereqs": ["ir-attn-soft-lookup"],
 "external_prereqs": ["linear-algebra: dot products as similarity"],
 "state": "unseen",
 "questions": ["information_retrieval-000451"]}
```

**This skill owns everything in that record except `state`.** `state` is written by `place`,
`tutor` and `grader` as the learner works; structure is written here. They are separate
responsibilities in the same record, which is fine — structure changes when the material does,
which is roughly never, and the field that changes every session is exactly one word.

This is the vault's connective tissue. Three consumers depend on it:

- **`tutor` sweeps the `concepts` array in order** — forward from the unit's `cursor`, fast,
  stopping at the first friction. Without a concept list there is no order to sweep, so a session
  degenerates into an unordered quiz. The order only needs to be *walkable*, not strictly linear:
  where the material forks, both branches get swept.
- **`place`** spreads its handful of questions across the graph's depth bands rather than
  clustering them at the roots, so the edges are what make a placement informative. It reads the
  structure and writes only `state`.
- **`scripts/units.py`** — `unit_questions()` unions the concept-level `questions` lists with the
  unit's own, and `askable()` refuses to serve a question while any concept it is attached to is
  not `seen`. A question no concept claims sits in the unit's own `questions` list and rides on
  the unit's stage instead — so a thin concept layer does not break the quiz, it just makes it
  blunter.

Building it is a deliberate, occasional action, like bank generation — not per-session.

## The node set

A node is a **concept**: a distinct *claim* or a distinct *skill* within a unit — never a chapter
or a topic. This is the third of the vault's three locked levels (course → unit → concept); do
not invent a fourth.

- **Claim** — "a page table maps VPN→PFN, so translation is an array index." Either regenerable
  or not.
- **Skill** — "the learner can fluently solve telescoping sums of this shape." Fluent, halting, or
  absent. Write these as capabilities, starting *"the learner can …"*, not as facts.

`kind` records which, and the distinction is not decoration: the two fail differently, so
`grader` reads a missed claim and a missed skill as different evidence.

Write the `claim` as a **sentence that asserts something**, not a label. "Cosine similarity" is a
heading; "the vector space model normalizes by length because raw dot products reward long
documents" is a concept — it is what `tutor` teaches against and what a question can be checked
against. A one-noun claim means the cut has not been made yet.

Target granularity: one node ≈ one reasoning step ≈ one thing `tutor` can teach and quiz in a few
minutes. The concept graph is **primarily a linear chain with a few branches** — if it comes out
heavily non-linear, the unit is probably two units.

Two cheap sources of a starting node set, in order of preference:

1. **The existing bank.** `courses/<slug>/bank.jsonl` already carries a `subtopic` field,
   and in most topics those cluster tightly to source sections. Extract and dedupe them first
   — this is nearly free and grounded in material already vetted. Every node so derived should
   record which question IDs cover it, in its `questions` list.
2. **The `units.json` header's `notes` and `sources`, plus the source's own structure**, for
   anything the bank doesn't reach yet. Note that the scope prose is a floor, not a ceiling (see
   `bank-generator/SKILL.md`) — the same rule applies here.

## The edges

An edge `A --> B` asserts: **without at least a partial grasp of A, B will not make sense, or you
will blank on how to tackle it.**

Two halves of that, and the second is the one people get wrong:

- **The failure it predicts** is either incomprehension ("this sentence is words") or paralysis
  ("I know what is being asked and have no idea where to start"). If neither would happen, there
  is no edge — B being *easier* with A, or *usually taught after* A, is not an edge.
- **The threshold is partial, not complete.** A needs to be somewhat recognizable or partially
  generable — not finished, not mastered, not `done`. `A --> B` does **not** mean 100% of A must
  be closed before B can begin.

Operationally, at unit granularity: **an edge is satisfied once its source unit reaches
`learning`** — that is, once it has been studied even once. A unit still at `unknown` or `new`
blocks what depends on it; nothing else does. At concept granularity there is no gate at all
(below), but the same threshold is what `tutor` uses when deciding it can move on.

That "studied once" clears the bar is the whole point. Requiring completion serializes a
curriculum for no reason and is exactly why textbooks feel like they must be read front to back.
A learner who has been through the source once has enough to start what depends on it — and
starting is often what consolidates the thing it depends on.

Draw an edge only where that claim holds. Two failure modes to avoid:

- **Narrative order is not dependency order.** A book presenting X before Y does not make X a
  prerequisite of Y. Ask whether B would genuinely stop making sense, or leave you with no
  first move, without A.
- **Edges across topic boundaries are the valuable ones.** A placement pass in the reference
  method chased a differential-forms question down into special relativity, because that's where
  the strand actually went. In the same way, a question on Gaussian mixture models can fail on
  a probability prerequisite rather than on the mixtures themselves. Edges into other courses are what let a
  session find that; they go in `external_prereqs` and should not be suppressed to keep the graph
  tidy.

### Concept edges are ordering hints, never gates

`prereqs` on a concept orders the sweep and nothing else. **No script gates anything on it** —
eligibility is decided entirely by unit-level `prereqs`, and question fairness entirely by
concept `state`. A wrong concept edge costs a slightly odd sweep order, and that is the whole of
the damage.

This is what makes the layer cheap to keep. Thousands of concepts is a lot of edges to be right about,
and they do not have to be right — only walkable. Spend the judgement on the unit graph, where a
wrong edge blocks material, and let the concept graph be approximately correct.

The corollary: **do not smuggle a hard dependency in as a concept edge.** If an unstudied
prerequisite would actually stop the learner, it belongs on the unit, where the scheduler reads
it.

### `external_prereqs`

Cross-course dependencies land here, as a descriptive phrase rather than an id —
`"linear-algebra: dot products as similarity"`. The far end is a phrase because the other course
may have no concept that matches exactly, and inventing an id that resolves to nothing is worse
than prose. Nothing parses them; they are for the tutor
and for the promotion decision below.

### Promoting a cross-course concept edge to a unit edge

Only some `external_prereqs` should be **promoted** to a `units.json` unit-level prerequisite
written `<course>:<unit>`, because that is what the scheduler reads and a unit edge makes a much
stronger claim than a concept edge.

Promote only when the edge would still be true at unit granularity — when an *unstudied* source
unit would leave a *substantial part* of the target unit incomprehensible. Remember what the
promoted edge then does: it stops the target unit being scheduled or quizzed at all until the
source has been studied once, so a wrong promotion doesn't merely mislead, it blocks.

Three patterns look like edges and are not. The examples are from cross-linking a databases
course with an information retrieval (IR) course:

- **Both courses teach the same thing.** A databases unit on the web as a database builds
  PageRank from the transition matrix itself; it does not depend on the IR course's PageRank
  unit teaching it first. Sibling coverage, not dependency.
- **The target is self-contained.** Sort-merge join, index range scan and blocking operators are
  each developed from scratch on the database side, even though the IR course reaches the same
  ideas. A shared idea is not a shared prerequisite.
- **One peripheral concept.** A single concept in a twenty-concept unit needing outside
  background does not make the unit depend on that course. Leave it in `external_prereqs`.

Expect very few to survive. In the databases and IR example, one of 17 concept-level edges did:
a unit on the Red Book's web-data essays genuinely presumes inverted indexing and TF-IDF, because
the essays say in as many words that they assume them, so that unit carries unit prerequisites on
the IR course's inverted-index and TF-IDF units. Resolve these by hand. Matching phrases to ids
automatically produces plausible-but-wrong edges, and a wrong prerequisite misroutes every
session that reads it.

Keep the graph acyclic. A cycle means the nodes are cut wrong — merge them or split the shared
dependency out. `check_vault.py` catches it, but it catches it as a structural error, not as a
hint about where the cut went wrong.

## Attaching questions

`questions` on a concept is the list of bank ids that test it. Write ids, never a count — this is
the list `askable()` reads.

**A question may legitimately attach to more than one concept**; one question often tests two
claims at once. Where that happens `askable()` applies the strictest reading: a question is fair
only when **every** concept it is attached to is `seen`, because it cannot be a fair review while
part of what it tests was never studied.

A question the unit owns but no concept claims goes in the **unit's own `questions` list**, which
holds only those — the two lists are disjoint by construction, which is why neither is redundant.
`unit_questions()` unions them.

## Maintenance

The concept layer changes when the **material** changes: a source is added, a unit is re-cut, a
concept turns out to be two concepts, an edge turns out not to predict either failure mode. It
does not change because a session went badly — that is `state`, and `grader` writes it.

When you do change it, things move together or the checker fails:

- **Renaming or splitting a concept** breaks any `prereqs` that names it, and possibly the unit's
  `cursor`. Fix them in the same pass.
- **Re-cutting units** moves concepts between records. A concept id must be unique across the
  whole course and appear in exactly one unit; two units claiming the same id is an error.
- **Deleting a concept** orphans its `questions`. Move them to another concept or to the unit's
  own list — do not drop them, the bank entry still exists.

Run `python3 scripts/check_vault.py` afterwards. On the concept layer it enforces exactly:

- `kind` is `claim` or `skill`, and `claim` is non-empty.
- `state` is one of `unknown` / `unseen` / `seen`.
- every cited question id exists in some bank.
- concept ids are unique within a unit and across the course.
- every concept `prereq` resolves to a concept **in the same course**, and the concept graph is
  acyclic.
- `cursor.concept`, if set, is one of the unit's own concepts.
- unit size: a warning above 25 concepts, an error above 35.

What it does **not** check, and you therefore have to: that the `concepts` array is in a
topological order (it is the sweep order, and nothing validates it), that `external_prereqs`
phrases mean anything, and that a claim says something rather than naming a heading.
