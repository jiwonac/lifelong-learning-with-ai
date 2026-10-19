# Ad-hoc session

This skill teaches what the learner needs to understand one thing they brought: a paper, an autoresearch or auto-litreview report, or a project need.
Use it when the learner says "explain this", "I don't follow this report", "help me read <paper>", "what do I need to know to <task>", or "what's in my learn queue".

An ad-hoc session has no scheduler draw, quiz or study unit.
Carding a paper belongs to `skills/flashcards/SKILL.md` → "Work papers"; this skill covers a first pass before the learner reads it, or a debrief after.

## Rules from the curriculum session

The universal rules in `CLAUDE.md` apply.
"gtg" ends the session at any moment, and "continue" resumes from the record's `cursor`.
Teach as in `skills/tutor/SKILL.md`, including "Broad first, then narrow, then back to broad".

## Opening

1. Run `python3 scripts/adhoc.py open`. If a session is open on the same material, resume from its cursor unless the learner wants a fresh start.
2. Otherwise, find the material yourself, never asking for anything the vault can reach: a file the learner names (usually in `courses/adhoc/sources/`), a URL, or the project need they describe. For a task about code, ask for the repository or file.
3. Copy a document that lives outside the vault into `courses/adhoc/sources/` and name that copy as the record's `source`. A file in Downloads or a temporary folder can disappear mid-session.
4. Ask **one message of questions in chat**:
   - What the learner needs the material for. For a report, which conclusions they must act on or judge. For a paper, whether they will read it after this (first pass) or already have (debrief). For a project, what they need to be able to do.
   - Which formal frameworks the material leans on they have used in their own work, named concretely (for example Bayesian inference, information theory, asymptotic statistics). Having read about a framework is not having used it.

The first answer sets the scope: teach only what that goal depends on.
The second sets the depth: a framework the learner has not used is taught from its basics before anything built on it.

## 1. Map the concepts

List the concepts the scoped material depends on, in prerequisite order, and check each against the vault:

| evidence | treat as |
|---|---|
| a concept in some `courses/*/units.json` with state `seen` | known: one-line reminder, naming its unit |
| a card in the Vault deck (`findNotes`, `deck:Vault <term>`) | known at the depth the card shows: one-line reminder |
| a concept with state `unseen` or `unknown`, or no trace | to teach |

Evidence shows a concept at the depth it was learned, and no deeper.
Cards from a paper the learner skimmed for its methods show they know what the method does, not that they can work its mathematics.
When the material needs more depth than the evidence shows, treat the concept as "to teach" and open it with one quick generative check.
Do not re-test known concepts the material uses only at the depth already shown; testing everything wastes the session.

In the narrow pass, open each "to teach" concept with one quick conceptual question or a self-report (`skills/tutor/SKILL.md` → "Checking prerequisites"); a correct answer moves it to known.
Publish the map in the artifact before teaching: the goal, the known concepts with reminders, and the concepts to teach.
For a long document, have a subagent return the concepts, the claims resting on each, and the passages using them.

## 2. Teach

1. **Broad pass.** Place the material among the vault units and courses it draws on or extends.
2. **Narrow pass.** Teach the "to teach" concepts in order, down to the derivations the goal needs. Advance the record's cursor as each lands.
3. **Synthesis round.** Include one question connecting the material to a related vault unit.
4. **Goal question.** Ask the question the session existed to answer: what the report's main conclusion rests on, what the paper's contribution is, or how they would approach the task.

**Name a source for every explanation** (`CLAUDE.md` rule 4).
Cite the material itself, a source in `courses/*/sources/`, the primary paper the material cites, or a standard reference fetched for the purpose.
A concept explained from general knowledge alone is marked "unverified" in the artifact and is never carded.

**Separate background from claims.**
Teach established background (what a B-tree is) as fact.
Teach a finding of the material itself as that source's claim, with its evidence and how far to trust it.

## 3. Sort what was taught

At "gtg", propose a destination for every concept taught, in the artifact next to any flashcard proposals.
The learner gets one feedback turn, as in `skills/flashcards/SKILL.md` → "At gtg".

| the concept is | destination |
|---|---|
| needed only for this material or task | nowhere; the session record keeps the explanation |
| a fact worth keeping fresh, with no unit to hold it | flashcards only (tags below) |
| part of what an existing unit covers | a new concept on that unit, plus flashcards |
| taught in an earlier ad-hoc session too, with no unit to hold it | see "Promotion" |

**Adding a concept to an existing unit**, only when the unit's reading covers it:

1. Write its `id`, `kind`, `claim` and `prereqs` per `skills/knowledge-map/SKILL.md`, and insert it in sweep order.
2. Set its state to `seen` if the unit has been placed, otherwise `unknown`.
3. Add one or two bank questions through `skills/bank-generator/SKILL.md` and list them in its `questions`.
4. Append a unit `log` entry: `what` = "ad-hoc session <slug> added <concept id>", `failed` empty.
5. Leave `srs` and `cursor` alone.

**Flashcards** follow `skills/flashcards/SKILL.md` → "Writing a card", for verified concepts only.

| card | tags | source line |
|---|---|---|
| on a concept that now lives in a unit | `vault::<course>::<unit-id>`, `vault::concept::<concept-id>` | the course and unit, as usual |
| background with no unit | `vault::topic::<topic>` | `Topic: <topic title>.` |
| a paper's claim | `vault::paper::<slug>`, per "Work papers" | the paper, per "Work papers" |
| a report's claim | `vault::report::<slug>`, with the topic tag when one applies | `Report: <report title>. (<YYYY-MM-DD>)` |

Cards with a unit go to that course's subdeck, paper claims to `Vault::Papers`, and topic and report cards to `Vault::Ad hoc` (`scripts/anki_decks.py --apply` creates it with the Vault preset).
A report-claim card asks what the report claims, like a paper card, and exists only for a claim the learner will cite.

## 4. Record

Write `sessions/<YYYY-MM-DD-HHMM>-adhoc-<slug>.md` (slug: the material in a few kebab-case words) with this front matter:

```
---
kind: adhoc
title: Product quantization in the vector-search report
source_kind: report
source: courses/adhoc/sources/<file> (or another vault path, a URL, or the project need in one line)
topics: [product-quantization, inverted-file-index]
status: done
cursor: inverted-file-index (IVF probing next)
---
```

- `source_kind` is `paper`, `report`, `project` or `other`.
- `topics` lists every concept taught (not reminders) as kebab-case names. Run `python3 scripts/adhoc.py topics` first and **reuse an existing name** whenever it fits; promotion counts exact matches.
- `status` is `open` while the goal question is unanswered and the learner may return, `done` otherwise.

The body is the artifact as markdown, including the sources named and the accepted sorting (card note ids, concept ids, bank ids).
Quote no more of an internal document than the explanation needs.

Then ship as in `skills/session/SKILL.md` → "gtg", with PR title `adhoc-<slug>: <what was taught>`.

## Source-specific notes

**A paper, before the learner reads it.** Teach its prerequisites and the problem it addresses, not the contribution.
Then publish a reading guide: the paper's question, where its contribution sits, and two or three questions to answer while reading.
Leave the record `open` with cursor "debrief after reading".

**A paper, after the learner reads it.** Have the learner answer the questions in `skills/flashcards/SKILL.md` → "Ask what a reading group would ask", and teach where an answer fails.
End by offering to card the paper, per "Work papers", with the debrief as the reading.

**An autoresearch or litreview report.** Scope hard to the conclusions the learner needs.
Before teaching a finding, say what source the report cites for it.
Trace a finding the learner will rely on to the primary source, and record in the artifact whether the source supports it.

**A project need.** Work backwards to the smallest set of concepts the task requires, using the project's own code, data or problem as examples.
The session is done when the learner can say how they would do the task.

## Promotion

A topic gets a home in `units.json` only once it comes back.
`python3 scripts/adhoc.py topics` flags topics taught in more than one session.
At "gtg", propose a home for each flagged topic of this session that has no unit:

- **An existing unit** whose reading covers it: add the concept as above.
- **A new unit in an existing course** that the topic belongs to, if a source exists, via `skills/course/SKILL.md`.
- **A new unit in `courses/adhoc/`**, the catch-all (`share: 0`: quizzed, never drawn for study; `default_priority: 5`; unit ids start with `adhoc-`).

A promoted unit then:

1. Gets a `reading` naming a real source (a vault file, or the primary reference the sessions cited), with the ad-hoc session records in `also_read`.
2. Gets concepts cut from what the sessions taught plus what the source covers.
3. Is placed with the taught concepts `seen` and the rest `unseen`.
4. Gets one review via `python3 scripts/review.py <course>:<unit-id> partial --seen <taught concept ids>`, so its questions enter the quiz.
5. Has its `vault::topic::<topic>` cards retagged with the unit and concept tags (`replaceTags`).
6. Has those cards moved with `python3 scripts/anki_decks.py --apply`.

A `courses/adhoc/` unit that grows into a subject moves to a real course via `skills/course/SKILL.md`.

## The learn queue

Surface the learn queue (`courses/adhoc/sources/`) only when the learner asks.
List the files there (excluding `README.md`) that no `status: done` ad-hoc record names as its `source`, one line each, and let the learner pick.
