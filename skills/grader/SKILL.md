# Grader

The grader marks answers and turns each result into a write.
Use it whenever the user answers a bank question: in the session quiz, mid-sweep, or handed back later.

The point is routing.
A result that does not change what gets asked next wasted the question.

## Your marking goes in the artifact

The verdict, what was missing, the answer key, the hint and what it unlocked, and any worked correction all go on the session page.
Chat gets the one-word routing outcome and the ids that were written.
Grading feedback is the most notation-dense thing this vault produces, and the terminal renders none of it; see `skills/session/SKILL.md` -> **Everything goes in the artifact**.
Record the learner's answer verbatim there, including a wrong turn they later corrected, since that turn is usually the diagnostic part.

## Grade generously on substance, strictly on production

The test is whether the user can *produce* the idea, in any words.
Accept a different but correct derivation, a different framing, or a correct answer with sloppy notation.
Reject a restatement of the question, a correct-sounding sentence with the mechanism missing, and "I know this one" without the production.

Say what was missing in one or two sentences.
Do not lecture; teaching happens in the sweep.

**A `?` on a badly written question is the author's error.**
If the question is ambiguous, has no correct answer, or the source resolves it two ways, score it out and say so, because a miss recorded on a bad question corrupts the unit's state.
Fix the bank entry while you are there.

**A vocabulary or factual-terminology miss gets its own bank question, on the spot.**
This covers answers where the mechanism is right but the learner mis-names or mis-states the underlying fact, such as calling a removable discontinuity "no discontinuity" or dropping a theorem's hypothesis from its statement.
Such a miss is too small to demote a concept over, but it still needs a fix.
Author a `definition`-type question isolating exactly that fact, append it to the course's `bank.jsonl`, and link its id onto the concept's `questions` array so the SRS picks it up.
This follows the `CLAUDE.md` rule that factual recall is a question type: the fix for a vocabulary miss is a question, never a flashcard.

## Classify every miss before recording it

The classification decides the write:

| what happened | what it means | what to write |
|---|---|---|
| **careless slip** — knew it on sight once shown | nothing is wrong with the model | nothing. **Never demote on a slip.** |
| **retrieval failure** — could not produce it cold, rebuilt it with a hint | the model is intact, the path to it is stale | `srs.lapses += 1`; concept stays `seen` |
| **model failure** — could not produce it or rebuild it | the concept is not there | concept back to `unseen`, `srs.lapses += 1`, name it in `log.failed` |

Telling the middle row from the bottom row is the main judgement call in this skill.
The test: **give one hint, no more.**
If the hint unlocks a full derivation, the model is there and retrieval was stale.
If the hint produces a guess or a restatement, the model is not there.

## Then write back

Everything lands in `courses/<slug>/units.json`, on the unit and on its concepts.

```
srs.last_seen = today
srs.reps     += 1
srs.lapses   += 1          on a retrieval or model failure
```

Do not compute this by hand.
**`scripts/review.py` is the only thing that should touch the SRS numbers**, and it maps the table's three rows onto its three grades:

    careless slip / clean pass  -> pass
    retrieval failure (hinted)  -> partial
    model failure               -> fail

```
python3 scripts/review.py example:ex-binary-search partial \
    --seen ex-bs-invariant --demote ex-bs-interval-conventions \
    --cursor ex-bs-interval-conventions --note "invariant solid; half-open updates needed the hint twice"
```

One call writes `difficulty`, `stability`, `reps`, `lapses`, `last_seen`, the concept states, the cursor and the log entry.
A lapse multiplies stability rather than resetting it.
The gain on a pass is damped by how retrievable the unit already was, so an effortful review counts for more than a fresh one.

**Demotion is the repair mechanism.**
Enough concepts back to `unseen` drops the unit out of `learned`, and it re-enters the study pool on its own at the next evaluation.
There is no separate repair path or escalation; a repaired unit is just a unit.

## What a repeated failure means

One cold miss on a `seen` concept is ordinary decay, and the SRS handles it by bringing the concept back sooner.
**A second cold miss is a model gap**, and more spacing will not fix it.
Mark the concept `unseen` so the sweep reaches it again and teaches it.

If several failures cluster in one region of a unit, or across units that share a prerequisite, the learner has a hole in the foundations.
Say so.
The prerequisite unit is probably the next session.

## Notes

- Record misses in the unit's `log` with the concept ids, not just a count. A later reader needs to know *what* failed to tell a decayed unit from a badly cut one.
- A standing observation about *how this learner fails*, as opposed to what they missed today, goes in the unit's `log` with the question id. Do not keep a separate learner model file: an unsourced generalisation about the learner is worse than none, and a sourced one belongs next to its evidence.
