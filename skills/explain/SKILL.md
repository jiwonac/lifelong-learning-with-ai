# Explain

Teaches what the learner needs to understand one thing they brought: a paper, an autoresearch or
auto-litreview report, or a project need. Use when the learner says "explain this", "I don't
follow this report", "help me read <paper>", "what do I need to know to <task>", or "what's in my
learn queue".

This is not a study session. Nothing is drawn from the scheduler, there is no quiz, and no unit is
studied. The session teaches the gaps in the learner's understanding of the material, then sorts
each concept it taught into the systems that already exist: nowhere, a flashcard, a concept on an
existing unit, or (on a repeat) a new unit. Nothing new is scheduled, so nothing here can build a
backlog.

Carding a paper the learner has already read and starred is still `skills/flashcards/SKILL.md` →
"Work papers". This skill covers the reading around it: a first pass before the learner reads, or
a debrief after.

## The rules carried over

Three rules from `skills/session/SKILL.md` apply unchanged:

1. **Everything the learner reads goes in the artifact.** The concept map, every explanation,
   question, answer, diagram and proposal. Chat carries turn-taking only.
2. **Any duration must work.** The session ends when the learner says "gtg". The record's
   `cursor` makes stopping safe at any moment, and "continue" resumes from it.
3. **Every question is generative.** No multiple choice.

Teaching follows `skills/tutor/SKILL.md`, including its three layers: broad first, then narrow,
then a synthesis round. In the narrow layer: leading questions, one reasoning step at a time,
split a failed step before re-explaining, ask for the mechanism. A step that fails twice after
splitting is a missing prerequisite; teach that first.

## Opening

Run `python3 scripts/explain.py open`. If a session is open on the same material, say so and
resume from its cursor unless the learner wants a fresh start.

Otherwise, find the material without asking for anything the vault can reach. When the optional
Raindrop integration is connected, a paper or report saved in Raindrop is fetched there (bookmark
note and highlights first, then full text). A file
the learner names is read from disk. A project need is whatever the learner described; ask for
the repository or file when the task concerns code the session can read.

Then ask **one question in chat**: what the learner needs the material for. For a report, which
conclusions they have to act on or judge. For a paper, whether they will read it themselves after
this (first pass) or already have (debrief). For a project, what they need to be able to do. The
answer sets the scope: the session teaches only what that goal depends on.

## 1. Map the concepts

List the concepts the scoped material depends on, in prerequisite order, and check each against
what the vault already knows about the learner:

| evidence | treat as |
|---|---|
| a concept in some `courses/*/units.json` with state `seen` | known: one-line reminder, naming its unit |
| a card in the Vault deck (`findNotes`, `deck:Vault <term>`) | known: one-line reminder |
| a concept with state `unseen` or `unknown`, or no trace | to teach |

The vault's evidence is a guess. In the narrow pass (section 2), open each "to teach" concept with
one quick generative check (state it, apply it); a correct answer moves it to known. This is the
tutor's sweep, applied to a list derived from a document instead of a unit.

Publish the map in the artifact before teaching: the goal, the known concepts with their reminders,
and the concepts to teach in order. For a long document, hand the reading to a subagent and have
it return the concepts, the claims that rest on each, and the passages that use them.

## 2. Teach

**Broad pass first.** Before any concept check, publish the material in plain words: what it does
end to end in a few sentences, then each part's job (what it produces for the next part and what
breaks without it), with as little notation as possible. Place it relative to what the learner
already studies: the vault units and courses it draws on or extends, found while mapping the
concepts in section 1. Ask conceptual questions part by part:
why a piece is needed, which choice follows from which fact, what a claim cannot tell you. Teach
explicitly where the learner lacks the picture, and end every explicit block with a question that
still costs effort. A long or machine-written document needs this most, because its notation is
dense and its order is the author's, not the learner's.

**Then the narrow pass.** Teach the "to teach" concepts in prerequisite order, at the friction the
checks expose, down to the derivations the goal needs. Advance the cursor in the record as each
concept lands, and after each one say where it sits in the broad picture.

**End with a synthesis round**: the learner reconstructs the whole chain, answers one question
that spans several parts, and one that connects the material to a vault unit it relates to,
before the goal question below.

**Name a source for every explanation.** The tutor refuses to teach a unit whose reading is
missing, because confident, plausible, unfalsifiable content is the worst failure available. The
same risk applies here, so each concept's explanation cites where it comes from: the material
itself, a source in `courses/*/sources/`, the primary paper the material cites, or a standard
reference fetched for the purpose. A concept explained from general knowledge alone is marked
"unverified" in the artifact and is never carded.

**Separate background from claims.** Established background (what a B-tree is, what a
contrastive loss optimizes) is taught as fact. A finding of the material itself (a report's
conclusion, a recent paper's result) is taught as that source's claim, with its evidence and
how far it can be trusted. This matters most for autoresearch output, which can be wrong.

Close by returning to the goal: ask the learner, generatively, the question the session existed
to answer (what the report's main conclusion rests on, what the paper's contribution is, how
they would approach the task).

## 3. Sort what was taught

At "gtg", propose a destination for every concept taught, in the artifact, next to any flashcard
proposals. The learner gets one feedback turn, as in `skills/flashcards/SKILL.md` → "At gtg".

| the concept is | destination |
|---|---|
| needed only for this material or task | nowhere; the session record keeps the explanation |
| a fact worth keeping fresh, with no unit to hold it | flashcards only (tags below) |
| part of what an existing unit covers | a new concept on that unit, plus flashcards |
| taught in an earlier explain session too, with no unit to hold it | see "Promotion" |

**Adding a concept to an existing unit.** Follow `skills/knowledge-map/SKILL.md` for the concept's
`id`, `kind`, `claim` and `prereqs`, and insert it in sweep order. Set its state to `seen` only
if the unit has been placed (otherwise leave it `unknown`, and placement will judge it). Add one
or two bank questions for it through `skills/bank-generator/SKILL.md` and list them in its
`questions`. Append a unit `log` entry: the date, `what` = "explain session <slug> added <concept
id>", `failed` empty. Leave `srs` and `cursor` alone; the unit itself was not reviewed. A concept
belongs on a unit only when the unit's reading covers it; a concept that merely relates to a
course is flashcards-only.

**Flashcards** follow every rule in `skills/flashcards/SKILL.md` → "Writing a card", including the
blind check. Only verified concepts are carded. Tags and source lines depend on where the card
came from:

| card | tags | source line |
|---|---|---|
| on a concept that now lives in a unit | `vault::<course>::<unit-id>`, `vault::concept::<concept-id>` | the course and unit, as usual |
| background with no unit | `vault::topic::<topic>` | `Topic: <topic title>.` |
| a paper's claim | `vault::paper::<slug>`, per "Work papers" | the paper, per "Work papers" |
| a report's claim | `vault::report::<slug>`, with the topic tag when one applies | `Report: <report title>. (<YYYY-MM-DD>)` |

Cards with a unit go to that course's subdeck, paper claims to `Vault::Papers`, and topic and
report cards to `Vault::Ad hoc` (create it with the first such card; `scripts/anki_decks.py
--apply` does this and gives it the Vault preset). A report-claim card asks what the report claims, never states it as fact, like a paper card. Most
reports deserve no claim cards at all: card the background they taught, and card a claim only
when the learner will cite it.

## 4. Record

Write `sessions/<YYYY-MM-DD-HHMM>-explain-<slug>.md`, where the slug names the material in a few
kebab-case words. It opens with front matter, which `scripts/explain.py` reads and
`scripts/check_vault.py` validates:

```
---
kind: explain
title: Product quantization in the vector-search report
source_kind: report
source: https://raindrop.io/... (or a vault path, or the project need in one line)
topics: [product-quantization, inverted-file-index]
status: done
cursor: inverted-file-index (IVF probing next)
---
```

- `source_kind` is `paper`, `report`, `project` or `other`.
- `topics` lists every concept taught, as short kebab-case topic names. Run
  `python3 scripts/explain.py topics` first and **reuse an existing name** whenever it fits;
  promotion counts exact matches. Known concepts that only got a reminder are not topics.
- `status` is `open` while the goal question is unanswered and the learner may come back, `done`
  otherwise. An open record needs `cursor`: the concept reached and what comes next.

The body is the artifact converted to markdown: the goal, the concept map, the teaching with the
learner's answers verbatim, the sources named, and the sorting with what the learner accepted
(card note ids, concept ids, bank ids). Quote no more of an internal document than the
explanation needs; the material lives in Raindrop or on disk.

Then ship as in `skills/session/SKILL.md` → "gtg", with PR title `explain-<slug>: <what was
taught>`.

## Source-specific notes

**A paper, before the learner reads it.** Teach the prerequisites the paper assumes and the
problem it addresses, then publish a short reading guide: the paper's question, where its
contribution sits, and two or three questions to answer while reading. Do not teach the
contribution itself; the learner's own reading does that. Leave the record `open` with cursor
"debrief after reading".

**A paper, after the learner reads it.** Run a debrief: ask the questions a reading group would
(`skills/flashcards/SKILL.md` → "Ask what a reading group would ask") and have the learner answer
them. Teach where an answer fails. The debrief shows how well the learner holds the paper, so end
by suggesting a star rating, and if the learner agrees, continue straight into "Work papers"
steps 3 to 7 with the debrief as the reading.

**An autoresearch or litreview report.** Scope hard: these are dense, and most of their concepts
are not on the path to the conclusions the learner needs. Before teaching any finding, check
whether the report cites a source for it and say what that source is. A finding the learner will
rely on gets traced to the primary source during the session, and the artifact records whether
the source supports it.

**A project need.** Work backwards from the task to the smallest set of concepts it requires, and
use the project's own code, data or problem as the worked examples. The session is done when the
learner can say how they would do the task. Most project concepts sort to "nowhere" or
flashcards.

## Promotion

A topic deserves a home in `units.json` only once it comes back. `python3 scripts/explain.py
topics` lists each topic with the dates of the sessions that taught it and flags those taught
more than once. At "gtg", if a topic in this session is flagged and has no unit, propose a home
alongside the other destinations:

- **An existing unit** whose reading covers it: add the concept as above.
- **A new unit in an existing course**, when the topic belongs to the course and a source for it
  exists. Cut it with `skills/course/SKILL.md`.
- **A new unit in `courses/adhoc/`**, the catch-all for topics with no course. Create the course
  on first use: header `course: adhoc`, `title: Ad hoc topics`, `share: 0` (never drawn for
  study, so the other shares need no change), `default_priority: 5`, and `notes` saying units
  here come from explain sessions. Unit ids start with `adhoc-`, so the recent course mix
  counts their study sessions. Its units' questions are still quizzed like any other unit's.

A unit cut this way follows the normal unit rules. Its `reading` names a real source (a vault
file, or the primary reference the sessions cited); the explain records go in `also_read`. Cut
its concepts from what the sessions taught plus what the source covers. Place it with the taught
concepts `seen` and the rest `unseen`, then record one review with `python3 scripts/review.py
<course>:<unit-id> partial --seen <taught concept ids>`, so its questions start entering the quiz.
Then retag its `vault::topic::<topic>` cards with the unit and concept tags (`replaceTags`), and
run `python3 scripts/anki_decks.py --apply` to move them into the course's subdeck.

A unit in `courses/adhoc/` that grows into a subject of its own moves to a real course, through
`skills/course/SKILL.md`.

## The learn queue

This section needs the optional Raindrop integration. Material the learner wants to understand
later is tagged `learn` in Raindrop. Nothing surfaces the
queue on its own: the study session never mentions it, so it cannot become a debt. When the
learner asks what is in it, list the bookmarks with that tag, one line each, and let them pick.
When a session on one finishes with `status: done`, remove its `learn` tag.
