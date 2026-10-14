# Design decisions

A dated log of the design calls behind the vault and why they were made, so later changes do not
re-litigate or accidentally undo them.

## 2026-08-18 — The unit becomes the only scheduled object

Locked, replacing the course-stride/targets/cards/spurs machinery wholesale.

- **A course is a list of units.** It carries no state. Two courses may reference the same unit.
- **A unit is 1-4 hours to cover every concept once** — roughly a chapter, or part of one where
  the book is dense. In practice 6-20 concepts.
- **Unit stages are `unknown | new | learning | learned`**, derived and never stored:
  unplaced / studied zero times / studied at least once / every concept seen.
- **Concept states are `unknown | unseen | seen`**, and they live **in `units.json`**, not in
  `map.md`. Structure and state change on different schedules, so they are different files.
- **Rank by retrievability × priority; never emit a due date.** FSRS's memory model without its
  scheduler — a three-week gap produces no backlog, only a uniformly staler ordering.
- **Priority is per unit with a course-level default.** `0` mutes material that is real but not
  wanted now. This replaces `targets:` and derived blocking/deferred disposition entirely.
- **Placement guesses, and errs low.** A unit placed too low costs one easy session; a unit
  placed too high unblocks material that cannot be understood yet.
- **No cards.** Factual recall is a question *type* in `bank.jsonl` — "Define X", "What does Y
  mean inside the definition of Z?". Spacing comes from the unit's SRS, not from the question
  being a different kind of object.
- **No repair course and no spurs.** Repeated failure demotes concepts to `unseen`, which drops
  the unit to `learning`. A repaired unit is just a unit.
- **`units.json`, not `units.jsonl`** — pretty-printed, because it is meant to be read and
  edited by hand.

## 2026-09-08 — Everything the learner reads goes in the artifact

Locked, and now stated in five places because it was being violated in practice: the SessionStart
hook prints it, `skills/session/SKILL.md` carries it as the third shaping rule with a
what-goes-where table, and `place`, `tutor` and `grader` each open with it.

- **The artifact carries all content.** Questions, answers, hints, answer keys, grading, every
  derivation, every diagram, every standing observation about the learner. Quiz, placement, study
  and one-off exchanges alike.
- **Chat carries turn-taking only.** Which question is live, that an answer landed, the one-word
  routing outcome, the ids written back, and everything about running the session.
- **The reason is the interface, not taste.** Claude Code renders GitHub-flavoured markdown and
  nothing else — no LaTeX, no image surface. `$\lim_{x\to a} f(x)$` reaches the learner as literal
  backslashes and a figure does not reach them at all. A session run in chat is not slightly
  worse; its mathematics is unreadable and its figures do not exist.
- **Write the artifact first, then speak.** Answering in chat and copying the good parts across
  afterwards is the habit that fails: it loses the notation every time and the figures always.
- **Answers are recorded verbatim**, including a wrong turn the learner later corrected. That turn
  is usually the diagnostic part, and a record showing only the corrected version cannot
  distinguish decay from a badly cut concept later.

## 2026-09-08 — A lapse is counted on `partial`, and on first reviews

`skills/grader/SKILL.md` had always said a retrieval failure writes `srs.lapses += 1`.
`scripts/units.py` did not: it incremented `lapses` inside the `elif grade == "fail"` arm of the
stability branch, so `partial` never counted, and even `fail` was skipped whenever the unit had no
prior stability or `last_seen`. The doc was right and the code has been corrected to match.

- **`lapses` records that the learner could not produce the material cold.** That is a fact about
  the review, so it is now counted before and independently of the stability branch, which is a
  decision about the schedule.
- **First reviews count.** The skipped-first-review case is not an edge case. Whole courses can be
  initialised to `learned` without ever being studied, so a unit's *first* real review is exactly
  the one worth recording, and it was the one being dropped.
- **Nothing was backfilled.** `lapses` counts written under the old behaviour were left alone;
  rewriting them would invent review outcomes that were never observed. Counts recorded before
  this fix are therefore a lower bound.
- **Nothing else moved.** `difficulty` and `stability` are unchanged for every grade and every
  prior state; the fix touches only the counter.

## 2026-09-08 — The study pick is weighted, and priority is a per-unit weight

The goal was roughly equal occurrence across courses, with a mostly-`learned` course a little
lower. Priority alone could not deliver it, and simulation showed it delivering the opposite.

- **An argmax does not interleave, and priority cannot make it.** The study pick took the single
  highest-urgency eligible unit. Dozens of eligible units sat at *exactly* the same urgency —
  never reviewed, so `R = 0` and urgency equals priority exactly — which left the
  `(-urgency, course, id)` tie-break choosing the entire curriculum in alphabetical order by unit
  id. Simulated over 40 sessions at flat priorities, **every session** went to whichever course
  won the alphabetical tie. Raising the parked courses made the monoculture worse, not better.
- **So the study pick is now weighted**, using the same `pick()` the quiz has always used. This
  reverses the "deterministic, not weighted" line in the README, and it is reversed on the vault's
  own reasoning: `pick()` exists because "top-N would serve the same handful every session and
  never interleave," and top-1 is top-N with N=1. `session.py` now prints the three highest-urgency
  runners-up next to the pick, so a weighted draw is still legible and easy to override.
- **Priority is a per-unit weight, not a course ranking.** A course's share of either draw is its
  per-unit priority multiplied by how many of its units are eligible, so a large course needs a
  *lower* number to get the same share. Recalibrated from measured eligible mass: for example, a
  course with 6 eligible units needed priority 10 to match one with 30 eligible units at 2.
- **Muted units stay muted.** Units at `priority: 0` were set deliberately and were not touched.
- **The quiz stays weighted toward whichever course has the most studied material, and priority
  will not fix it.** Quiz eligibility needs studied material. It corrects as the other courses are
  actually studied, not by turning a number.

## 2026-09-08 — `share` decides the course, urgency decides the unit

Superseding the priority recalibration recorded above, which was made the same day and lasted a
few hours. That fix worked but priced course frequency in the wrong currency: it set per-unit
weights to compensate for unit counts, so a large course had to sit at 2 and a small one at 10 to
come out level, and nobody reading those numbers later would have guessed why.

- **The study draw is two-stage.** Which course, by `share`; then which unit, urgency-weighted
  inside that course alone. A single weighted draw ties a course's frequency to how many units it
  happens to have eligible, which is the whole problem. Choosing the course first removes unit
  count from the question.
- **`share` is a course-header field and reads as sessions out of ten**, for example 3, 3, 2 and 2
  across four courses. Shares sum to `SHARE_WINDOW` on purpose. A course with no eligible unit
  holds no slot and the rest renormalise, so muting or exhausting a course redistributes its share
  instead of wasting it.
- **`priority` goes back to being a within-course weight only**, and every course returns to
  `default_priority: 5`. Explicit per-unit priorities that only duplicated an old course default
  were removed, because against a default of 5 they would have silently become real demotions.
  Units muted at `priority: 0` are untouched.
- **The course stage scores by deficit, not by probability.** Target share minus what the last ten
  sessions actually served, with the history read off `sessions/` filenames — the vault's own
  record, so the rotation needs no counter of its own. Independent draws at the target
  probabilities have the right mean and the wrong short run: over ten sessions, sd ≈ 1.4 against a
  target of 3, with all-zero windows ordinary. Deficit scoring pushes back against whatever the
  last few sessions did.
- **`JITTER` is the deliberate leak, and it is the only dial.** Every eligible course keeps a floor
  of weight however far ahead it is, so surprise is always possible and the rotation never becomes
  a recitable cycle. Measured over 200 windows of ten:

  | `JITTER` | windows exactly on target | mean error per course |
  |---|---|---|
  | 0.00 | 100% | 0.00 |
  | 0.15 | 52% | 0.27 |
  | **0.35** (default) | 30% | 0.46 |
  | 0.60 | 18% | 0.61 |
  | 1.00 | 11% | 0.72 |
  | independent draws | ~4% | ~0.95 |

  0.35 was chosen to sit near the middle: mean counts on target, roughly half the spread of naive
  sampling, and a real chance of an off-pattern session. `--jitter` overrides it per run.
- **Session filenames became load-bearing**, and that is a genuine cost of this design. A study
  session not named `<date>-<unit-id>.md` is invisible to the rotation and quietly starves its own
  course. Recorded in `SCHEMA.md` and in `skills/session/SKILL.md`. Existing files that break the
  convention were left alone rather than renamed, since renaming a session record rewrites history
  to suit a scheduler.
- **The quiz was deliberately left alone.** Course shares are not applied to it. The quiz's job is
  to return what has been studied, and forcing course balance would over-drill the thin courses,
  which may have only a handful of quiz-eligible units or none. It stays urgency-weighted and evens
  out as the other courses are actually studied.

## 2026-09-08 — The course draw is i.i.d.; the noise moves to the unit

Correcting the entry above, made an hour earlier. The shares and the two-stage structure stand;
the deficit scheduler and the course-level jitter do not.

- **Courses are drawn independently each session**, at probabilities set by `share` (30/30/20/20
  for shares 3, 3, 2 and 2). No history is consulted. The deficit scheme it replaces (target minus
  what the last ten sessions served) did hit every ten-session window exactly, and that was the
  wrong target: *roughly* 3:3:2:2 on average was what was wanted, not a rotation locked to 3:3:2:2
  every ten sessions.
- **Streaks are the accepted cost and they are not a defect.** Over ten sessions a `share: 3`
  course returns 0 to 8 times, sd ≈ 1.5, and P(same course twice running) is 0.27 — measured across
  400 windows and matching the i.i.d. prediction of 0.26 exactly. The remedy for an unlucky run is
  to name a course, which overrides the draw in one sentence. A scheduler that cannot produce an
  unlucky run also cannot produce a surprise, and the run is the cheaper problem.
- **`units.recent_study_courses()` survives as display only.** `session.py` prints the recent mix
  so an unwanted run is visible and can be overridden, but nothing schedules on it. This also
  retires the cost recorded above: session filenames are no longer load-bearing, and
  off-convention files stay unremarkable.
- **The jitter moves from the course to the unit, and becomes Gaussian.** `units.UNIT_NOISE`,
  sigma 0.25, added to `(1 - retrievability) x priority` before weighting, clamped at zero.
  Measured: it leaves units of comparable urgency where they were, and its one real effect is at
  the floor — a unit reviewed today has urgency exactly 0 and was unreachable, and now has about a
  1.3% chance. That is a partial answer to the unfinished-unit problem, arrived at sideways.
- **The quiz draw takes no noise.** `pick()` gained a `noise` parameter defaulting to 0, and only
  the study draw passes it. In the quiz the urgency ranking is the entire claim being made.
- **The `JITTER` dial and its calibration table are gone**, along with the flaw found in them: a
  flat floor added per course pulled the draw toward uniform as it grew rather than toward the
  shares, and quietly favoured whichever course asked for least.

## 2026-10-05 — "gtg" merges to `main` automatically

- Ending a session now commits, pushes, opens a PR and merges it, gated only on
  `check_vault.py` reporting zero errors (`skills/session/SKILL.md` → "gtg"). The repo is almost
  all data, every session's writes are state the learner already saw land in the artifact, and a
  manual review step was adding friction outside the material — the thing rule 1 says to remove.
- Merge commit, not squash: the per-concept commits are the cursor's audit trail.

## 2026-10-05 — A flashcard layer in Anki, below the bank

- Easy, one-sentence front–back cards for atomic facts, written by the agent and approved by the
  learner in one feedback turn at "gtg" (`skills/flashcards/SKILL.md`). The bank stays the
  demanding layer; the deck only keeps facts warm between sessions 2–3 days apart. The layer is
  optional, and sessions without Anki skip it.
- Anki desktop + AnkiConnect + `@ankimcp/anki-mcp-server`, with sessions run on the machine where
  Anki desktop runs. The cloud container cannot reach a local Anki, and AnkiWeb's terms rule out
  third-party sync clients. Cloud sessions skip the flashcard steps.
- One `Vault` deck, FSRS, desired retention 0.80, about 15 min/day via the review cap. A card that
  lapses 4 times is suspended as a leech and its concept is pulled into the next quiz, so repeated
  failure is routed to teaching instead of more repetitions.

**Amended 2026-10-05, after a local setup:** the review cap is 100 a day, not 120, which is about
12 minutes instead of 15, to keep the daily load lighter. The whole path was tested end to end:
AnkiConnect reached from WSL over mirrored networking, the `anki` MCP server, `addNote` with
MathJax and two tags, `sync` to a phone, `deleteNotes`, and the leech query. Two setup problems
came up, and `skills/flashcards/SETUP.md` now covers both. A `.wslconfig` saved as UTF-16 is
silently ignored. AnkiConnect also does not load until Anki is fully restarted.

## 2026-10-05 — Work papers go into the same deck, through Raindrop

- Papers the learner reads for work, outside any course, are carded into the `Vault` deck under
  the same rules and the same 100-a-day cap (`skills/flashcards/SKILL.md` → "Work papers"). There
  is no separate deck and no separate budget, so the reviews stay seamless.
- **Raindrop is the source.** This integration is optional and assumes the learner keeps these
  papers in Raindrop.io. The agent reads the bookmark, its highlights and its full text through
  Raindrop's official MCP server, and the repo stores no PDFs. The papers may be internal. The
  session record holds only the title, the Raindrop link and the cards. A carded bookmark gets the
  tag `anki`.
- **Local only.** Cards are written from a session on the machine where Anki runs, like every
  other flashcard step. There is no pending queue for cloud sessions, by choice.
- **Mixed randomly into the new-card queue** (`scripts/anki_mix.py`), not appended behind the
  existing backlog and not put ahead of it. Each paper card gets a random position among the
  queued new cards, and the paper's own definition-first order is kept. The anki MCP server has
  no reposition tool, so the script calls AnkiConnect's `setSpecificValueOfCard` on `due`. This
  was tested on a live deck with two throwaway notes, which were then deleted.
- Paper cards are tagged `vault::paper::<slug>`, plus `vault::concept::<id>` when they state an
  existing course concept. A paper-only leech has no quiz to go to, so it is re-taught from the
  Raindrop passage in the artifact and then rewritten.

## 2026-10-05 — Work papers: the learner picks, stars set the budget, cards ask what the paper claims

- Only important papers are carded. "Untagged with `anki`" no longer means "to card", because
  that matched almost the whole library. The agent surveys the Raindrop library by topic, lists
  the papers that look important in the learner's work topics, and the learner replies with
  `#` plus stars. One star is one card, the main claim only; more stars give more cards
  (`skills/flashcards/SKILL.md` → "Work papers").
- Every paper card asks what the paper claims ("What does X (Author Year) claim about …?") and
  never states the claim as a general fact. Most of these papers are recent and contested. The
  only exception is a definition of an established term, at three stars and up.

## 2026-10-05 — Card format: source line, answer-only backs, lists; deeper star budgets

- Every front opens with a bold source line, then `<br>`: the paper's title, up to three
  author surnames and the year for a paper card, or the course and unit title for a course card.
  Existing course notes were given theirs in place (same note ids, review history kept).
- Backs are the answer only. "Claims:" and similar prefixes are gone, because the front already
  carries the attribution. Backs are terser, and a multi-part answer is a bulleted list.
- The star budgets became ranges and the top end went up: `*` 1–2, `**` 2–4, `***` 3–6,
  `****` 5–10. A four-star paper gets a deep dive into its method, experiments and arguments,
  at the cost of a higher total.
- A paper card that overlaps a course unit carries that unit's tag and its concept tag as well
  as the paper tag. Meta cards about a paper (its impact, what it superseded) are allowed when
  the drafter is confident.

## 2026-10-05 — Paper cards ask reading-group questions

- Paper cards moved away from rote facts. Experimental numbers and implementation details (which
  strategies were adopted, component names) are no longer carded. Cards ask what a research
  reading group would ask instead: the novel contribution, the key choices in formulation, design
  and experiments and why they were made, the experimental design (research questions, tasks,
  datasets, baselines), the paper's arguments, and contrasts with related papers in the learner's
  own library (`skills/flashcards/SKILL.md` → "Ask what a reading group would ask").

## 2026-10-13 — An English vocabulary deck, sorted by the learner, two cards a word

- `Vault::Vocabulary` holds English vocabulary for reading and writing: words that are
  nontrivial but still used in demanding modern nonfiction and literary fiction, not archaic
  ones (`skills/flashcards/SKILL.md` → "Vocabulary"). It is a deck only, with no course, kept in
  the vault because the vault manages everything in Anki.
- **Two cards per word, word → meaning and meaning → word,** through a custom note type,
  `Vault Vocabulary`. This is a deliberate exception to "no reversed cards": reading needs the
  first direction, writing the second, and neither trains the other fully. The note type also
  puts the learning aids (connotation, an example, etymology, contrasts) at the bottom of both
  backs, which `Basic` cannot do for a reversed pair.
- **Candidates come from public lists, filtered by frequency, and the learner sorts them.**
  Capturing words met in reading fails when the reading happens on a device with no export. The
  pool is SAT, GRE and word-of-the-day lists, kept to Zipf 1.9–3.2 (words at the target level sit
  at 2.1–2.9, vouchsafe at 1.7). A sorting page shows each word with its definition and takes one
  of four keys: new or known, crossed with add or skip. Skips split into "too obscure" and "too
  easy" so the band can be tuned. "Too obscure" means never seen once; anything the learner has
  vaguely seen is worth adding. In practice the never-seen words fall at the same frequencies as
  the adds, so the band alone cannot filter them out.
- A multi-sense word is one note whose cards ask for every sense, with labeled blanks. The
  carded form is the most common one. There is no pronunciation. The learner sets the
  subdeck's scheduling.

## 2026-10-13 — Learner flags in review: marked means fix, suspended means useless

- The learner flags cards while reviewing. A **marked** card needs one-by-one attention, a
  clarification or a rewrite (a `clarify` tag says which), done in place so its history stays.
  A card **suspended** without a `leech` tag is useless: it stays suspended, is tagged
  `rejected`, and its kind goes into "Cards the learner rejected" in
  `skills/flashcards/SKILL.md` so it stops being written. Sessions open by counting both.
- Early rejections set two rules: no cards on which named systems a paper uses as baselines, and
  no cards on how a survey was assembled. Baselines left the "experimental design" list of what
  to card from a paper.
- **Amended the same day: an automated pre-review of unseen cards.** Subagents review
  never-reviewed cards in bulk against the rules and the learner's flags (brief:
  `skills/flashcards/PREREVIEW.md`), suspending some as `rejected autopass`, rewriting others,
  and merging related cards into cloze notes. The rule for unstudied material: if a card is too
  hard to learn from its front and back it is useless; otherwise the learner learns it by
  inference from the back. Originals are saved in `sessions/<date>-anki-prereview.json`.
