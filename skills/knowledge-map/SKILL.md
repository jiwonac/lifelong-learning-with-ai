# Knowledge Map

This skill cuts and maintains the concept layer inside `courses/<slug>/units.json`: the `concepts` array on each unit.
Each concept holds what it claims, what it depends on, and which bank questions test it.
Use it when the learner asks to build or refresh a course's concepts, when a course gains sources, or when `place` or `tutor` hits a unit whose `concepts` is still empty.

A concept lives on the unit that owns it, in sweep order:

```json
{"id": "ir-attn-scaled", "kind": "claim",
 "claim": "Scaling by 1/sqrt(d_k) keeps the dot products out of the region where softmax saturates, which is why it is there and not for normalization.",
 "prereqs": ["ir-attn-soft-lookup"],
 "external_prereqs": ["linear-algebra: dot products as similarity"],
 "state": "unseen",
 "questions": ["information_retrieval-000451"]}
```

**This skill owns everything in that record except `state`.**
`place`, `tutor` and `grader` write `state` as the learner works.
Structure changes only when the material does; `state` changes every session.

Three consumers depend on the concept layer:

- **`tutor`** sweeps the `concepts` array in order, forward from the unit's `cursor`, stopping at the first friction. Without a concept list, a session becomes an unordered quiz. The order only needs to be walkable, not strictly linear: where the material forks, both branches get swept.
- **`place`** spreads its few questions across the graph's depth bands instead of clustering them at the roots. It reads the structure and writes only `state`.
- **`scripts/units.py`**: `unit_questions()` unions the concept-level `questions` lists with the unit's own, and `askable()` refuses a question while any concept it is attached to is not `seen`. A question no concept claims sits in the unit's own `questions` list and rides on the unit's stage. A thin concept layer makes the quiz blunter but does not break it.

Building the layer is a deliberate, occasional action, like bank generation, and not per-session.

## The node set

A node is a **concept**: a distinct claim or a distinct skill within a unit, never a chapter or a topic.
This is the third of the vault's three levels (course, unit, concept); do not invent a fourth.

- **Claim**: "a page table maps VPN→PFN, so translation is an array index." The learner can regenerate it or cannot.
- **Skill**: "the learner can fluently solve telescoping sums of this shape." Fluent, halting, or absent. Write skills as capabilities starting "the learner can …".

`kind` records which.
The two fail differently, so `grader` reads a missed claim and a missed skill as different evidence.

Write the `claim` as a sentence that asserts something, not a label.
"Cosine similarity" is a heading.
"The vector space model normalizes by length because raw dot products reward long documents" is a concept: `tutor` teaches against it and a question can be checked against it.
A one-noun claim means the cut has not been made yet.

Target granularity: one node is one reasoning step, which `tutor` can teach and quiz in a few minutes.
The concept graph is mostly a linear chain with a few branches.
If it comes out heavily non-linear, the unit is probably two units.

Get a starting node set from these sources, in order of preference:

1. **The existing bank.** `courses/<slug>/bank.jsonl` carries a `subtopic` field, and subtopics usually cluster tightly to source sections. Extract and dedupe them first. Each node derived this way records the question ids that cover it in its `questions` list.
2. **The `units.json` header's `notes` and `sources`, plus the source's own structure**, for anything the bank doesn't reach yet. The scope prose is a floor, not a ceiling (see `bank-generator/SKILL.md`); the same rule applies here.

## The edges

An edge `A --> B` asserts: **without at least a partial grasp of A, B will not make sense, or you will blank on how to tackle it.**

- **The failure it predicts** is incomprehension ("this sentence is words") or paralysis ("I know what is being asked and have no idea where to start"). If neither would happen, there is no edge. B being easier with A, or usually taught after A, is not an edge.
- **The threshold is partial, not complete.** A needs to be somewhat recognizable or partially generable, not mastered. `A --> B` does **not** mean all of A must be closed before B can begin.

At unit granularity, **an edge is satisfied once its source unit reaches `learning`**, that is, once it has been studied once.
A unit still at `unknown` or `new` blocks what depends on it; nothing else does.
Concept edges gate nothing (below), but `tutor` uses the same threshold when deciding it can move on.
Requiring completion would serialize the curriculum for no reason, and starting the dependent material often consolidates its prerequisite.

Draw an edge only where that claim holds. Avoid two mistakes:

- **Treating narrative order as dependency order.** A book presenting X before Y does not make X a prerequisite of Y. Ask whether B would stop making sense, or leave you with no first move, without A.
- **Suppressing edges across topic boundaries.** These are the valuable ones. A placement pass once chased a differential-forms question down into special relativity, because that is where the strand went. A question on Gaussian mixture models can fail on a probability prerequisite rather than on the mixtures. Edges into other courses go in `external_prereqs`; do not drop them to keep the graph tidy.

### Concept edges are ordering hints, never gates

`prereqs` on a concept orders the sweep and nothing else.
**No script gates anything on it.**
Unit-level `prereqs` decide eligibility, and concept `state` decides question fairness.
A wrong concept edge costs only a slightly odd sweep order.

So concept edges need to be walkable, not exactly right.
Spend judgment on the unit graph, where a wrong edge blocks material.

**Do not smuggle a hard dependency in as a concept edge.**
If an unstudied prerequisite would actually stop the learner, put it on the unit, where the scheduler reads it.

### `external_prereqs`

Cross-course dependencies go here as a descriptive phrase rather than an id, such as `"linear-algebra: dot products as similarity"`.
The other course may have no exactly matching concept, and an id that resolves to nothing is worse than prose.
Nothing parses these phrases; they serve the tutor and the promotion decision below.

### Promoting a cross-course concept edge to a unit edge

Promote an `external_prereqs` entry to a `units.json` unit-level prerequisite, written `<course>:<unit>`, only in some cases.
The scheduler reads unit edges, and a unit edge makes a much stronger claim than a concept edge.

Promote only when the edge holds at unit granularity: an unstudied source unit would leave a substantial part of the target unit incomprehensible.
A promoted edge stops the target unit from being scheduled or quizzed until the source has been studied once, so a wrong promotion blocks material.

Three patterns look like edges and are not.
The examples come from cross-linking a databases course with an information retrieval (IR) course:

- **Both courses teach the same thing.** A databases unit on the web as a database builds PageRank from the transition matrix itself; it does not need the IR course's PageRank unit first. This is sibling coverage.
- **The target is self-contained.** Sort-merge join, index range scan and blocking operators are each developed from scratch on the database side, even though the IR course reaches the same ideas. A shared idea is not a shared prerequisite.
- **One peripheral concept.** A single concept in a twenty-concept unit needing outside background does not make the unit depend on that course. Leave it in `external_prereqs`.

Expect very few to survive.
In the databases and IR example, one of 17 concept-level edges did.
A unit on the Red Book's web-data essays presumes inverted indexing and TF-IDF, because the essays say they assume them, so that unit carries unit prerequisites on the IR course's inverted-index and TF-IDF units.
Resolve these by hand.
Matching phrases to ids automatically produces plausible but wrong edges, and a wrong prerequisite misroutes every session that reads it.

Keep the graph acyclic.
A cycle means the nodes are cut wrong: merge them or split the shared dependency out.
`check_vault.py` catches a cycle as a structural error, but it does not say where the cut went wrong.

## Attaching questions

`questions` on a concept lists the bank ids that test it.
Write ids, never a count; `askable()` reads this list.

**A question may attach to more than one concept**, since one question often tests two claims.
`askable()` then applies the strictest reading: the question is fair only when **every** attached concept is `seen`.

A question the unit owns but no concept claims goes in the **unit's own `questions` list**, which holds only those.
The two lists are disjoint, and `unit_questions()` unions them.

## Maintenance

The concept layer changes when the material changes: a source is added, a unit is re-cut, a concept turns out to be two, or an edge turns out not to predict either failure.
It does not change because a session went badly; that is `state`, and `grader` writes it.

When you change it, update the linked pieces in the same pass or the checker fails:

- **Renaming or splitting a concept** breaks any `prereqs` that names it, and possibly the unit's `cursor`. Fix them.
- **Re-cutting units** moves concepts between records. A concept id must be unique across the whole course and appear in exactly one unit.
- **Deleting a concept** orphans its `questions`. Move them to another concept or to the unit's own list; do not drop them, because the bank entry still exists.

Run `python3 scripts/check_vault.py` afterwards. On the concept layer it enforces exactly:

- `kind` is `claim` or `skill`, and `claim` is non-empty.
- `state` is one of `unknown` / `unseen` / `seen`.
- every cited question id exists in some bank.
- concept ids are unique within a unit and across the course.
- every concept `prereq` resolves to a concept **in the same course**, and the concept graph is acyclic.
- `cursor.concept`, if set, is one of the unit's own concepts.
- unit size: a warning above 25 concepts, an error above 35.

It does not check these, so you must:

- the `concepts` array is in topological order (it is the sweep order).
- `external_prereqs` phrases mean something.
- each claim asserts something rather than naming a heading.
