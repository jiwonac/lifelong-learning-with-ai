#!/usr/bin/env python3
"""
Archive or restore a course: move it under courses/_archive/ (or back), repointing every
source_ref that names its old path in the same operation.

Archiving is a move, not a delete -- the bank stays intact because its questions are still
referenced from sessions/ and from the unit that owns each one; a moved course is still fully
discoverable by check_vault.py, just excluded from scheduling. See SCHEMA.md and
check_vault.py's course_dirs(): location under courses/_archive/ is what makes a course archived,
nothing in the data itself. Priority becomes moot the moment a course is archived --
scripts/units.py only loads live courses, so nothing needs to change there.

A course in the current architecture is units.json + bank.jsonl + sources/, no COURSE.md and no
map.md -- the whole directory moves as one atomic git operation, and every source_ref inside
bank.jsonl naming a real vault path under the old location is rewritten to the new one in the
same step, so nothing is left pointing at a path that no longer exists.

Usage:
    python3 scripts/archive_course.py archive <slug>
    python3 scripts/archive_course.py restore <slug>
"""
import argparse, json, re, subprocess, sys
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SRC_PATH = re.compile(r"^((?:sources|courses)/[^#]*?\.(?:pdf|md|txt|epub|json))", re.I)


def git_mv(src, dst):
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "mv", str(src), str(dst)], cwd=VAULT, check=True)


def repoint_bank(bank_path, old_prefix, new_prefix):
    """Rewrite every source_ref in bank_path that names a real path under old_prefix."""
    if not bank_path.exists():
        return 0
    lines, n = bank_path.read_text().splitlines(), 0
    out = []
    for line in lines:
        if not line.strip():
            continue
        q = json.loads(line)
        sr = str(q.get("source_ref", ""))
        m = SRC_PATH.match(sr)
        if m and m.group(1).startswith(old_prefix + "/"):
            q["source_ref"] = new_prefix + sr[len(old_prefix):]
            n += 1
        out.append(json.dumps(q, ensure_ascii=False))
    bank_path.write_text("\n".join(out) + "\n")
    return n


def move(slug, forward):
    src = (VAULT / "courses" / slug) if forward else (VAULT / "courses" / "_archive" / slug)
    dst = (VAULT / "courses" / "_archive" / slug) if forward else (VAULT / "courses" / slug)
    if not src.is_dir():
        print(f"no courses/{'_archive/' if not forward else ''}{slug}/ to move"); return 1
    if dst.exists():
        print(f"{dst.relative_to(VAULT)} already exists -- aborting"); return 1

    old_prefix = f"courses/{slug}"
    new_prefix = f"courses/_archive/{slug}" if forward else f"courses/{slug}"

    git_mv(src, dst)
    n = repoint_bank(dst / "bank.jsonl", old_prefix, new_prefix)

    verb = "Archived" if forward else "Restored"
    print(f"{verb} {slug}: {src.relative_to(VAULT)}/ -> {dst.relative_to(VAULT)}/, "
          f"repointed {n} source_ref(s)")
    print("Run `git add -A && python3 scripts/check_vault.py` to confirm zero errors before "
          "committing.")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["archive", "restore"])
    ap.add_argument("slug")
    args = ap.parse_args()
    return move(args.slug, forward=(args.action == "archive"))


if __name__ == "__main__":
    sys.exit(main())
