#!/usr/bin/env python3
"""
What to be quizzed on, and what to study. The whole scheduler.

Two draws, both from the same ranking:

  quiz    N units by urgency, one question each, restricted to questions whose concepts have
          all been seen -- so a review is never a test of never-learned material.
  study   one unit by urgency, excluding `learned`, because a learned unit does not need an
          hour; if it has decayed the quiz will demote it and it becomes eligible again.

Both draws are *weighted*, not top-N: an argmax serves whichever unit sits at the top of the
ranking every session until it is exhausted, and never interleaves.

The study draw is additionally **two-stage**, and the two stages answer different questions:

    which course?   `share`, drawn independently each session
    which unit?     urgency, which is (1 - retrievability) x the unit's own priority

That split is what makes `share` mean what it says. A one-stage weighted draw makes a course's
frequency depend on how many units it happens to have eligible, so a course with 80 units drowns
one with 25 unless the priorities are bent to compensate. Choosing the
course first removes unit count from the question entirely, and `priority` goes back to being
only a within-course weight.

The course stage samples independently at the share probabilities and consults no history; see
`units.course_weights` for why it is not a deficit scheme. The unit stage adds small Gaussian
noise to each urgency (`units.UNIT_NOISE`, `--noise`) so the same few units do not always win
inside a course. The quiz draw takes no noise.

Urgency is `(1 - retrievability) x priority` and there is no due date anywhere in here. See
scripts/units.py and CLAUDE.md.

Usage:
    python3 scripts/session.py              # what the tutor opens with
    python3 scripts/session.py -n 12        # a longer quiz
    python3 scripts/session.py --course example
"""
import argparse, json, random, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import units as U

VAULT = Path(__file__).resolve().parent.parent


def load_bank():
    """question id -> record, across every live course."""
    q = {}
    for slug in U.course_slugs():
        p = U.COURSES / slug / "bank.jsonl"
        if not p.exists():
            continue
        for line in p.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                q[r["id"]] = r
    return q


def pick(pool, n, rng, noise=0.0):
    """Weighted sample without replacement, by urgency. Weighted rather than top-N because
    top-N would serve the same handful of units every session and never interleave.

    `noise` adds Gaussian jitter to each unit's urgency before weighting -- see `units.UNIT_NOISE`.
    The study draw passes it so the unit chosen inside a course is not always from the same head of
    the ranking. The quiz leaves it at 0: there, urgency is the entire claim being made.
    """
    chosen, pool = [], list(pool)
    for _ in range(min(n, len(pool))):
        weights = [max(U.jittered_urgency(u, rng, noise), 1e-6) for u in pool]
        total = sum(weights)
        r, acc = rng.random() * total, 0.0
        for i, w in enumerate(weights):
            acc += w
            if acc >= r:
                chosen.append(pool.pop(i))
                break
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-n", "--questions", type=int, default=8)
    ap.add_argument("--course", help="restrict the study pick to one course")
    ap.add_argument("--seed", type=int)
    ap.add_argument("--noise", type=float, default=U.UNIT_NOISE,
                    help="sigma of the Gaussian added to unit urgency in the study draw")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    allu = U.load_all()
    bank = load_bank()

    # --- quiz -------------------------------------------------------------------------------
    quiz_pool = [u for u in allu.values() if U.quiz_eligible(u, allu) and U.askable(u)]
    quiz = []
    for u in pick(quiz_pool, args.questions, rng):
        opts = U.askable(u)
        qid = rng.choice(opts)
        quiz.append({"unit": f"{u['course']}:{u['id']}", "question": qid,
                     "urgency": round(U.urgency(u), 3),
                     "text": bank.get(qid, {}).get("question", "")})

    # --- study ------------------------------------------------------------------------------
    study_pool = [u for u in allu.values() if U.study_eligible(u, allu)]
    if args.course:
        study_pool = [u for u in study_pool if u["course"] == args.course]
    # Stage one: the course, drawn independently each session at probabilities set by `share`.
    # Only courses that can actually offer a unit get a slot; their shares renormalise over that
    # set. No history is consulted -- see units.course_weights for why this is not a deficit.
    by_course = defaultdict(list)
    for u in study_pool:
        by_course[u["course"]].append(u)
    cw = U.course_weights(sorted(by_course))
    study = None
    if by_course:
        slugs = sorted(by_course)
        r, acc = rng.random() * sum(cw[c] for c in slugs), 0.0
        chosen = slugs[-1]
        for c in slugs:
            acc += cw[c]
            if acc >= r:
                chosen = c
                break
        # Stage two: the unit, urgency-weighted inside that course, with noise on the urgency.
        study = pick(by_course[chosen], 1, rng, noise=args.noise)[0]
    # The runners-up are shown, not used: both stages are random, so a session that opens by
    # naming one unit should say what it was drawn over.
    runners = sorted((u for u in study_pool if u is not study),
                     key=lambda u: (-U.urgency(u), u["course"], u["id"]))[:3]

    if args.json:
        print(json.dumps({"quiz": quiz,
                          "study": None if study is None else {
                              "unit": f"{study['course']}:{study['id']}",
                              "title": study["title"], "stage": U.stage(study)}}, indent=2))
        return 0

    print(f"{len(allu)} units — "
          + ", ".join(f"{s}:{sum(1 for u in allu.values() if U.stage(u) == s)}" for s in U.STAGES))

    print(f"\nQUIZ — {len(quiz)} question(s) drawn from {len(quiz_pool)} eligible unit(s)")
    if not quiz_pool:
        print("  Nothing is fair to ask yet: no unit has a question whose concepts have all")
        print("  been seen. Study first; the quiz fills itself in.")
    for q in quiz:
        print(f"  [{q['urgency']:.2f}] {q['unit']:<34} {q['question']}")
        print(f"         {q['text'][:96]}")

    print(f"\nSTUDY — from {len(study_pool)} eligible unit(s) in {len(by_course)} course(s)")
    if by_course:
        print("  course draw: " + ", ".join(
            f"{c.split('-')[0][:4]} {cw[c]*100:.0f}%" for c in sorted(by_course)))
        # Shown, never scheduled on: the draw is independent of history, so a run of one course is
        # ordinary rather than a sign of anything. This line is here so an unwanted run is visible
        # and can be overridden by simply naming a course.
        history = U.recent_study_courses()
        if history:
            mix = ", ".join(f"{c.split('-')[0][:4]} {history.count(c)}"
                            for c in sorted(set(history)))
            print(f"  last {len(history)} curriculum session(s) actually were: {mix}")
    if study is None:
        print("  Nothing eligible. Every unit is muted, blocked on a prerequisite, learned,")
        print("  or missing its reading.")
        return 0
    st = U.stage(study)
    done = len(U.seen_concepts(study))
    tot = len(study.get("concepts") or [])
    print(f"  --> {study['course']}:{study['id']} — {study['title']}")
    print(f"      stage={st}  priority={U.priority(study)}  urgency={U.urgency(study):.2f}  "
          f"concepts {done}/{tot} seen")
    if st == "unknown":
        print("      NOT PLACED. Place it first — a few questions across its concepts, then")
        print("      guess the rest. Err low: too low costs one easy session, too high")
        print("      unblocks material that cannot be understood yet.")
    if runners:
        print("      drawn over: " + ", ".join(
            f"{r['course']}:{r['id']} [{U.urgency(r):.2f}]" for r in runners))
    cur = (study.get("cursor") or {}).get("concept")
    if cur:
        note = (study.get("cursor") or {}).get("note") or ""
        print(f"      resume the sweep at {cur}" + (f" — {note}" if note else ""))
    elif tot:
        print(f"      no cursor — sweep from {study['concepts'][0]['id']}, fast, and stop at")
        print("      the first friction. That is where the teaching goes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
