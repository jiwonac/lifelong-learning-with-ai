#!/usr/bin/env python3
"""
Where the bank is thin, and where units are unready.

Answers the two questions worth asking of the material as a whole: which units have no way to be
quizzed (no questions, or no questions that are fair to ask yet), and which concepts nothing in
the bank tests. Both are inputs to `skills/bank-generator/SKILL.md`.

Usage:
    python3 scripts/bank_stats.py             # per-course summary
    python3 scripts/bank_stats.py --units     # every unit
    python3 scripts/bank_stats.py --gaps      # concepts no question reaches
"""
import argparse, sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import units as U
from session import load_bank


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", action="store_true")
    ap.add_argument("--gaps", action="store_true")
    ap.add_argument("--course")
    args = ap.parse_args()

    allu = U.load_all()
    bank = load_bank()

    per = defaultdict(lambda: defaultdict(int))
    dry, gaps = [], defaultdict(list)
    for key, u in sorted(allu.items()):
        c = u["course"]
        if args.course and c != args.course:
            continue
        p = per[c]
        p["units"] += 1
        p[U.stage(u)] += 1
        p["questions"] += len(U.unit_questions(u))
        p["concepts"] += len(u.get("concepts") or [])
        p["seen"] += len(U.seen_concepts(u))
        ask = U.askable(u)
        if ask:
            p["units_askable"] += 1
        elif u.get("concepts") or U.unit_questions(u):
            dry.append((key, len(U.unit_questions(u)), len(u.get("concepts") or [])))
        if not U.unit_questions(u):
            p["units_no_questions"] += 1
        for cd in u.get("concepts") or []:
            if not (cd.get("questions") or []):
                gaps[c].append(f"{u['id']}/{cd['id']}")

    print(f"{'course':<24}{'units':>6}{'qs':>7}{'concepts':>10}{'seen':>6}"
          f"{'askable':>9}{'no qs':>7}")
    for c in sorted(per):
        p = per[c]
        print(f"{c:<24}{p['units']:>6}{p['questions']:>7}{p['concepts']:>10}{p['seen']:>6}"
              f"{p['units_askable']:>9}{p['units_no_questions']:>7}")
    print("\nstage:")
    for c in sorted(per):
        p = per[c]
        print(f"  {c:<24}" + "  ".join(f"{s}:{p[s]}" for s in U.STAGES if p[s]))

    print(f"\n{len(dry)} unit(s) have material but nothing fair to ask yet.")
    if args.units:
        for key, nq, nc in dry:
            print(f"  {key:<44} {nq:>4} questions, {nc:>3} concepts, "
                  f"{'no question' if not nq else 'concepts unseen'}")

    total_gaps = sum(len(v) for v in gaps.values())
    print(f"\n{total_gaps} concept(s) that no bank question reaches:")
    for c in sorted(gaps):
        print(f"  {c:<24} {len(gaps[c])}")
    if args.gaps:
        for c in sorted(gaps):
            for g in gaps[c]:
                print(f"    {c}:{g}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
