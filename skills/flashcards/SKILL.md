# Flashcards

Flashcards give fast front-and-back recall of atomic facts from sessions, reviewed in Anki on the learner's own schedule.
They are optional and light: the bank and the tutor carry the demanding retrieval, and the deck keeps facts warm between sessions.
The agent writes and manages every card; the learner only reviews, and approves proposals once per session.

## Plumbing

- **Anki desktop** with **AnkiConnect** (port 8765) and the **`anki` MCP server** (`@ankimcp/anki-mcp-server`, in `.mcp.json`). It works only from a Claude Code session on the machine where Anki runs, never from a cloud session. Setup: `skills/flashcards/SETUP.md`.
- **One deck tree, `Vault`, note types `Basic` and `Cloze`** (fields `Text`, `Back Extra`). No decks outside `Vault`, no reversed cards.
- **Subdecks by kind of card.** A card goes in exactly one subdeck; where it sits does not change its tags.

  | subdeck | holds |
  |---|---|
  | `Vault::Courses::<course title>` | cards from course sessions, named by the course `title` in `units.json` |
  | `Vault::Papers` | every claim attributed to a work paper |
  | `Vault::Ad hoc` | ad-hoc session cards with no unit (`skills/ad-hoc/SKILL.md`), created with its first card |

  A paper's claim (its front names the paper in a `ttl` span) goes to Papers even with a course tag on it.
  A plain-fact definition carded from a paper, or a card tagged with two courses, goes to the course of its concept tag.
  `python3 scripts/anki_decks.py` applies these rules to the whole deck and reports what is out of place; `--apply` moves it.
  A new kind of card that needs its own scheduling gets a new subdeck: add it to that script and this table.
- If the `anki` tools are missing or AnkiConnect does not answer, say so in one line and skip every flashcard step.

## Writing a card

These rules draw on Wozniak's "Twenty rules of formulating knowledge", Nielsen's "Augmenting Long-term Memory" and Matuschak's "How to write good prompts".

The bar: once the concept is understood, the card takes a few seconds and is usually right (**3 out of 5**).
A card that asks for a derivation step, an exact constant, or a condition the learner has to reason out is a 4; split it, or move it to the bank.

- **The front determines the back.** This rule comes before every other one. Someone who knows the field, given only the front, gives this back and no other correct answer. For every front, write down the strongest *other* correct answer and check that the front rules it out. When it does not, the front says which answer it wants:
  - **which definition**, when the object has several equivalent ones (rank as a dimension, as a pivot count, as the size of a largest nonzero minor): one card per definition, each naming its lens;
  - **which axis**, for every "how does X differ from Y" (substrate, planner, guarantee, granularity): one axis per card, and a similarity between the two is its own card;
  - **which claim**, for a paper: the aspect the claim is about, and what it is opposed to when the opposition is the point.

  Cut words from the back, never from the cue.
- **One fact per card.** A front that would take "and" to answer is two cards. Count and structure are separate facts ("how many products" and "which entries each product takes"), even when one formula answers both.
- **Understood first.** Card only what the learner can explain now. A card on an idea they never grasped goes to pending (see "Pending"), and the idea goes in the ad-hoc learn queue (`courses/adhoc/sources/`).
- **Worth knowing in a year.** Card a fact only if recalling it would save the learner time later, or it is striking. Skip trivia such as awards, or which systems descended from a paper.
- **Standalone.** New cards come up in random order, so every card is answerable on its own. Name the object; never "this theorem", "the above", "in the paper".
- **The field's own terms.** "the determinant of a square matrix", not "an n-by-n determinant".
- **Foundations first.** Define every nontrivial term a card uses on its own card, unless an existing card already does. Cover the family as well as the member (removable discontinuities, plus what a discontinuity is and the other types). Before carding a miss, card the plain definitions it rests on: a miss on Newton's method needs "what is Newton's method" before "why the Hessian must be positive definite".
- **Broad and narrow cards.** Narrow cards hold the definitions, formulas and steps. Broad cards hold each piece's role in the whole: what it is for, what it feeds into, and what breaks without it ("Why does the selection loop need a forecast of the information a call adds?" → "To price each option before buying it."). Every topic with narrow cards gets at least one broad card (see `skills/tutor/SKILL.md` → "Broad first, then narrow, then back to broad").
- **Recall only.** No options, no yes/no.

### Front

- **Source line first.** Every front opens with `<div class="src">…</div>` (styled on the note types, see `SETUP.md`), then `<br>`, then the question:
  - from a course: `<div class="src">Database Internals — Relational model: relations, schemas, keys.</div><br>…` (the course `title` and the unit `title`, not bold);
  - from a paper: `<div class="src"><b>ColBERT</b>: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. Khattab & Zaharia. (2020)</div><br>…` (the title; up to three author surnames, otherwise "Carlini et al."; the year). **Bold only the short title**, in place if the title contains it. If the paper is known by a name not in its title, put the name first: `<b>TracIn</b> · Estimating Training Data Influence by Tracing Gradient Descent. …`. With no short title, nothing is bold.
- **One question, at most one sentence after the source line.**
- **Name papers by their short title, not by their authors**: the paper's own name (BEIR), the full title when short, or a token phrase cut from it ("Debunking the Myth of Join Ordering"). Wrap it in `<span class="ttl">…</span>`, in contrasts too. Fall back to "Smith et al." for a long title with no name, or when the short title makes the sentence awkward ("George et al.'s mislabel detection framework", "Freitag et al. run TPC-H").
- **File a claim under the paper that makes it.** A finding BEIR reports about ColBERT is a BEIR card, with BEIR's source line and tag.
- **Bold the tested keyword** with `<b>…</b>` (**Quotient Law**, **one-sided limit**). When the thing tested is a formula, bold the word that tells it apart from its neighbours, such as **informally** against the ε-δ card.
- **No maths in the front unless the question needs it.** "When does the two-sided limit exist" needs no formula; "Why does the Quotient Law need \(\lim g\neq0\)" does.

### Back

- **Terse.** The answer is the shortest phrase that is still correct, usually under 15 words. Fragments are fine. Cut lead-ins ("It is", "Claims:"), restatements of the question, hedges and side-notes.
- **Two parallel items → `<ul><li>…</li></ul>`**, one fragment per item. Three or more go to cloze (below).
- **Diagrams for geometric ideas** (a tangent line, a squeeze between two curves): a small inline SVG under the answer, wrapped in `<div class="diagram">`, separated from the answer by `<br>`, at most about six labelled elements, `viewBox` set, width about 240px, strokes and text in `currentColor` for night mode, plain-text labels (MathJax does not render inside SVG).
- **No explanation prose.** The back holds the answer, plus a diagram where one helps, and nothing else.
- **Maths in MathJax**: `\(...\)` inline, `\[...\]` display. Never `$`.

### Cloze notes

Cloze notes follow every rule above. `Text` opens with the source line, then `<br>`, then the sentence; no deletion contains `::` or `}}`; `Back Extra` stays empty unless it holds a diagram.
Anki makes one card per deletion number, and deletions that share a number hide together.

- **Lists of three or more** are always cloze. Never ask for an unprompted list of three or more. One sentence names the list and its size: `<span class="ttl">BEIR</span> varies along four <b>dimensions</b>: {{c1::task}}, {{c2::domain}}, {{c3::corpus size}} and {{c4::query and document length}}.` Delete every item for course material and `***`/`****` papers, and only the least obvious one for `*`/`**` papers. Scope the stem so the list is complete ("C-Store's three storage novelties"), and keep visible any cue word the hidden item needs.
- **Short deletions.** A deletion hides a few words, never a clause or a chain of reasons. Split a causal chain into one card per link.
- **Cue each list item** when the stem alone does not narrow it, with its category in parentheses: `rejects two explanations for the tree–NN gap: (data) {{c1::categorical features}}; (training) {{c2::insufficient hyperparameter tuning}}`.
- **Long items go in a lettered list** (`<ol type="a">`), one item per line, with a name and its meaning as separate deletions: `<li>{{c1::Reservation}}: {{c2::slots held for tokens not yet generated}}.</li>`.
- **Contrasts whose answer names both sides** are always cloze, one deletion per side: `Whereas <span class="ttl">LOTUS</span> runs semantic operators on {{c1::pandas dataframes}}, <span class="ttl">Cortex AISQL</span> runs them in {{c2::a distributed SQL engine}}.` A contrast that asks for one side only ("What does ThalamusDB guarantee, unlike SUPG's precision targets?") stays Basic.
- **Closely related questions** that each need the others as context go in one short paragraph with a deletion per question, so the context is written once: "The <b>Leibniz formula</b> expresses the determinant as a sum over permutations. There are {{c1::\(n!\)}} terms because there are that many {{c1::permutations of the columns}} … Formally, \(\det A=\){{c2::\(\sum_{\sigma\in S_n}\operatorname{sign}(\sigma)\prod_i a_{i\,\sigma(i)}\)}}." Any term the paragraph uses but does not define gets its own card.
- **A single fact** may be cloze when stating the setting as a sentence is clearer than a Basic front, and a shared number lets a fact and its reason be one card, but only when both are short and so tightly linked that testing one alone would give away the other: "To find the limit \(L\) of a convergent recursive sequence \(a_{n+1}=f(a_n)\), we use the identity {{c1::\(L=f(L)\)}}, which holds since {{c1::if \(a_n=L\) then \(a_{n+1}=L\) also}}." Don't cloze a sentence whose wording gives the answer away, or one memorable only as a phrase.

### Examples

Reference cards. Match this length and tone:

| Front | Back |
|---|---|
| What does \(\lim_{x\to a}f(x)=L\) mean <b>informally</b>? | \(f(x)\) can be made arbitrarily close to \(L\) as \(x\) gets close enough to \(a\). |
| Why does the <b>Quotient Law</b> for limits need \(\lim_{x\to a}g(x)\neq0\)? | The denominator would be zero. |

Fronts that failed in review:

| Bad front | Why | Good front(s) |
|---|---|---|
| What is the rank of a matrix? | Many equivalent definitions | What is the <b>rank</b> of a matrix in terms of its column space? |
| How does Palimpzest's quality estimate differ from LOTUS' accuracy guarantees? | Three facts, no axis | What <b>reference</b> do Palimpzest and LOTUS both judge quality against? · Cloze: Whereas Palimpzest judges quality per {{c1::whole plan}}, LOTUS judges it per {{c2::operator}}. · Cloze: Whereas Palimpzest gives a {{c1::point estimate}} of quality, LOTUS gives {{c2::an ε-δ guarantee}}. |

### What qualifies

- **Yes:** definitions; theorem statements; what one part of a definition or theorem is for; simple applications; steps of a routine computation; the key claim of a seminal paper or textbook section; why a paper or algorithm mattered in its field; and **every miss, distilled**: the idea that was missing, not the question that exposed it.
- **No:** anything the learner would have to derive at length; anything an existing card covers (search first), unless it is a foundational concept with naturally different phrasings or interpretations, which rarely holds for a paper card; unit material the learner has not been taught yet.

**Tags.** Every card needs both:

- `vault::<course>::<unit-id>`: the unit the card came from.
- `vault::concept::<concept-id>`: the concept it serves, so a struggling card finds its way back into the vault.

Paper cards add `vault::paper::<slug>` (see "Work papers").
Ad-hoc cards with no unit use `vault::topic::` and `vault::report::` tags (see `skills/ad-hoc/SKILL.md` → "Sort what was taught").

## At "gtg": propose, then add

Run this after capture, before shipping (see `skills/session/SKILL.md` → "gtg").

1. **Draft** cards from this session: concepts taught or marked `seen`, quiz misses, claims from the reading. Aim for about 3–8, so the daily cap of 100 reviews (about 12 minutes) holds.
2. **Search** the deck (`findNotes`, e.g. `deck:Vault tag:vault::concept::<id>`) and drop duplicates.
3. **Blind check.** Hand the fronts only (source line included) to a fresh subagent and have it answer each in a few words; the drafter cannot do this, because it knows which answer it meant. A card fails when the answer is correct but is not the back, or needs "and". Rewrite every failure under "The front determines the back" and check it again.
4. **Publish the proposals in the session artifact** as a numbered list, front and back rendered.
5. **Wait for one feedback turn.** The learner keeps, drops or edits by number; anything unmentioned is accepted. No second round unless they ask.
6. **Add** the accepted cards (`addNotes`, subdeck per "Plumbing", model `Basic` or `Cloze`, both tags), then **sync**.
7. Record the count and the note ids in the session's `log` sentence and the session file.

## Work papers

Papers the learner reads for work, outside any course, go into `Vault::Papers` under the same rules and daily cap.

**Only important papers are carded, and the learner picks them** by giving each a star rating from `*` to `****`, which sets the card budget even when it is only one or two cards:

| Stars | Cards | What they cover |
|---|---|---|
| `*` | 1–2 | the main claim, nothing else |
| `**` | 2–4 | main claim, plus the core idea of the method or the key result |
| `***` | 3–6 | the above, plus the paper's own terms and a definition card for an established term the deck lacks |
| `****` | 5–10 | a deep dive: the novel contribution, the key design and experimental choices and why, the arguments against alternatives, the core idea of the method, and contrasts with other papers the learner has carded or keeps in the vault |

**Every card asks what the paper claims, never states it as a general fact**, because most of these papers are recent and contested.
Write "How does LOTUS's optimizer choose the **threshold** for …?", never "Why are semantic operators cheaper than …?".
The attribution is not the cue: "What do X claim about <topic>?" always has several right answers, so name the aspect of the topic.
The only exception is a definition of an established term the paper relies on (BM25, HNSW), written as a plain fact; these appear only at `***` and up and count toward the budget.

**Ask what a reading group would ask.**
Card the answers to what researchers in a reading group would ask about the paper:

- **The novel contribution.** What is new, and what problem it newly poses or solves.
- **Key choices and why.** The problem formulation, design or assumption, the alternative it rejects, and why these datasets or tasks.
- **Experimental design, not numbers.** Which research questions the experiments answer, with which tasks, datasets and metrics, and the main finding qualitatively. Never "what speedup / accuracy did X report".
- **The argument.** What the paper argues against, and how it supports that.
- **Contrasts with other papers the learner has carded or keeps in the vault.** Same problem with a different approach, or same approach with a different assumption. Name both papers and the axis in the front. These are among the most valuable cards.

Never card rote system facts (adopted strategies, component names, configuration, feature lists) unless they are the contribution or a deliberate argued choice.
**Meta cards are welcome** when the facts come from the paper's own text or are widely known: its impact, what it superseded, or the main critique it drew.

**Trigger:** "card this paper", "I read <title>", "which papers should I card", or anything like it.
It runs as an ad-hoc session that only cards the paper: no quiz, no study unit, no change to `units.json`.

1. **Pick the papers.** If the learner named a paper, find it from the file they name (typically in `courses/adhoc/sources/`) or the URL they give, and ask for its stars in one line. Otherwise, survey: list the papers in `courses/adhoc/sources/` that have no paper record yet (`sessions/<date>-paper-<slug>.md`). Group them by topic (one subagent per cluster when there are many) and list the important ones (seminal, highly cited, area-defining surveys, recent additions central to the learner's work), numbered, with a one-line claim each. Wait for the learner's reply of `#` plus stars.
2. **Read it.** Read the learner's own notes on the paper first, if any, then the full text; for a long paper, have a subagent return claims, definitions and highlights only.
3. **Draft** as many cards as the stars allow, every one framed as the paper's claim, with the learner's noted claims first. At `***` and up, foundations come first (search `deck:Vault` for each established term). Card only what the paper says, and keep out internal numbers or names the learner would not want on a phone.
4. **Propose, wait for one feedback turn, add**, as in steps 3–6 of "At gtg" (blind check included). Tags:
   - `vault::paper::<slug>` on every paper card, where the slug is first author, year and a keyword, such as `vaswani-2017-attention`.
   - When a card overlaps a course unit, also **both** course tags, `vault::<course>::<unit-id>` and `vault::concept::<concept-id>`, as a BM25 card from a ranking paper would. Check `units.json` for every paper, since course units are often built on papers. Leave both off when no concept matches, and do not invent concepts. The source line still names the paper.
   - Before adding a card with a concept tag, check that the concept is `seen` (see "Pending" below).
5. **Record** `sessions/<YYYY-MM-DD-HHMM>-paper-<slug>.md`: the title, authors and year, the file path or URL, and the cards as a table with their note ids. This record marks the paper as carded. Never store a PDF or quote beyond the cards; papers may be internal or copyrighted. Then do "gtg" as usual. The PR title is `paper-<slug>: <n> cards`, and there is no `units.json` log entry.

## Leeches → the quiz

A card the learner keeps missing needs teaching rather than more repetitions.
Anki's leech setting (`SETUP.md`) tags it `leech` and suspends it.

**At session opening**, run `findNotes` with `deck:Vault tag:leech is:suspended`. For each hit:

- With a `vault::concept::` tag, add **one** item for that concept to this session's quiz, on top of the normal draw: a bank question on the concept if one is askable, otherwise the card's own front, asked generatively in the artifact. Grade and route it like any quiz miss (`skills/grader/SKILL.md`).
- With only a `vault::paper::`, `vault::topic::` or `vault::report::` tag, re-teach it in the artifact from the paper, or from the ad-hoc session record and its source, then ask the card's front generatively. A topic card that keeps returning as a leech suggests the topic needs a unit (`skills/ad-hoc/SKILL.md` → "Promotion").
- Then fix the card: rewrite (`updateNoteFields`) or split it if the miss came from its wording. Either way, remove the `leech` tag and unsuspend it.
- Any other leech with no routing tag goes in the next cleanup batch.

No more than three leeches per session; the rest wait.

## Cards the learner flags in review

The learner flags cards in Anki while reviewing, and each flag asks for something different:

- **Marked** (Anki's `marked` tag, Ctrl+K): the card needs a rewrite, or a clarification when tagged `clarify`. Take them one at a time in the artifact: show the card, ask what is wrong unless the tag says, then explain or rewrite (`updateNoteFields`, same note id, keeping review history). Remove `marked` and `clarify` once the learner is satisfied.
- **Suspended without a `leech` tag**: the learner judged the card useless. Don't revive or rewrite it. Add its kind to "Cards the learner rejected" below, and tag the note `rejected`.
- **Pending**: a card whose `vault::concept::` concept is `unseen` or `unknown` is suspended and tagged `pending`, not rewritten. The learner can also send a card to pending when it needs background they lack. A pending card with no concept tag has nothing to trigger its return, so list it at each cleanup for the learner to revive or drop.

**At session opening**, alongside the leech query, run `findNotes` with `deck:Vault tag:marked`, `deck:Vault is:suspended -tag:leech -tag:rejected -tag:pending`, and `deck:Vault tag:pending`.
Unsuspend each pending card whose concept is now `seen` and remove `pending`.
Mention the counts in one line; work through them when the learner asks.

### Cards the learner rejected

These are kinds of card the learner suspended as useless. Never write them.

- **Named baselines.** Card a baseline only when the choice of comparison is itself the argument.
- **How a survey was assembled.** Card what a survey concludes.
- **Claims that follow from the premise** ("What cost does Cortex AISQL's planner plan around?" → "LLM inference cost"). Card what the premise does not predict.
- **Trivia about a paper's legacy** (Codd's Turing Award, the systems that descended from the relational model).
- **What earlier work could not do** ("What does Abacus optimize that earlier optimizers could not?"). It has several right answers and rests on a contested history; card what the system does.
- **A paper's headline win on its own benchmark** ("TracIn surfaces mislabels earliest"). Card what an evaluation was designed to show only when the design itself is the contribution.

## Pre-review of unseen cards

A pre-review pass checks never-reviewed cards in bulk for what the learner would mark or suspend.
Run it when the learner asks, or after a large batch.

1. Dump the `deck:Vault is:new -is:suspended` notes, excluding today's cards, grouped by paper tag or unit tag, with each concept's state from `units.json`, into `all.json` in a scratch directory. Split the groups into chunks of about 90 notes.
2. Hand each chunk to a subagent with `skills/flashcards/PREREVIEW.md` as its brief. Each writes `actions<i>.json`: reject, rewrite, or merge, never touching Anki. Check that every reviewer covered every group in its chunk.
3. Run `python3 scripts/anki_prereview_apply.py <dir> --dry`, then without `--dry`, then `python3 scripts/anki_decks.py --apply` and sync. Save `applied.json` as `sessions/<date>-anki-prereview.json`.

Keep a card on unstudied material only if a reader with the learner's background can understand it from its front and back.
Update `PREREVIEW.md` with each new lesson from the learner's flags.

## Cleanup

Cleanup is due when `flashcards.json` → `last_cleanup` is null or more than 30 days old.
It runs inside the same "gtg" feedback turn as the proposals.

Candidates, each with a one-line reason:

- duplicates or near-duplicates;
- cards that break the rules above;
- cards whose unit was archived or whose concept no longer exists;
- leeches with no concept, `vault::paper::`, `vault::topic::`, or `vault::report::` tag;
- `vault::topic::` cards whose topic now has a unit (retag them with the unit and concept tags);
- cards in the wrong subdeck, as reported by `python3 scripts/anki_decks.py`.

**Never delete, edit or retag without the learner's yes.**
Apply what they approve, then set `last_cleanup` to today.
