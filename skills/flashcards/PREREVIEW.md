# Automated pre-review of unseen Anki cards

The learner reviews these cards in Anki and flags bad ones: **marked** = confusing or badly made
(needs a rewrite), **suspended** = useless. Your job is to catch the cards they would flag before
they see them. It won't be perfect; aim for the clear cases and leave borderline cards alone.

Read `skills/flashcards/SKILL.md` (relative to the vault root) first, especially "Writing a
card", "Work papers", and "Cards the learner rejected". Those rules govern every rewrite.

## Lessons from the learner's flags

Rewrites the learner wrote or approved (their taste, follow it). These are examples; replace and
extend them with lessons from your own flags as they accumulate:

- Basic "What equation does the limit L of a convergent recursive sequence satisfy?" →
  Cloze: "To find the limit \(L\) of a convergent recursive sequence \(a_{n+1}=f(a_n)\), we use
  the identity {{c1::\(L=f(L)\)}}, which holds since {{c1::if \(a_n=L\) then \(a_{n+1}=L\) also}}."
- Basic "What limit does the Ratio Test compute?" → Cloze: "The purpose of the Ratio Test is to
  {{c1::test if a series converges}}. It computes \(R=\){{c2::\(\lim|a_{n+1}/a_n|\)}}. The
  convergence rule is {{c3::\(R<1\) converges, \(R>1\) diverges, \(R=1\) unknown}}."
- **General pattern:** a few very closely related questions, each needing
  the others as context, are better as ONE cloze note with several deletions. Same-numbered
  deletions hide together (a fact and its reason); different numbers are separate cards.
- Two-fact Basic backs ("Encodes separately … so vectors are precomputable") → split into
  deletions or into two short cloze notes.
- Vague answers ("Unevenly", "It surfaces them earliest") → name the mechanism, or reject.
- Long fronts that lean on a second paper the learner may not know (an MT-Eval comparison) →
  drop the second paper; define the paper's own term (e.g. self-conditioning) in the sentence.
- A list card that names items without saying what they are (PagedAttention's three kinds of
  waste) → pair each name with what it means, one deletion number per item.
- A paper-framed card about a plain property of a standard metric ("What does nDCG@10 have that
  precision lacks, per BEIR?") → reject; plain definitions belong in plain cards.
- Terms a cloze paragraph uses but doesn't define get noted (report them; don't invent cards).

Rejected kinds (reject these):
- named baselines a paper compares against, unless the choice of comparison is the argument;
- how a survey was assembled;
- answers the reader could infer from the front's own premise (an LLM-in-SQL engine "plans
  around LLM inference cost");
- a paper's headline win on its own benchmark;
- experimental numbers (already in the rules);
- **material too hard to learn from the card alone.** Many cards cover papers or course
  concepts the learner has not studied (`concept_states` shows `unseen`/`unknown`). Judge each:
  if a reader with the learner's background (for example, CS, databases and ML) could understand it from the front and back
  alone, keep it (they learn by inference); if it needs background the card doesn't give
  (e.g. "join-project plans stay within the AGM bound", semijoin reduction, influence-function
  Hessian details), reject it.

## What to output

Do not touch Anki. Write a JSON file (path given in your prompt): a list of actions, one per
card you change. Cards you keep unchanged are not listed.

```json
[
 {"action": "reject", "ids": [123], "reason": "named baselines"},
 {"action": "rewrite", "ids": [124], "reason": "two facts; cloze clearer",
  "model": "Cloze", "fields": {"Text": "...", "Back Extra": "..."}},
 {"action": "merge", "ids": [125, 126, 127], "reason": "three closely related questions",
  "model": "Cloze", "fields": {"Text": "...", "Back Extra": "..."}}
]
```

- `rewrite` replaces one note; `merge` replaces several notes of the SAME group with one note.
  The new note keeps the old notes' deck and the union of their tags (minus `marked`).
- `model` is `Basic` (fields `Front`, `Back`) or `Cloze` (fields `Text`, `Back Extra`).
- Keep every formatting convention from SKILL.md: the `<div class="src">…</div><br>` source line
  copied exactly from the original, `<span class="ttl">` paper names, `<b>` keyword, MathJax
  `\(...\)`, `<div class="expl">` explanation (in `Back Extra` for cloze, after `<br><br>` on a
  Basic back).
- **Never add claims that are not on the original cards**, except widely known textbook facts
  (definitions). Restructure and clarify; don't invent paper findings.
- Be conservative: change a card only when you are fairly sure the learner would flag it. A
  typical well-made card should be kept. Expect to change maybe 10–30% of cards.

At the end of your reply, give counts (kept / rewritten / merged / rejected) and list any
undefined terms you noticed.
