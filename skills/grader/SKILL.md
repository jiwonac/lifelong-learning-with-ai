# Grader

The grader marks answers and turns each result into a write.
Use it whenever the user answers a bank question: in the session quiz, mid-sweep, or handed back later.
A result that does not change what gets asked next wasted the question.

## Your marking goes in the artifact

The verdict, answer key, hint and worked correction go on the session page, with the learner's answer verbatim; chat gets the routing outcome and the ids written.
See `skills/session/SKILL.md` → **Everything goes in the artifact**.

## Grade generously on substance, strictly on production

The test is whether the user can *produce* the idea, in any words.
Accept a different but correct derivation, a different framing, or a correct answer with sloppy notation.
Reject a restatement of the question, a correct-sounding sentence with the mechanism missing, and "I know this one" without the production.

Say what was missing in one or two sentences.
Do not lecture; teaching happens in the sweep.

**A `?` on a badly written question is the author's error.**
If the question is ambiguous, has no correct answer, or the source resolves it two ways, score it out and say so rather than recording a miss.
Fix the bank entry while you are there.

**A vocabulary or factual-terminology miss gets its own bank question, on the spot.**
This covers answers where the mechanism is right but the learner mis-names or mis-states the underlying fact, such as calling a removable discontinuity "no discontinuity" or dropping a theorem's hypothesis from its statement.
Such a miss is too small to demote a concept over.
Author a `definition`-type question isolating exactly that fact, append it to the course's `bank.jsonl`, and link its id onto the concept's `questions` array.
The fix is a question, never a flashcard (`CLAUDE.md` → bank.jsonl, "Factual recall is a question type").

## Classify every miss before recording it

The classification decides the write:

| what happened | what it means | what to write |
|---|---|---|
| **careless slip**: knew it on sight once shown | nothing is wrong with the model | nothing. **Never demote on a slip.** |
| **retrieval failure**: could not produce it cold, rebuilt it with a hint | the model is intact, the path to it is stale | `srs.lapses += 1`; concept stays `seen` |
| **model failure**: could not produce it or rebuild it | the concept is not there | concept back to `unseen`, `srs.lapses += 1`, name it in `log.failed` |

To tell the middle row from the bottom row, **give one hint, no more.**
If the hint unlocks a full derivation, the model is there and retrieval was stale.
If the hint produces a guess or a restatement, the model is not there.

**A second cold miss on a `seen` concept is a model gap**: mark it `unseen`, because more spacing will not fix it.
If several failures cluster in one region of a unit, or across units that share a prerequisite, say the learner has a hole in the foundations; the prerequisite unit is probably the next session.

## Then write back

Record the result with `scripts/review.py`, never by hand. It maps the table's rows onto its three grades:

    careless slip / clean pass  -> pass
    retrieval failure (hinted)  -> partial
    model failure               -> fail

```
python3 scripts/review.py example:ex-binary-search partial \
    --seen ex-bs-invariant --demote ex-bs-interval-conventions \
    --cursor ex-bs-interval-conventions --note "invariant solid; half-open updates needed the hint twice"
```

Demotion is the whole repair mechanism (`CLAUDE.md` → "stage").

## Notes

A standing observation about *how this learner fails*, as opposed to what they missed today, goes in the unit's `log` with the question id.
Keep no separate learner model file; an observation belongs next to its evidence.
