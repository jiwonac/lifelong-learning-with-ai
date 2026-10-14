#!/usr/bin/env python3
"""
Record a review's outcome against a unit. Called at capture time, so the SRS numbers are never
hand-edited.

    python3 scripts/review.py example:ex-binary-search pass
    python3 scripts/review.py example:ex-binary-search fail --demote ex-bs-overflow
    python3 scripts/review.py example:ex-binary-search partial --seen ex-bs-invariant,ex-bs-log-steps \
        --cursor ex-bs-interval-conventions --note "through the step count; interval conventions next"

Grades are `fail` | `partial` | `pass` -- three, not FSRS's four, because a unit's review is
several questions and the aggregate is not a button press. `partial` means the learner got there
with a hint; `fail` means they could not get there at all. See skills/grader/SKILL.md.
"""
import argparse, sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import units as U


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("unit", help="<course>:<unit-id>")
    ap.add_argument("grade", choices=U.GRADES)
    ap.add_argument("--seen", default="", help="comma-separated concept ids to mark seen")
    ap.add_argument("--demote", default="", help="comma-separated concept ids back to unseen")
    ap.add_argument("--cursor", help="concept the sweep reached")
    ap.add_argument("--note", default="", help="human-readable position / what happened")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if ":" not in args.unit:
        print("unit must be <course>:<unit-id>"); return 1
    slug, uid = args.unit.split(":", 1)
    doc = U.load_course(slug)
    if not doc:
        print(f"no courses/{slug}/units.json"); return 1
    u = next((x for x in doc["units"] if x["id"] == uid), None)
    if u is None:
        print(f"{slug} has no unit '{uid}'"); return 1

    before = U.stage(u), dict(u.get("srs") or {})
    ids = {c["id"] for c in u.get("concepts") or []}
    seen = [c.strip() for c in args.seen.split(",") if c.strip()]
    demote = [c.strip() for c in args.demote.split(",") if c.strip()]
    for c in seen + demote + ([args.cursor] if args.cursor else []):
        if c not in ids:
            print(f"'{c}' is not a concept of {args.unit}"); return 1

    for c in u.get("concepts") or []:
        if c["id"] in seen:
            c["state"] = "seen"
        if c["id"] in demote:
            c["state"] = "unseen"

    U.review(u, args.grade)
    if args.cursor or args.note:
        u.setdefault("cursor", {})
        if args.cursor:
            u["cursor"]["concept"] = args.cursor
        if args.note:
            u["cursor"]["note"] = args.note
    what = args.note or f"{args.grade} review"
    u.setdefault("log", []).append({"date": date.today().isoformat(),
                                    "what": what, "failed": demote})

    after = U.stage(u), u["srs"]
    print(f"{args.unit}  {before[0]} -> {after[0]}")
    print(f"  difficulty {before[1].get('difficulty')} -> {after[1]['difficulty']}   "
          f"stability {before[1].get('stability')} -> {after[1]['stability']}   "
          f"reps {after[1]['reps']}  lapses {after[1]['lapses']}")
    if seen:
        print(f"  seen:    {', '.join(seen)}")
    if demote:
        print(f"  demoted: {', '.join(demote)}")
    if args.dry_run:
        print("  (dry run — nothing written)")
    else:
        U.save_course(slug, doc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
