#!/usr/bin/env python3
"""Put every note in the Vault deck into the subdeck its kind belongs in.

    Vault::Courses::<course title>   cards from course sessions, and plain-fact definitions
                                     carded from a paper that a course concept covers
    Vault::Papers                    every claim attributed to a work paper
    Vault::Ad hoc                    ad-hoc session cards with no unit (topic and report tags)

Subdecks exist so each kind of card can get its own deck options (new cards per day, desired
retention). The tags stay as they are: they route leeches and drive cleanup, and the deck only
decides scheduling. The rule for a card that could sit in more than one deck:

  1. A paper's claim (its front names the paper in a `ttl` span) goes to Papers, even when a
     course concept tag is also on it.
  2. Any other card with a course tag goes to that course. When it has two, the course of its
     `vault::concept::` tag wins, because the concept is the narrower claim.
  3. Any other card with a paper tag goes to Papers.
  4. A card with only `vault::topic::` or `vault::report::` tags goes to Ad hoc.

The anki MCP server cannot set deck options, so this talks to AnkiConnect directly. A subdeck it
creates gets the parent Vault deck's options preset, so moving a card changes nothing about how it
is scheduled until the learner gives that subdeck its own preset.

    python3 scripts/anki_decks.py              # report what would move
    python3 scripts/anki_decks.py --apply      # move it
"""

import argparse
import json
import os
import sys
import urllib.request
from collections import Counter, defaultdict
from pathlib import Path

ROOT = "Vault"
PAPERS = f"{ROOT}::Papers"
ADHOC = f"{ROOT}::Ad hoc"
URL = os.environ.get("ANKI_CONNECT_URL", "http://localhost:8765")
COURSES = Path(__file__).resolve().parent.parent / "courses"


def anki(action, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, body), timeout=60) as resp:
        out = json.load(resp)
    if out["error"]:
        sys.exit(f"AnkiConnect {action}: {out['error']}")
    return out["result"]


def course_decks():
    """Course slug -> its deck, named by the course `title` in units.json. Archived courses are
    included so a card from one still has a deck to go to."""
    out = {}
    for f in sorted(COURSES.glob("*/units.json")) + sorted(COURSES.glob("_archive/*/units.json")):
        doc = json.loads(f.read_text())
        out.setdefault(doc["course"], f"{ROOT}::Courses::{doc['title']}")
    return out


def prefix_map():
    """Course slug -> the id prefixes its units use (`calc`, `db`, ...)."""
    out = defaultdict(set)
    for f in list(COURSES.glob("*/units.json")) + list(COURSES.glob("_archive/*/units.json")):
        doc = json.loads(f.read_text())
        for u in doc.get("units", []):
            out[doc["course"]].add(u["id"].split("-")[0])
    return out


def concept_course(concept, prefixes):
    """The course a concept id belongs to, read off its prefix, or None if that is ambiguous."""
    hits = [slug for slug, ps in prefixes.items() if concept.split("-")[0] in ps]
    return hits[0] if len(hits) == 1 else None


def target(note, decks, prefixes):
    """The deck a note belongs in, or None when its tags give no rule."""
    tags = note["tags"]
    fields = note["fields"]
    front = (fields.get("Front") or fields.get("Text") or {"value": ""})["value"]
    paper = any(t.startswith("vault::paper::") for t in tags)
    courses = sorted({t.split("::")[1] for t in tags
                      if t.startswith("vault::") and t.split("::")[1] in decks})
    if paper and 'class="ttl"' in front:
        return PAPERS
    if len(courses) > 1:
        concepts = [t.split("::", 2)[2] for t in tags if t.startswith("vault::concept::")]
        owners = {concept_course(c, prefixes) for c in concepts} & set(courses)
        courses = sorted(owners) if len(owners) == 1 else courses
    if courses:
        return decks[courses[0]]
    if paper:
        return PAPERS
    if any(t.startswith(("vault::topic::", "vault::report::")) for t in tags):
        return ADHOC
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--apply", action="store_true", help="move the cards (default: report only)")
    args = ap.parse_args()

    decks, prefixes = course_decks(), prefix_map()
    nids = anki("findNotes", query=f'"deck:{ROOT}"')
    notes = []
    for i in range(0, len(nids), 200):
        notes += anki("notesInfo", notes=nids[i:i + 200])
    # Batched, like notesInfo: one large response has left AnkiConnect on Windows holding a dead
    # socket, which it then reports as WinError 10022 on every poll until Anki restarts.
    cids = [c for n in notes for c in n["cards"]]
    deck_of = {}
    for i in range(0, len(cids), 200):
        deck_of.update({c["cardId"]: c["deckName"] for c in anki("cardsInfo", cards=cids[i:i + 200])})

    moves, unrouted, where = defaultdict(list), [], Counter()
    for n in notes:
        dest = target(n, decks, prefixes)
        if dest is None:
            unrouted.append(n["noteId"])
            continue
        where[dest] += 1
        moves[dest] += [c for c in n["cards"] if deck_of.get(c) != dest]

    for dest in sorted(where):
        print(f"{dest:<52} {where[dest]:>4} notes, {len(moves[dest]):>4} cards to move")
    if unrouted:
        print(f"no rule for {len(unrouted)} notes (left in place): {unrouted[:10]}")
    if not args.apply:
        return

    root_conf = anki("getDeckConfig", deck=ROOT)["id"]
    existing = set(anki("deckNames"))
    for dest in sorted(where):
        if dest not in existing:
            anki("createDeck", deck=dest)
            # A parent created on the way (Vault::Courses) needs the preset too.
            parts = dest.split("::")
            new = ["::".join(parts[:i]) for i in range(2, len(parts) + 1)]
            anki("setDeckConfigId", decks=[d for d in new if d not in existing], configId=root_conf)
            existing.update(new)
        if moves[dest]:
            anki("changeDeck", cards=moves[dest], deck=dest)
    print("moved")


if __name__ == "__main__":
    main()
