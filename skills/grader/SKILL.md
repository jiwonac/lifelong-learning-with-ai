# Grader

Marks answers and turns each result into a write. Use whenever the user answers a bank question —
in the session quiz, mid-sweep, or handed back later.

Grading is not the point; **routing is**. A result that does not change what gets asked next was
a waste of the question.

## Your marking goes in the artifact

Not in chat. The verdict, what was missing, the answer key, the hint and what it unlocked, and any
worked correction all belong on the session page; chat gets the one-word routing outcome and the
ids that were written. Grading feedback is the most notation-dense thing this vault produces, and
the terminal renders none of it — see `skills/session/SKILL.md` -> **Everything goes in the
artifact**. Record the learner's answer verbatim there, including a wrong turn they later
corrected, since that turn is usually the diagnostic part.

## Grade generously on substance, strictly on production

The question is whether the user can *produce* the idea, not whether they produced it in the
answer key's words. Accept a different-but-correct derivation, a different framing, a correct
answer with sloppy notation. Reject a restatement of the question, a correct-sounding sentence
with the mechanism missing, and "I know this one" without the production.

Say what was missing in one or two sentences. Do not lecture — the teaching happens in the sweep,
where there is room for it.

**A `?` on a badly written question is the author's error.** If the question is ambiguous, has no
correct answer, or the source resolves it two ways, score it out and say so, because a miss recorded on a bad
question corrupts the unit's state. Fix the bank entry while you are there.

**A vocabulary or factual-terminology miss gets its own bank question, on the spot.** When the
mechanism is right but the learner mis-names or mis-states the underlying fact — a removable
discontinuity called "no discontinuity," a theorem's hypothesis dropped from its statement — that
is not a model gap worth demoting a concept over, and it is not nothing either. Author a
`definition`-type question isolating exactly that fact, append it to the course's `bank.jsonl`,
and link its id onto the concept's `questions` array so the SRS picks it up going forward. This is
what `SCHEMA.md` means by "factual recall is a question type, not a separate object" — the fix for
a vocabulary miss is a question, not a flashcard.

## Classify every miss before recording it

The classification decides the write, and the three are genuinely different failures:

| what happened | what it means | what to write |
|---|---|---|
| **careless slip** — knew it on sight once shown | nothing is wrong with the model | nothing. **Never demote on a slip.** |
| **retrieval failure** — could not produce it cold, rebuilt it with a hint | the model is intact, the path to it is stale | `srs.lapses += 1`; concept stays `seen` |
| **model failure** — could not produce it or rebuild it | the concept is not there | concept back to `unseen`, `srs.lapses += 1`, name it in `log.failed` |

Distinguishing the middle row from the bottom is the judgement call this skill exists for. The
test: **give one hint, no more.** If the hint unlocks a full derivation, the model is there and
the retrieval was stale. If the hint produces a guess or a restatement, the model is not there.

## Then write back

Everything lands in `courses/<slug>/units.json`, on the unit and on its concepts.

```
srs.last_seen = today
srs.reps     += 1
srs.lapses   += 1          on a retrieval or model failure
```

Do not compute this by hand. **`scripts/review.py` is the only thing that should touch the SRS
numbers**, and it maps this table's three rows onto its three grades exactly:

    careless slip / clean pass  -> pass
    retrieval failure (hinted)  -> partial
    model failure               -> fail

```
python3 scripts/review.py example:ex-binary-search partial \
    --seen ex-bs-invariant --demote ex-bs-interval-conventions \
    --cursor ex-bs-interval-conventions --note "invariant solid; half-open updates needed the hint twice"
```

It writes `difficulty`, `stability`, `reps`, `lapses`, `last_seen`, the concept states, the
cursor and the log entry in one call. A lapse multiplies stability rather than resetting it, and
the gain on a pass is damped by how retrievable the unit already was — an effortful review is
worth far more to the schedule than a fresh one.

**Demotion is the repair mechanism.** Enough concepts back to `unseen` drops the unit out of
`learned`, and it re-enters the study pool on its own at the next evaluation. There is no repair
course, no spur, no escalation path and no second code path. A repaired unit is just a unit.

## What a repeated failure means

One cold miss on a `seen` concept is ordinary decay — the SRS handles it by bringing the concept
back sooner. **A second cold miss is not decay**; it is a model gap wearing decay's clothes, and
more spacing will not fix it. Mark the concept `unseen` so the sweep reaches it again and it gets
taught rather than tested.

If several failures cluster in one region of a unit — or across units that share a prerequisite —
that is a hole, not stray facts. Say so out loud. The prerequisite unit is probably the next
session.

## Notes

- Record misses in the unit's `log` with the concept ids, not just a count. A later reader needs
  to know *what* failed to tell a decayed unit from a badly cut one.
- A standing observation about *how this learner fails* — as opposed to what they missed today —
  goes in the unit's `log` with the question id, not into a separate model file. There is no
  global learner document: an unsourced generalisation about the learner is worse than none, and
  a sourced one already has a home next to the evidence.
