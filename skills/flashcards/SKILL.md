# Flashcards

Fast, easy, front–back recall of atomic facts from sessions, reviewed in Anki on the learner's own
schedule. This layer is optional: everything else in the vault works without Anki. This is the light layer under the vault: the bank and the tutor carry the demanding
retrieval, the deck keeps the facts warm between sessions that are a few days apart.

The agent writes and manages every card. The learner only reviews, and approves proposals once
per session.

## Plumbing

- **Anki desktop** with the **AnkiConnect** add-on (port 8765). Phone review, if wanted, goes
  through AnkiWeb sync (AnkiDroid, AnkiMobile or AnkiWeb in a browser).
- **`anki` MCP server** (`@ankimcp/anki-mcp-server`), declared in `.mcp.json`. It reaches Anki only
  from a Claude Code session on the machine where Anki desktop runs (including WSL on that
  machine), never from a cloud session. Setup: `skills/flashcards/SETUP.md`.
- **One deck tree, `Vault`, note types `Basic` and `Cloze`.** `Cloze` (fields `Text`, `Back Extra`) is
  for lists, two-sided contrasts, and facts a sentence makes clearer (see "Writing a card"). No
  decks outside `Vault`, no reversed cards.
- **Subdecks by kind of card**, so each kind can get its own deck options. A card goes in exactly
  one; its tags are unchanged by where it sits.

  | subdeck | holds |
  |---|---|
  | `Vault::Courses::<course title>` | cards from course sessions, named by the course `title` in `units.json` |
  | `Vault::Papers` | every claim attributed to a work paper |
  | `Vault::Ad hoc` | ad-hoc session cards with no unit (`skills/ad-hoc/SKILL.md`), created with its first card |

  For a card that fits two, judge which kind it is. A paper's claim (its front names the paper
  in a `ttl` span) goes to Papers even with a course tag on it. A plain-fact definition carded
  from a paper goes to the course whose concept it is tagged with. A card tagged with two
  courses goes to the course of its concept tag. `python3 scripts/anki_decks.py` applies these
  rules to the whole deck and reports what is out of place; `--apply` moves it. A new kind of
  card that wants its own scheduling gets a new subdeck: add it to that script and this table.
- **`raindrop` MCP server** (Raindrop.io's official one, HTTP + OAuth), declared in `.mcp.json`.
  It is optional, for learners who keep the papers they read outside the vault in Raindrop.io.
  Only "Work papers" below uses it.
- If the `anki` tools are missing or AnkiConnect does not answer, say so in one line and skip every
  flashcard step. Nothing else in the session depends on them.

## Writing a card

The bar: once the concept is understood, the card takes a few seconds and is usually right.
Difficulty belongs to the bank, not here. **Aim for 3 out of 5.** A card that asks for a
derivation step, an exact constant, or a condition the learner has to reason out is a 4; split it,
or move it to the bank.

- **The front determines the back.** This rule comes before every other one. Someone who knows
  the field, given only the front, gives this back and no other correct answer. For every front,
  write down the strongest *other* correct answer and check that the front rules it out. When
  it does not, the front says which answer it wants:
  - **which definition**, when the object has several equivalent ones (rank as a dimension, as a
    pivot count, as the size of a largest nonzero minor): one card per definition, each naming
    its lens;
  - **which axis**, for every "how does X differ from Y" (substrate, planner, guarantee,
    granularity);
  - **which claim**, for a paper: the aspect the claim is about, and what it is opposed to when
    the opposition is the point.

  Terseness never comes at the price of this. Cut words from the back, not from the cue.
- **Contrasts: one axis per card, named in the front.** Never "How does Cortex AISQL differ
  from LOTUS?". A similarity between the two is its own card. A contrast whose answer names
  both sides asks for two things, so write it as a **cloze note with two deletions**, one per
  side: `Whereas <span class="ttl">LOTUS</span> runs semantic operators on {{c1::pandas
  dataframes}}, <span class="ttl">Cortex AISQL</span> runs them in {{c2::a distributed SQL
  engine}}.` Each card shows one side and asks for the other. A contrast that asks for one
  side only ("What does ThalamusDB guarantee, unlike SUPG's precision targets?") stays Basic.
- **Count and structure are separate facts.** "How many products" and "which entries each
  product takes" are two cards (two deletions of one cloze note, see below), even when one
  formula answers both.
- **Lists of three or more → a cloze note.** One sentence names the list and its size, with
  each item as a deletion: `<span class="ttl">BEIR</span> varies along four
  <b>dimensions</b>: {{c1::task}}, {{c2::domain}}, {{c3::corpus size}} and {{c4::query and
  document length}}.` Anki makes one card per deletion, and each hides one item while showing
  the rest. Delete every item for course material and `***`/`****` papers, and only the least
  obvious one for `*`/`**` papers. Scope the stem so the list is complete ("C-Store's three
  storage novelties"), and keep visible any cue word that the hidden item needs. A bare list on
  the back is fine only for two items. Never ask a learner to produce an unprompted list of
  three or more.
- **The field's own terms.** "the determinant of a square matrix", not "an n-by-n
  determinant". The front names objects as a textbook in the field would.

- **Foundations before misses.** A miss usually means the definition under it is shaky, not
  only the point that was asked. Before carding a miss, card the plain definitions it rests on:
  what the object is, and why it is defined that way when the reason is short. A miss on Newton's
  method needs "what is Newton's method" before "why the Hessian must be positive definite".
- **Broad and narrow cards, for the same material.** Narrow cards hold the definitions, formulas
  and steps. Broad cards hold each piece's role in the whole: what it is for, what it feeds into,
  and what breaks without it ("Why does the selection loop need a forecast of the information a
  call adds?" → "To price each option before buying it."). A session's batch carries both, and
  every topic with narrow cards gets at least one broad card that places it. A deck of narrow
  cards alone keeps facts warm that the learner can no longer place, which is the failure
  `skills/tutor/SKILL.md` → "Broad first, then narrow, then back to broad" exists to prevent.
- **Define every nontrivial term a card uses**, on its own card, unless an existing card already
  defines it. Cover the family as well as the member: a card on removable discontinuities comes
  with cards on what a discontinuity is and on the other types.
- **Order matters.** Anki introduces new cards in the order they were added, so add definition
  cards before the cards that use them.
- **Source line first.** Every front opens with a small, faded source line in
  `<div class="src">…</div>` (styled on the `Basic` note type, see `SETUP.md`), then `<br>` for
  one empty line, then the question:
  - from a course: `<div class="src">Database Internals — Relational model: relations, schemas, keys.</div><br>…`
    (the course `title` and the unit `title` from `units.json`, not bold);
  - from a paper: `<div class="src"><b>ColBERT</b>: Efficient and Effective Passage Search via Contextualized Late Interaction over BERT. Khattab & Zaharia. (2020)</div><br>…`
    (the paper's title; up to three author surnames, otherwise "Carlini et al."; the year).
    **Bold only the short title**, where the paper has one. If the title contains the name, bold it
    in place (`<b>ColBERT</b>: …`, `… in <b>LOTUS</b>.`). If the paper is known by a name that is not
    in its title, put the name first: `<b>TracIn</b> · Estimating Training Data Influence by Tracing Gradient Descent. …`.
    If it has no short title, nothing is bold.
- **Name papers by their title in the question, not by their authors.** Use the short title a
  researcher would recognise over time: the paper's own name (PagedAttention, SemBench,
  Cortex AISQL, TracIn, BEIR), the full title when it is short or natural ("Random Sampling
  over Joins Revisited"), or a token phrase cut from it ("Access Paths for Ordering with
  LLMs", "Debunking the Myth of Join Ordering"). Wrap it in `<span class="ttl">…</span>`
  (styled on both note types, see `SETUP.md`), so a paper reads differently from a term:
  "What does <span class="ttl">BEIR</span> find about …", "<span class="ttl">LOTUS</span>'s
  optimizer …". This goes for other papers named in the front too, as in contrasts. Fall back
  to "Smith et al." only for a paper with a long title and no name. The source line bolds the
  same short title.
- **Front: one question, at most one sentence after the source line. Back: one answer**, plus
  an optional diagram, then the easy explanation.
- **Easy explanation under the answer.** After the answer (and its diagram, if any), leave one
  empty line and add `<div class="expl">…</div>`: 1–3 short sentences (about 20–50
  words) that make the answer click. Give the intuition, why it is true or why it matters, a
  tiny example or an everyday analogy, in plain words. Don't reword the answer. On paper cards,
  keep the attribution and add no claims beyond the card and widely known facts. The empty line
  is `<br><br>` after a plain-text answer, `<br>` after a diagram's `</div>`, and nothing after
  a `</ul>` (the list's own margin leaves it). Full back:
  `First formalism with … parameters.<br><br><div class="expl">Before LOTUS, "ask an LLM about each row" had no …</div>`.
- **Terse.** The answer (the back before its explanation) is the shortest phrase that is still correct, usually under 15 words.
  Fragments are fine. Cut lead-ins ("Exactly when", "Otherwise", "It is", "Claims:",
  "Proposes:"), anything that restates the question, hedges, and parenthetical side-notes. Use
  symbols where they read faster than words. The front carries the framing, so the answer is
  only the answer.
- **Two items → a list.** When the answer is two parallel items, write the back as
  `<ul><li>…</li></ul>`, one fragment per item, not as a sentence joined with commas and
  semicolons. Three or more go leave-one-out (above).
- **No maths in the front unless the question needs it.** "When does the two-sided limit exist"
  needs no formula; "Why does the Quotient Law need \(\lim g\neq0\)" does.
- **Bold the tested keyword** in the front, the term the card is really about, with `<b>…</b>`
  (for example **Quotient Law** or **one-sided limit**). When the thing tested is a formula
  rather than a term, bold the word that tells it apart from its neighbours, such as
  **informally** against the ε-δ card.

  Reference cards. Match this length and tone:

  | Front | Back |
  |---|---|
  | What does \(\lim_{x\to a}f(x)=L\) mean <b>informally</b>? | \(f(x)\) can be made arbitrarily close to \(L\) as \(x\) gets close enough to \(a\). |
  | When does the <b>two-sided limit</b> exist in terms of one-sided limits? | Both one-sided limits exist and are equal. |
  | What do the <b>limit laws</b> say? | The limit of \(+,\ -,\ \times c,\ \times,\ \div,\ {}^{n}\) is that of the individual limits (if they exist). |
  | Why does the <b>Quotient Law</b> for limits need \(\lim_{x\to a}g(x)\neq0\)? | The denominator would be zero. |

  Fronts that fail in review, and what they should have been. Each bad front has several
  correct answers:

  | Bad front | Why | Good front(s) |
  |---|---|---|
  | What is the rank of a matrix? | Many equivalent definitions | What is the <b>rank</b> of a matrix in terms of its column space? |
  | How does Cortex AISQL's setting differ from LOTUS? | No axis; two facts | Cloze, one per axis: Whereas LOTUS runs semantic operators on {{c1::pandas dataframes}}, Cortex AISQL runs them in {{c2::a distributed SQL engine}}. · the same for the <b>query planner</b> |
  | What do Maharana et al. claim about LLMs on very long conversations? | Many claims, by many authors | What kind of <b>reasoning</b> does LoCoMo find LLMs struggle with in very long conversations, beyond recalling isolated facts? |
  | Which products appear in the big formula for an n-by-n determinant? | Two facts; wrong term | How many products are in the <b>Leibniz formula</b> for the determinant of a square matrix? · Which entries does each product in the <b>Leibniz formula</b> take? |
  | How do Thakur et al. make BEIR heterogeneous? | Unprompted list of four | Cloze: BEIR varies along four <b>dimensions</b>: {{c1::task}}, {{c2::domain}}, {{c3::corpus size}} and {{c4::query and document length}}. |
  | How does Palimpzest's quality estimate differ from LOTUS' accuracy guarantees? | Three facts, no axis | What <b>reference</b> do Palimpzest and LOTUS both judge quality against? · Cloze: Whereas Palimpzest judges quality per {{c1::whole plan}}, LOTUS judges it per {{c2::operator}}. · Cloze: Whereas Palimpzest gives a {{c1::point estimate}} of quality, LOTUS gives {{c2::an ε-δ guarantee}}. |
- **Diagrams for geometric ideas.** When the fact is a shape, a picture, or a direction (a
  tangent line, a volume element, a row picture of planes, a squeeze between two curves), put a
  small inline SVG under the back's sentence. Keep it simple: no more than about six labelled
  elements, `viewBox` set, width about 240px, strokes and text in `currentColor` so it reads in
  Anki's night mode, plain-text labels (MathJax does not render inside SVG).
- **Standalone.** Name the object; never "this theorem", "the above", "in the paper". Someone who
  knows the field but not today's session must be able to read it.
- **Recall only.** No options, no yes/no.
- **Cloze when the sentence makes the card clearer.** Lists and two-sided contrasts are always
  cloze. A single fact may also be a cloze when stating the setting as a sentence makes the
  question clearer than a Basic front would: "To find the limit \(L\) of a convergent
  recursive sequence \(a_{n+1}=f(a_n)\), we use the identity {{c1::\(L=f(L)\)}}, which holds
  since {{c1::if \(a_n=L\) then \(a_{n+1}=L\) also}}." Deletions that share a number hide
  together, so a fact and its reason can be asked as one card. Don't cloze a sentence whose
  wording gives the answer away, or one memorable only as a phrase.
- **Closely related questions → one cloze note with several deletions.** When a few questions
  each need the others as context (what the Ratio Test is for, the limit it computes, what that
  limit decides), write one short paragraph with a deletion per question instead of separate
  Basic cards that each repeat the setup. Each deletion number is still its own card, so this
  keeps "one fact per card" while the paragraph carries the context once. Example: "The
  <b>Leibniz formula</b> expresses the determinant as a sum over permutations. There are
  {{c1::\(n!\)}} terms because there are that many {{c1::permutations of the columns}} …
  Formally, \(\det A=\){{c2::\(\sum_{\sigma\in S_n}\operatorname{sign}(\sigma)\prod_i a_{i\,\sigma(i)}\)}}."
  Any term the paragraph uses but does not define (here, the sign of a permutation) gets its
  own card.
- **Cloze notes** follow the same rules as Basic. `Text` opens with the source line, then
  `<br>`, then the sentence; no deletion contains `::` or `}}`; `Back Extra` holds the
  `<div class="expl">`.
- **One fact per card.** Two facts → two cards, related or not. A front that would take "and"
  to answer is two cards.
- **Maths in MathJax**: `\(...\)` inline, `\[...\]` display. Never `$`.
- **What qualifies:** definitions; theorem statements; what one part of a definition or theorem is
  for (why the hypothesis is there, what breaks without it); simple applications; steps of a
  routine computation; the key claim of a seminal paper or textbook section; why a paper or
  algorithm mattered in its field; and **every miss, distilled** — the idea that was missing, not
  the question that exposed it.
- **What does not:** anything the learner would have to derive at length; anything already
  covered by an existing card (search first); unit material the learner has not been taught yet.

**Tags**, both required (paper cards add a paper tag, see "Work papers"; ad-hoc sessions use
`vault::topic::` and `vault::report::` tags for cards with no unit, see
`skills/ad-hoc/SKILL.md` → "Sort what was taught"):
- `vault::<course>::<unit-id>` — the unit the card came from.
- `vault::concept::<concept-id>` — the concept in `units.json` it serves. This is how a struggling
  card finds its way back into the vault.

## At "gtg": propose, then add

After capture, before shipping (see `skills/session/SKILL.md` → "gtg"):

1. **Draft** cards from this session: concepts taught or marked `seen`, quiz misses, claims from
   the reading. Aim for about 3–8. The daily cap is about 12 minutes (100 reviews), which holds only if each
   session adds a handful.
2. **Search** the deck (`findNotes`, e.g. `deck:Vault tag:vault::concept::<id>`) and drop
   anything that duplicates an existing card.
3. **Blind check.** Hand the fronts only (source line included, backs withheld) to a fresh
   subagent and have it answer each in a few words. A card fails when the answer is correct but
   is not the back, or when the answer needs "and". Rewrite every failure under "The front
   determines the back" and check it again. The drafter cannot do this check itself: it already
   knows which answer it meant.
4. **Publish the proposals in the session artifact** as a numbered list, front and back rendered.
   Chat says only that they are up.
5. **Wait for one feedback turn.** The learner keeps, drops or edits by number. Apply that
   feedback exactly; anything they did not mention is accepted. Do not start a second round unless
   they ask for one.
6. **Add** the accepted cards (`addNotes`, deck per the subdeck table in "Plumbing", model `Basic` or `Cloze`, both tags), then **sync** so
   they reach the phone.
7. Record the count and the note ids in the session's `log` sentence and the session file.

## Work papers

Papers the learner reads for work, outside any course, go into `Vault::Papers`, under the
same writing rules and the same daily cap. They are reviewed with everything else; nothing about
the review side changes. Only run this from a session on the machine where Anki runs.

**Only important papers are carded, and the learner picks them.** Most of the library (videos,
AI transcripts, papers skimmed once) never becomes cards. The learner marks each paper to card
with stars, and the stars set the card budget:

| Stars | Cards | What they cover |
|---|---|---|
| `*` | 1–2 | the main claim, nothing else |
| `**` | 2–4 | main claim, plus the core idea of the method or the key result |
| `***` | 3–6 | the above, plus the paper's own terms and a definition card for an established term the deck lacks |
| `****` | 5–10 | a deep dive: the novel contribution, the key design and experimental choices and why, the arguments against alternatives, the core idea of the method, and contrasts with related papers in the library |

Keep `*` and `**` papers to their few cards. Spend depth only on `****` papers, where the
learner wants to understand the paper, not just recognise its claim.

**Every card asks what the paper claims, never states it as a general fact.** Most of these
papers are recent and contested, so the front keeps the attribution: "What does Sampling over
Union of Joins claim about the **variance** of …?", "How does LOTUS's optimizer choose the
**threshold** for …?", "What kind of reasoning does LoCoMo find LLMs **struggle with** …?". Never "Why are
semantic operators cheaper than …?". The attribution is not the cue: "What do X claim about
<topic>?" alone always has several right answers, so name the aspect of the topic the claim is
about. This applies to results, mechanisms and the paper's own terms. The back is the answer alone, with no "Claims:" prefix. The only exception is a
definition of an established term the paper relies on (BM25, HNSW), which is not the paper's
claim and is written as a plain fact. Those appear only at `***` and up, and they count toward
the budget.

**Ask what a reading group would ask.** Before drafting, the drafter imagines the discussion
of the paper in a research reading group and cards the answers to what researchers there would
ask:
- **The novel contribution.** What is new here that earlier work did not do? What problem does
  it newly pose or solve?
- **Key choices and why.** Why this problem formulation, this design or this assumption, and
  what alternative it rejects. Why these baselines, datasets or tasks.
- **Experimental design, not experimental numbers.** Which research questions the experiments
  answer, which tasks, datasets and metrics they use, and what the main finding is
  qualitatively. Not which named systems serve as baselines (see "Cards the learner rejected"). Never "what speedup / accuracy / percentage did X report"; the numbers are not
  worth remembering.
- **The argument.** What the paper argues against, and how it supports that.
- **Contrasts with related papers in the learner's Raindrop library.** How the paper differs
  from a similar paper the learner also saved: same problem, different approach, or same
  approach, different assumption. Name both papers and the axis in the front, one axis per
  card. These are among the most valuable cards, because they place the paper in the learner's
  map of the field.

Never card rote system facts: which strategies an implementation adopted and which it did not,
component names, configuration details, or lists of features. If a design detail is not the
contribution or a deliberate argued choice, leave it out.

**Meta cards are welcome** when the drafter is confident of the facts: the paper's impact
(what it started, what it is the standard baseline for), what it superseded, or the main
critique it drew. Base them on the paper's own text or on widely known facts, never on guesses.

**Trigger:** "card this paper", "I read <title>", "which papers should I card", or anything like
it. It runs as an ad-hoc session that only cards the paper: there is no quiz and no study unit, and nothing in
`units.json` changes.

1. **Pick the papers.** If the learner named a paper, search Raindrop for it and ask for its
   stars in one line. Otherwise, survey: group the library's papers by topic (tags first, with
   one subagent per cluster when the library is large), keep the topics close to the learner's
   work, and list the papers in them that look important, aiming broadly (seminal, highly
   cited, area-defining surveys, and recent saves central to their research). Number the
   list, give a one-line claim for each paper, skip anything already tagged `anki`, and wait for
   the learner's reply of `#` plus stars. Never ask the learner for a PDF or a link that Raindrop
   already has.
2. **Read it.** Read the bookmark's note and highlights first: they mark what mattered to the
   learner, and the cards should cover them. Then read the full text (Raindrop's full-text
   fetch, or the bookmark's URL when it is public). For a long paper, hand the reading to a
   subagent and have it return claims, definitions and highlights only.
3. **Draft** as many cards as the stars allow (table above), every one framed as the paper's
   claim. Every rule in "Writing a card" applies. At `***` and up, foundations come first: the
   established terms the claim rests on get definition cards unless the deck already has them
   (search `deck:Vault` for the term). Highlights that state a claim take priority within the
   budget. **Standalone** matters more than usual here: the source line names the paper, and
   the question names the paper by its short title in a `ttl` span, or the method or system,
   never "the paper" or "the authors". Card only what the paper says. Internal numbers or names the learner would not want on a phone stay out.
4. **Propose, wait for one feedback turn, add.** This is the same as steps 3–6 of "At gtg" (blind check included), in
   this session's artifact. Tags:
   - `vault::paper::<slug>`, where the slug is first author, year and a keyword, such as
     `vaswani-2017-attention`. Every paper card gets this tag.
   - When a card overlaps a course unit, it also gets **both** course tags,
     `vault::<course>::<unit-id>` and `vault::concept::<concept-id>`, as a BM25 card from a
     ranking paper would. Course units are often built on papers (a databases course might have
     units on Fagin's Threshold Algorithm or C-Store), so check `units.json` for every paper. The
     concept tag routes its leech into the quiz like any vault card. Leave both off when no
     concept matches, and do not invent concepts. The source line still names the paper.
   - Deck: `Vault::Papers` for every claim card. A plain-fact definition with a course concept
     tag goes to that course's subdeck instead.
5. **Mix into the queue:** `python3 scripts/anki_mix.py <note ids in add order>`. This gives each
   card a random position among the new cards already queued, keeping their own order, so paper
   cards are spread through the backlog instead of waiting behind it. Then **sync**.
6. **Mark it in Raindrop:** add the tag `anki` to the bookmark, so the next survey leaves it out.
7. **Record** `sessions/<YYYY-MM-DD-HHMM>-paper-<slug>.md`: the title, authors and year, the
   Raindrop link, and the cards as a table with their note ids. Never store a PDF or quote
   beyond the cards. The papers may be internal, and Raindrop is where they live. Then do "gtg"
   as usual. The PR title is `paper-<slug>: <n> cards`, and there is no `units.json` log entry.

## Leeches → the quiz

A card the learner keeps missing needs teaching, not more repetitions. Anki's leech threshold
(set to 4 lapses, action *Suspend*, see `SETUP.md`) catches it, tags it `leech` and suspends it.

**At session opening**, run `findNotes` with `deck:Vault tag:leech is:suspended`. For each hit:

- Read its `vault::concept::` tag and add **one** item for that concept to this session's quiz, on
  top of the normal draw. Use a bank question on the concept if one is askable; otherwise ask the
  card's own front, generatively, in the artifact.
- Grade and route it exactly like any other quiz miss (`skills/grader/SKILL.md`). A concept that
  fails goes back to `unseen` and the existing repair path takes over.
- Then fix the card: if the miss came from the card's wording, rewrite it (`updateNoteFields`).
  Either way remove the `leech` tag and unsuspend it.
- A paper card with no concept tag (`vault::paper::` only) has no quiz to go to. Re-teach it in
  the artifact instead: reread the passage in Raindrop, explain the idea in a few sentences, and
  ask the card's front generatively. Then rewrite or split the card, and unsuspend it.
- A `vault::topic::` or `vault::report::` card with no concept tag came from an ad-hoc session.
  Re-teach it the same way from the ad-hoc session record in `sessions/` and the source it names, then
  rewrite or split the card and unsuspend it. A topic card that keeps coming back as a leech is
  a sign the topic needs a unit (`skills/ad-hoc/SKILL.md` → "Promotion").
- Any other leech with no concept tag is a card that cannot be routed: put it in the next cleanup
  batch.

No more than three leeches per session; the rest wait.

## Cards the learner flags in review

The learner flags cards in Anki while reviewing, and each flag asks for something different:

- **Marked** (Anki's `marked` tag, Ctrl+K): the card needs one-by-one attention, either a
  clarification (the learner doesn't follow it) or a rewrite (the card is badly made). A
  `clarify` tag says which. Take them one at a time in the artifact: show the card, ask what is
  wrong unless the tag says, then explain or rewrite (`updateNoteFields`, same note id, so the
  review history stays). Remove `marked` and `clarify` once the learner is satisfied.
- **Suspended without a `leech` tag**: the learner judged the card useless. Don't revive or
  rewrite it. Work out what kind of card it is, add that kind to "Cards the learner rejected"
  below so it stops being written, and tag the note `rejected` so it is not processed again.

- **Pending**: a marked card that rests on a concept the learner has not been taught yet
  (its `vault::concept::` tag is `unseen` or `unknown` in `units.json`) is suspended and tagged `pending`,
  not rewritten. Such a card broke "What does not" below; when carding a paper, check each
  concept tag's state before adding the card. The learner can also send a card to pending
  when it needs background they lack. A pending card with no concept tag has nothing to trigger
  its return, so list it at each cleanup for the learner to revive or drop.

**At session opening**, alongside the leech query, run `findNotes` with
`deck:Vault tag:marked`, `deck:Vault is:suspended -tag:leech -tag:rejected -tag:pending`, and
`deck:Vault tag:pending`. For each pending card whose concept is now `seen`, unsuspend it
and remove `pending`. Mention the
counts in one line and work through them when the learner asks.

### Cards the learner rejected

Kinds of card the learner suspended as useless. Never write these.

- **Named baselines.** Which systems a paper compares against (ThalamusDB against MindsDB and
  ABAE) is rote. Card a baseline only when the choice of comparison is itself the argument.
- **How a survey was assembled.** "It classified eight GPU DBMSs" is routine method. Card what a
  survey concludes, not how it was done.
- **Claims that follow from the premise.** Once the front says what the system is, an answer
  the reader could infer from that alone is trivial ("What cost does Cortex AISQL's planner plan
  around?" → "LLM inference cost", for an LLM-in-SQL engine). Card what the premise does not
  predict.
- **A paper's headline win on its own benchmark.** "TracIn surfaces mislabels earliest" says only
  that the method beat the others, which every paper reports. Card what an evaluation was
  designed to show only when the design itself is the contribution.

## Pre-review of unseen cards

To catch cards the learner would mark or suspend before they see them, a pass reviews the new
(never-reviewed) cards in bulk. Run it when the learner asks, or after a large batch of cards.

1. Dump the `deck:Vault is:new -is:suspended` notes, excluding today's cards,
   grouped by paper tag or unit tag, with each concept's state from `units.json`, into
   `all.json` in a scratch directory, and split the groups into chunks of about 90 notes.
2. Hand each chunk to a subagent with `skills/flashcards/PREREVIEW.md` as its brief. Each
   writes `actions<i>.json`: reject, rewrite, or merge, never touching Anki. Check that every
   reviewer covered every group in its chunk.
3. `python3 scripts/anki_prereview_apply.py <dir> --dry`, then without `--dry`, then
   `python3 scripts/anki_decks.py --apply` and sync. Save `applied.json` as
   `sessions/<date>-anki-prereview.json`.

Material the learner hasn't studied is judged by difficulty: keep a card a reader with the
learner's background can understand from its front and back; reject one that needs background
it doesn't give. Update `PREREVIEW.md` with each new lesson from the learner's flags.

## Cleanup

Due when `flashcards.json` → `last_cleanup` is null or more than 30 days old. It runs inside the
same "gtg" feedback turn as the proposals, so the learner sees one batch.

Candidates, each with a one-line reason:
- duplicates or near-duplicates;
- cards that break the rules above (two facts, cloze-shaped, context-dependent wording, a front
  with more than one correct answer, an unprompted list of three or more);
- cards whose unit was archived or whose concept no longer exists;
- leeches with no concept, `vault::paper::`, `vault::topic::`, or `vault::report::` tag;
- `vault::topic::` cards whose topic now has a unit (retag them with the unit and concept tags);
- paper cards whose bookmark is no longer in Raindrop (the learner may have dropped the paper);
- cards in the wrong subdeck, as reported by `python3 scripts/anki_decks.py`.

**Never delete, edit or retag without the learner's yes.** Apply what they approve, then set
`last_cleanup` to today.
