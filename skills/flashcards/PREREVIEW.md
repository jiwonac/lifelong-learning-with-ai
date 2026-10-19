# Automated pre-review of unseen Anki cards

Catch the unseen cards the learner would flag in review (**marked**: confusing or badly made; **suspended**: useless).
Change only clear cases, and leave borderline cards alone.

Every rewrite follows `skills/flashcards/SKILL.md`, especially "Writing a card", "Work papers", and "Cards the learner rejected".
Read it first.

## Lessons from the learner's flags

The learner wrote or approved these rewrites; follow their taste.

- Closely related questions that each need the others as context → ONE cloze note with several deletions: Basic "What limit does the Ratio Test compute?" → Cloze: "The purpose of the Ratio Test is to
  {{c1::test if a series converges}}. It computes \(R=\){{c2::\(\lim|a_{n+1}/a_n|\)}}. The
  convergence rule is {{c3::\(R<1\) converges, \(R>1\) diverges, \(R=1\) unknown}}."
- Two-fact Basic backs ("Encodes separately … so vectors are precomputable") → split into deletions or into two short cloze notes.
- Vague answers ("Unevenly", "It surfaces them earliest") → name the mechanism, or reject.
- Long fronts leaning on a second paper the learner may not know (an MT-Eval comparison) → drop it, and define the paper's own term (e.g. self-conditioning) inline.
- A list card naming items without saying what they are (PagedAttention's three kinds of waste) → pair each name with its meaning, one deletion per item.
- A paper-framed card about a plain property of a standard metric ("What does nDCG@10 have that precision lacks, per BEIR?") → reject; plain definitions belong in plain cards.
- Report the terms a cloze paragraph uses but doesn't define; don't invent cards for them.
- A list the learner cannot recall cold → cue each item with its category: "(data) {{c1::categorical features}}; (training) {{c2::insufficient hyperparameter tuning}}".
- A long sentence listing named items with meanings → a lettered list, name and meaning as separate deletions.
- A deletion that hides a causal chain ("varies the positional bias, so errors differ and cancel") → keep the chain visible and delete only the contrast: "{{c1::shuffling the input order}} mitigates positional bias; {{c2::raising temperature}} does not."
- An awkward short title mid-sentence → "George et al.", "Freitag et al.".
- A finding of paper B carded under paper A (BEIR's result about ColBERT) → refile it to B.
- Trivia (awards, descendants) and "what earlier work could not do" → reject.

Reject every kind in SKILL.md → "Cards the learner rejected", plus experimental numbers and material too hard to learn from the card alone.
For material the learner has not studied (`concept_states` shows `unseen`/`unknown`), keep a card that a reader with the learner's background (for example, CS, databases and ML) could understand from front and back alone.
Reject one that needs background the card doesn't give (e.g. "join-project plans stay within the AGM bound", semijoin reduction, influence-function Hessian details).

## What to output

Do not touch Anki.
Write a JSON file (path given in your prompt) with one action per card you change.

```json
[
 {"action": "reject", "ids": [123], "reason": "named baselines"},
 {"action": "rewrite", "ids": [124], "reason": "two facts; cloze clearer",
  "model": "Cloze", "fields": {"Text": "...", "Back Extra": "..."}},
 {"action": "merge", "ids": [125, 126, 127], "reason": "three closely related questions",
  "model": "Cloze", "fields": {"Text": "...", "Back Extra": "..."}}
]
```

- `rewrite` replaces one note. `merge` replaces several notes of the SAME group with one note. The new note keeps the old notes' deck and the union of their tags (minus `marked`).
- `model` is `Basic` (fields `Front`, `Back`) or `Cloze` (fields `Text`, `Back Extra`).
- Keep every formatting convention from "Writing a card". Copy the `<div class="src">…</div><br>` source line exactly from the original.
- **Never add claims that are not on the original cards**, except widely known textbook facts (definitions).
- Change a card only when you are fairly sure the learner would flag it. Expect to change maybe 10–30% of cards.

At the end of your reply, give counts (kept / rewritten / merged / rejected) and list any undefined terms you noticed.
