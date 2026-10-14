#!/usr/bin/env python3
"""
Read the front matter of explain-session records, `sessions/<YYYY-MM-DD-HHMM>-explain-<slug>.md`.

An explain session teaches the gaps in one document or task the learner brought (a paper, an
autoresearch report, a project question) and schedules nothing. Two questions about those records
need an answer across all of them, and this script gives it:

    python3 scripts/explain.py open      # sessions stopped part-way, with their cursor
    python3 scripts/explain.py topics    # every topic, how many sessions taught it, and where

A topic taught in two or more sessions is a candidate for a home in `units.json`: a concept on an
existing unit, or a new unit. The script only counts. Whether the topic deserves a unit is the
agent's call, made with the learner (see skills/explain/SKILL.md -> "Promotion").

Front matter is a small fixed format, parsed here rather than with a YAML library:

    ---
    kind: explain
    title: Product quantization in the FAISS report
    source_kind: report            # paper | report | project | other
    source: https://raindrop.io/... (or a vault path, or a one-line project description)
    topics: [product-quantization, inverted-file-index]
    status: open                   # open | done
    cursor: inverted-file-index — PQ codes done; IVF probing next
    ---
"""
import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
SESSIONS = VAULT / "sessions"

NAME = re.compile(r"^\d{4}-\d{2}-\d{2}-\d{4}-explain-[a-z0-9-]+\.md$")
TOPIC = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
REQUIRED = ("kind", "title", "source_kind", "source", "topics", "status")
SOURCE_KINDS = ("paper", "report", "project", "other")
STATUSES = ("open", "done")


def front_matter(path):
    """The `key: value` pairs between the opening `---` lines, or None if there are none.
    `topics` becomes a list."""
    lines = path.read_text().splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    meta = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" not in line:
            continue
        key, val = line.split(":", 1)
        val = re.sub(r"\s+#.*$", "", val).strip()
        meta[key.strip()] = val
    else:
        return None
    t = meta.get("topics", "").strip()
    meta["topics"] = [x.strip() for x in t.strip("[]").split(",") if x.strip()] if t else []
    return meta


def records(sessions=SESSIONS):
    """(path, meta) for every explain-session file, meta None when the front matter is absent."""
    return [(p, front_matter(p)) for p in sorted(sessions.glob("*-explain-*.md"))]


def problems(path, meta):
    """What is wrong with one record, as a list of messages. check_vault.py reports these."""
    out = []
    if not NAME.match(path.name):
        out.append("filename must be <YYYY-MM-DD-HHMM>-explain-<slug>.md")
    if meta is None:
        return out + ["no front matter"]
    out += [f"front matter missing '{k}'" for k in REQUIRED if k not in meta]
    if meta.get("kind", "explain") != "explain":
        out.append("kind must be 'explain'")
    if meta.get("source_kind", "other") not in SOURCE_KINDS:
        out.append(f"source_kind must be one of {', '.join(SOURCE_KINDS)}")
    if meta.get("status", "done") not in STATUSES:
        out.append("status must be 'open' or 'done'")
    if meta.get("status") == "open" and not meta.get("cursor"):
        out.append("an open session needs a cursor")
    out += [f"topic '{t}' is not kebab-case" for t in meta.get("topics", []) if not TOPIC.match(t)]
    return out


def cmd_open(recs):
    rows = [(p, m) for p, m in recs if m and m.get("status") == "open"]
    if not rows:
        print("No open explain sessions.")
    for p, m in rows:
        print(f"{p.name}\n  {m.get('title', '?')}\n  cursor: {m.get('cursor', '?')}")


def cmd_topics(recs):
    where = defaultdict(list)
    for p, m in recs:
        for t in (m or {}).get("topics", []):
            where[t].append(p.name[:10])
    if not where:
        print("No topics recorded yet.")
        return
    width = max(len(t) for t in where)
    for t, dates in sorted(where.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        flag = "  <- taught more than once: look for a home" if len(dates) > 1 else ""
        print(f"{t:<{width}}  {len(dates)}  {', '.join(dates)}{flag}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[1])
    ap.add_argument("command", choices=("open", "topics"))
    args = ap.parse_args()
    recs = records()
    for p, m in recs:
        for msg in problems(p, m):
            print(f"warning: {p.name}: {msg}", file=sys.stderr)
    {"open": cmd_open, "topics": cmd_topics}[args.command](recs)


if __name__ == "__main__":
    main()
