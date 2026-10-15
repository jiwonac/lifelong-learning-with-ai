# Knowledge Map

This skill cuts and maintains the `concepts` array on each unit in `courses/<slug>/units.json`.
Use it when the learner asks to build or refresh a course's concepts, when a course gains sources, or when `place` or `tutor` hits a unit whose `concepts` is still empty.
Building the layer is a deliberate, occasional action, not per-session.

A concept lives on the unit that owns it, in sweep order:

```json
{"id": "ir-attn-scaled", "kind": "claim",
 "claim": "Scaling by 1/sqrt(d_k) keeps the dot products out of the region where softmax saturates, which is why it is there and not for normalization.",
 "prereqs": ["ir-attn-soft-lookup"],
 "external_prereqs": ["linear-algebra: dot products as similarity"],
 "state": "unseen",
 "questions": ["information_retrieval-000451"]}
```

**This skill owns everything in that record except `state`**, which `place`, `tutor` and `grader` write.
Field meanings are in `CLAUDE.md` → "concepts".

Consumers of the layer:

- **`tutor`** sweeps the array in order from the `cursor`, stopping at the first friction. Without a concept list, a session becomes an unordered quiz. Where the material forks, both branches get swept.
- **`place`** spreads its few questions across the graph's depth bands instead of clustering them at the roots.
- **`grader`** reads a missed claim and a missed skill as different evidence, which is why `kind` matters.
- **`scripts/units.py`** uses `questions` to decide what is askable. A thin concept layer makes the quiz blunter but does not break it.

## The node set

A node is one claim or one skill (see `CLAUDE.md` → "Levels of abstraction"), never a chapter or a topic.

Write the `claim` as a sentence that asserts something, not a label.
"Cosine similarity" is a heading.
"The vector space model normalizes by length because raw dot products reward long documents" is a concept: `tutor` teaches against it and a question can be checked against it.

Target granularity: one node is one reasoning step, which `tutor` can teach and quiz in a few minutes.
If the graph comes out heavily non-linear, the unit is probably two units.

Get a starting node set from these sources, in order of preference:

1. **The existing bank.** Extract and dedupe the `subtopic` fields in `courses/<slug>/bank.jsonl`; they usually cluster tightly to source sections. Each node derived this way lists the question ids that cover it in `questions`.
2. **The header's `notes` and `sources`, plus the source's own structure**, for anything the bank doesn't reach yet. The scope prose is a floor, not a ceiling, as in `skills/bank-generator/SKILL.md`.

## The edges

The edge definition and threshold are in `CLAUDE.md` → "Prerequisites".
Ask whether B would cause incomprehension or leave the learner with no first move without A; if neither, there is no edge.
`tutor` uses the same partial-grasp threshold when deciding it can move on.

Avoid two mistakes:

- **Treating narrative order as dependency order.** A book presenting X before Y does not make X a prerequisite of Y.
- **Suppressing edges across topic boundaries.** These are the valuable ones. A question on Gaussian mixture models can fail on a probability prerequisite rather than on the mixtures. Edges into other courses go in `external_prereqs`; do not drop them to keep the graph tidy.

Keep the graph acyclic.
A cycle means the nodes are cut wrong: merge them or split the shared dependency out.
`check_vault.py` catches a cycle but does not say where the cut went wrong.

### Concept edges are ordering hints, never gates

No script gates anything on a concept's `prereqs`.
A wrong concept edge costs only a slightly odd sweep order, so spend judgment on the unit graph, where a wrong edge blocks material.
**Do not smuggle a hard dependency in as a concept edge.**
If an unstudied prerequisite would actually stop the learner, put it on the unit.

### `external_prereqs`

Write cross-course dependencies as a descriptive phrase, such as `"linear-algebra: dot products as similarity"`, not an id.
An id that resolves to nothing is worse than prose.
Nothing parses these phrases; they serve the tutor and the promotion decision below.

### Promoting a cross-course concept edge to a unit edge

Promote an `external_prereqs` entry to a unit-level prerequisite, written `<course>:<unit>`, only when an unstudied source unit would leave a substantial part of the target unit incomprehensible.
A promoted edge blocks the target unit from study and quiz until the source reaches `learning`, so a wrong promotion blocks material.

Three patterns look like edges and are not:

- **Sibling coverage.** A databases unit on the web as a database builds PageRank from the transition matrix itself; it does not need the IR (information retrieval) course's PageRank unit first.
- **A self-contained target.** Sort-merge join and index range scan are developed from scratch on the database side, even though the IR course reaches the same ideas. A shared idea is not a shared prerequisite.
- **One peripheral concept.** A single concept in a twenty-concept unit needing outside background stays in `external_prereqs`.

Expect very few to survive.
Cross-linking a databases course with an IR course, one of 17 concept-level edges did: a unit on the Red Book's web-data essays says it assumes inverted indexing and TF-IDF, so it carries unit prerequisites on those IR units.
Resolve these by hand.
Matching phrases to ids automatically produces plausible but wrong edges.

## Attaching questions

Write bank ids into a concept's `questions`, never a count.
A question may attach to more than one concept; it is askable only when every attached concept is `seen`.
A question no concept claims goes in the unit's own `questions` list (see `CLAUDE.md` → "concepts").

## Maintenance

The concept layer changes when the material changes: a source is added, a unit is re-cut, a concept turns out to be two, or an edge turns out not to predict either failure.
It does not change because a session went badly; that is `state`.

Update the linked pieces in the same pass:

- **Renaming or splitting a concept** breaks any `prereqs` that names it, and possibly the unit's `cursor`.
- **Re-cutting units** moves concepts between records. Each concept id appears in exactly one unit.
- **Deleting a concept** orphans its `questions`. Move them to another concept or to the unit's own list; never drop them.

Run `python3 scripts/check_vault.py` afterwards (its checks are listed in `CLAUDE.md` → "Scripts TL;DR").
It does not check these, so you must:

- the `concepts` array is in topological order (it is the sweep order).
- `external_prereqs` phrases mean something.
- each claim asserts something rather than naming a heading.
