#!/usr/bin/env python3
"""
Vault integrity checker.

Run before and after every migration phase. The point is that a phase which breaks a
cross-reference gets caught immediately, not three phases later when it's hard to attribute.

Layout-agnostic on purpose: it discovers banks and maps under both the legacy layout
(question_banks/, maps/) and the course layout (courses/<slug>/), so it keeps working
throughout the migration rather than needing to be rewritten mid-flight.

Source-ref strictness escalates automatically as the migration proceeds: non-canonical
source_ref values are warnings for an unmigrated topic, but errors for any course that has
units.json or declares `refs: canonical` in COURSE.md. --strict-refs applies that bar
everywhere and is the Phase 6 exit gate. Archived courses stay exempt.

ERROR = a broken cross-reference or malformed record. Fails the run (exit 1).
WARN  = a data-quality problem that doesn't break anything today but will make the course
        migration harder. Reported, does not fail.

Usage:
    python scripts/check_vault.py [--vault .] [--warnings] [--quiet]
"""
import argparse
import json
import re
import sys
from pathlib import Path
from collections import Counter, defaultdict

REQUIRED_FIELDS = ["id", "course", "type", "question",
                   "answer_key", "source_ref", "date_generated"]
QID = re.compile(r"[a-z_]+-\d{6}")
# A source_ref locator is "<path to a real file><anything>". Section info is appended with
# '#', ', ' or plain space depending on which generation run produced the entry, so pull the
# path off by extension rather than by separator.
SRC_PATH = re.compile(r"^((?:sources|courses)/[^#]*?\.(?:pdf|md|txt|epub|json))", re.I)


class Report:
    def __init__(self):
        self.errors, self.warns = [], []
        self.counts = Counter()

    def error(self, where, msg):
        self.errors.append((where, msg))
        self.counts[f"E:{where}"] += 1

    def warn(self, where, msg):
        self.warns.append((where, msg))
        self.counts[f"W:{where}"] += 1


def load_jsonl(path, rep):
    items = []
    for n, line in enumerate(path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError as e:
            rep.error("bank-parse", f"{path}:{n} not valid JSON — {e}")
    return items


def course_dirs(vault):
    """Every course directory, live or archived, with its archived flag.

    Location is authoritative: anything under courses/_archive/ is archived regardless of what
    its COURSE.md says. Archived courses stay fully discoverable -- their banks are still
    referenced by session_log.jsonl and by past test documents, so dropping them from discovery
    would break those joins. They are excluded from scheduling and from source_ref strictness,
    not from existence.
    """
    out = []
    for d in sorted((vault / "courses").glob("*/")):
        if d.name == "_archive":
            continue
        out.append((d.name, d, False))
    for d in sorted((vault / "courses" / "_archive").glob("*/")):
        out.append((d.name, d, True))
    return out


def course_meta(vault, name):
    """Read a course's COURSE.md for the fields that change how strictly we check it.

    `refs: canonical` is a latch: once a course declares its source_refs normalized, any
    regression becomes an error rather than a warning. A course with units.json is held to
    the same bar whether or not it declares it -- unit mapping joins on real paths, so prose
    citations there are a broken join waiting to happen, not a style preference.
    """
    meta = {"tier": None, "refs": "legacy", "planned": False}
    d = vault / "courses" / name
    if not d.is_dir():
        d = vault / "courses" / "_archive" / name
        if not d.is_dir():
            return meta
        meta["tier"] = "archived"
    meta["planned"] = (d / "units.json").exists()
    cf = d / "COURSE.md"
    if cf.exists():
        text = cf.read_text()
        for key in ("tier", "refs"):
            m = re.search(rf"^\s*[-*]?\s*{key}\s*:\s*(\S+)", text, re.M | re.I)
            if m:
                meta[key] = m.group(1).strip().strip("`\"'").lower()
    if (vault / "courses" / "_archive" / name).is_dir():
        meta["tier"] = "archived"   # location wins over the file
    return meta


def find_banks(vault):
    """Course banks (live and archived), plus any legacy question_banks/<topic>.jsonl."""
    banks = {}
    for p in sorted((vault / "question_banks").glob("*.jsonl")):
        banks[p.stem] = p
    for name, d, _ in course_dirs(vault):
        if (d / "bank.jsonl").exists():
            banks[name] = d / "bank.jsonl"
    return banks



def check_banks(vault, banks, rep, strict_refs=False):
    questions, seen = {}, {}
    for name, path in banks.items():
        meta = course_meta(vault, name)
        # Archived courses are exempt: normalizing material you have shelved is wasted work.
        strict = strict_refs or (
            meta["tier"] != "archived" and (meta["refs"] == "canonical" or meta["planned"])
        )
        ref_issue = rep.error if strict else rep.warn
        for q in load_jsonl(path, rep):
            qid = q.get("id")
            if not qid:
                rep.error("bank-field", f"{path}: entry with no id — {str(q)[:90]}")
                continue
            if qid in seen:
                rep.error("bank-dup-id", f"{qid} appears in both {seen[qid]} and {path}")
                continue
            seen[qid] = path
            questions[qid] = q

            missing = [f for f in REQUIRED_FIELDS if f not in q]
            if missing:
                rep.error("bank-field", f"{qid} missing required field(s): {', '.join(missing)}")
            if not str(q.get("answer_key", "")).strip():
                rep.error("bank-field", f"{qid} has an empty answer_key")
            # The ID prefix is what session_log and the maps join on, so a mismatch between
            # it and the file it lives in is a real hazard, not a cosmetic one.
            prefix = qid.rsplit("-", 1)[0]
            if prefix != name and q.get("course") != name:
                rep.error("bank-id-prefix",
                          f"{qid} lives in {path.name} but its prefix is '{prefix}'")

            sr = str(q.get("source_ref", "")).strip()
            m = SRC_PATH.match(sr)
            if m:
                if not (vault / m.group(1)).exists():
                    rep.error("source-missing", f"{qid} → {m.group(1)} does not exist")
                elif "#" not in sr:
                    ref_issue("source-format",
                              f"{qid} locator not '#'-delimited: {sr[:80]}")
            elif sr.startswith(("sources/", "courses/")):
                rep.error("source-missing", f"{qid} → unparseable vault path: {sr[:80]}")
            elif sr:
                ref_issue("source-prose",
                          f"{qid} prose citation, not a vault path: {sr[:70]}")
    return questions




VALID_CONCEPT_STATES = {"unknown", "unseen", "seen"}
READING_STATUS = {"present", "missing"}
UNIT_CONCEPTS_WARN = 25    # CLAUDE.md: a unit is 1-4 hours to cover once, ~6-20 concepts
UNIT_CONCEPTS_ERROR = 35


def check_units(vault, questions, rep):
    """units.json per course — the vault's one scheduled object. See CLAUDE.md."""
    all_units, prereq_refs = {}, {}
    for cname, _d, archived in course_dirs(vault):
        uf = _d / "units.json"
        if not uf.exists():
            if not archived and (_d / "bank.jsonl").exists():
                rep.warn("units-missing", f"courses/{cname}/ has a bank but no units.json — "
                         "nothing in it can be scheduled or quizzed")
            continue
        try:
            doc = json.loads(uf.read_text())
        except json.JSONDecodeError as e:
            rep.error("units-parse", f"{uf}: {e}")
            continue
        for key in ("course", "title", "default_priority", "units"):
            if key not in doc:
                rep.error("units-header", f"{uf}: missing top-level '{key}'")
        if doc.get("course") not in (None, cname):
            rep.error("units-header",
                      f"{uf}: declares course '{doc['course']}' but lives in courses/{cname}/")
        dp = doc.get("default_priority")
        if not isinstance(dp, int) or dp < 0:
            rep.error("units-header", f"{uf}: default_priority must be a non-negative integer")
        sh = doc.get("share")
        if sh is None and not archived:
            # Archived courses are excluded from scheduling entirely, so a missing share there
            # says nothing.
            rep.warn("course-share",
                     f"{uf}: no 'share' — the study draw falls back to default_priority for this "
                     f"course, which makes its frequency depend on how many units it has")
        elif sh is not None and (not isinstance(sh, int) or sh < 0):
            rep.error("units-header", f"{uf}: share must be a non-negative integer")

        all_concepts, concept_pre, mapped_here = {}, {}, set()
        for u in doc.get("units", []):
            uid = u.get("id")
            if not uid:
                rep.error("unit-id", f"{uf}: a unit has no id")
                continue
            qual = f"{cname}:{uid}"
            if qual in all_units:
                rep.error("unit-id", f"{uf}: duplicate unit id '{uid}'")
            all_units[qual] = u
            prereq_refs[qual] = u.get("prereqs", [])

            where = f"{cname}:{uid}"
            r = u.get("reading") or {}
            if r.get("status") not in READING_STATUS:
                rep.error("unit-reading",
                          f"{where}: reading.status '{r.get('status')}' not in {READING_STATUS}")
            if u.get("priority") is not None and (
                    not isinstance(u["priority"], int) or u["priority"] < 0):
                rep.error("unit-priority", f"{where}: priority must be a non-negative integer")

            srs = u.get("srs") or {}
            for f in ("last_seen", "reps", "lapses", "difficulty", "stability"):
                if f not in srs:
                    rep.error("unit-srs", f"{where}: srs missing '{f}'")
            if srs.get("reps", 0) and not srs.get("last_seen"):
                rep.error("unit-srs", f"{where}: reps={srs['reps']} but no last_seen")
            if srs.get("last_seen") and not u.get("placed"):
                rep.error("unit-srs", f"{where}: has been reviewed but was never placed")
            d, st = srs.get("difficulty"), srs.get("stability")
            if isinstance(d, (int, float)) and not 1.0 <= d <= 10.0:
                rep.error("unit-srs", f"{where}: difficulty {d} outside [1, 10]")
            if isinstance(st, (int, float)) and st < 0:
                rep.error("unit-srs", f"{where}: stability {st} is negative")
            if srs.get("lapses", 0) > srs.get("reps", 0):
                rep.error("unit-srs", f"{where}: {srs['lapses']} lapses in {srs['reps']} reps")

            cids = []
            for c in u.get("concepts") or []:
                cid = c.get("id")
                cids.append(cid)
                if c.get("state") not in VALID_CONCEPT_STATES:
                    rep.error("unit-concept-state",
                              f"{where}: concept '{cid}' state '{c.get('state')}' invalid")
                if c.get("kind") not in ("claim", "skill"):
                    rep.error("unit-concept",
                              f"{where}: concept '{cid}' kind '{c.get('kind')}' is not "
                              "claim or skill")
                if not str(c.get("claim", "")).strip():
                    rep.error("unit-concept", f"{where}: concept '{cid}' has no claim text")
                for qid in c.get("questions") or []:
                    if qid not in questions:
                        rep.error("unit-bank",
                                  f"{where}: concept '{cid}' cites unknown question {qid}")
                if cid in all_concepts:
                    rep.error("unit-concept",
                              f"courses/{cname}: concept '{cid}' appears in two units")
                all_concepts[cid] = uid
                concept_pre[cid] = c.get("prereqs") or []
                mapped_here.add(cid)
            if len(cids) != len(set(cids)):
                rep.error("unit-concept", f"{where}: repeats a concept id")
            if len(cids) > UNIT_CONCEPTS_ERROR:
                rep.error("unit-size", f"{where}: {len(cids)} concepts — far past the "
                          f"1-4 hour unit size; split it (CLAUDE.md)")
            elif len(cids) > UNIT_CONCEPTS_WARN:
                rep.warn("unit-size", f"{where}: {len(cids)} concepts — above the "
                         f"{UNIT_CONCEPTS_WARN} that fits a 1-4 hour unit; consider splitting")

            cur = u.get("cursor") or {}
            if cur.get("concept") and cids and cur["concept"] not in cids:
                rep.error("unit-cursor",
                          f"{where}: cursor points at '{cur['concept']}', not one of its concepts")

            for qid in u.get("questions", []):
                if qid not in questions:
                    rep.error("unit-bank", f"{where}: cites unknown question {qid}")

            for e in u.get("log", []):
                if "date" not in e or "what" not in e:
                    rep.error("unit-log", f"{where}: log entry needs 'date' and 'what'")

        # Concept prerequisites resolve within the course, and the concept graph is acyclic.
        for cid, pres in concept_pre.items():
            for pre in pres:
                if pre not in all_concepts:
                    rep.error("concept-prereq",
                              f"courses/{cname}: concept '{cid}' prereq '{pre}' does not resolve")
        ccol = {}

        def cvisit(n, path):
            ccol[n] = 1
            for q in concept_pre.get(n, []):
                if q not in concept_pre:
                    continue
                if ccol.get(q) == 1:
                    rep.error("concept-cycle",
                              f"courses/{cname}: concept cycle {' -> '.join(path + [n, q])}")
                elif ccol.get(q, 0) == 0:
                    cvisit(q, path + [n])
            ccol[n] = 2

        for n in concept_pre:
            if ccol.get(n, 0) == 0:
                cvisit(n, [])

    # Prerequisites resolve, and the unit graph is acyclic.
    for qual, refs in prereq_refs.items():
        owner = qual.split(":", 1)[0]
        for ref in refs:
            key = ref if ":" in ref else f"{owner}:{ref}"
            if key not in all_units:
                rep.error("unit-prereq", f"{qual}: prereq '{ref}' does not resolve")
    colour = {}

    def visit(n, path):
        colour[n] = 1
        for ref in prereq_refs.get(n, []):
            owner = n.split(":", 1)[0]
            k = ref if ":" in ref else f"{owner}:{ref}"
            if k not in prereq_refs:
                continue
            if colour.get(k) == 1:
                rep.error("unit-cycle", f"prerequisite cycle: {' -> '.join(path + [n, k])}")
            elif colour.get(k, 0) == 0:
                visit(k, path + [n])
        colour[n] = 2

    for n in prereq_refs:
        if colour.get(n, 0) == 0:
            visit(n, [])
    return all_units






def check_adhoc(vault, rep):
    """Ad-hoc session records carry front matter that `scripts/adhoc.py` reads to list open
    sessions and count topics. A malformed one drops out of both, so it is an error."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import adhoc
    for path, meta in adhoc.records(vault / "sessions"):
        for msg in adhoc.problems(path, meta):
            rep.error("adhoc-session", f"sessions/{path.name}: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vault", default=".")
    ap.add_argument("--warnings", action="store_true", help="List individual warnings")
    ap.add_argument("--quiet", action="store_true", help="Summary only")
    ap.add_argument("--strict-refs", action="store_true",
                    help="Treat every non-canonical source_ref as an error, everywhere. "
                         "This is the Phase 6 exit gate.")
    args = ap.parse_args()

    vault = Path(args.vault)
    rep = Report()

    banks = find_banks(vault)
    if not banks:
        print("No question banks found — is --vault pointing at the vault root?")
        return 1
    questions = check_banks(vault, banks, rep, strict_refs=args.strict_refs)
    units = check_units(vault, questions, rep)
    check_adhoc(vault, rep)

    print(f"vault: {vault.resolve()}")
    cds = course_dirs(vault)
    ncourses = sum(1 for _, _, a in cds if not a)
    narch = sum(1 for _, _, a in cds if a)
    print(f"banks: {len(banks)}   questions: {len(questions)}   "
          f"courses: {ncourses} (+{narch} archived)   "
          f"units: {len(units)}")

    if not args.quiet:
        for where, msg in rep.errors[:40]:
            print(f"  ERROR [{where}] {msg}")
        if len(rep.errors) > 40:
            print(f"  ... {len(rep.errors) - 40} more errors")
        if args.warnings:
            for where, msg in rep.warns[:40]:
                print(f"  WARN  [{where}] {msg}")
            if len(rep.warns) > 40:
                print(f"  ... {len(rep.warns) - 40} more warnings")

    by_kind = defaultdict(int)
    for k, v in rep.counts.items():
        by_kind[k] = v
    if by_kind:
        print("\nby check:")
        for k in sorted(by_kind):
            print(f"  {k:<24} {by_kind[k]}")

    print(f"\n{len(rep.errors)} error(s), {len(rep.warns)} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
