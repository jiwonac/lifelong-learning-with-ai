#!/usr/bin/env python3
"""Scatter newly added notes at random positions through the Vault deck's new-card queue.

Anki introduces new cards in position order, which is add order by default, so cards from a work
paper would otherwise wait behind every card already queued. This gives each card a random slot in
the queue and keeps the order they were added in, so a paper's definition cards still come before
the cards that use them. The relative order of the cards already queued is unchanged.

The anki MCP server has no reposition tool, so this talks to AnkiConnect directly.

    python3 scripts/anki_mix.py 1791225560218 1791225560224 ...   # note ids, in add order
    python3 scripts/anki_mix.py --dry-run <note ids>
"""

import argparse
import json
import os
import random
import sys
import urllib.request

DECK = "Vault"
URL = os.environ.get("ANKI_CONNECT_URL", "http://localhost:8765")


def anki(action, **params):
    body = json.dumps({"action": action, "version": 6, "params": params}).encode()
    with urllib.request.urlopen(urllib.request.Request(URL, body), timeout=30) as resp:
        out = json.load(resp)
    if out["error"]:
        sys.exit(f"AnkiConnect {action}: {out['error']}")
    return out["result"]


def new_cards(query):
    """(due, card id) of the new cards matching query, in queue order."""
    ids = anki("findCards", query=f"deck:{DECK} is:new {query}")
    return sorted((c["due"], c["cardId"]) for c in anki("cardsInfo", cards=ids)) if ids else []


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("notes", nargs="+", type=int, help="note ids, in the order they were added")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", type=int)
    args = ap.parse_args()

    nids = ",".join(map(str, args.notes))
    mine = new_cards(f"nid:{nids}")
    queue = [due for due, _ in new_cards(f"-nid:{nids}")]
    if not mine:
        sys.exit("none of those notes has a new card in the Vault deck")
    if not queue:
        print("queue is otherwise empty; nothing to mix into")
        return

    # A slot i means "just after the i-th queued card"; equal positions tie-break by card id,
    # and these cards are the newest, so they land after the card they share a position with.
    rng = random.Random(args.seed)
    slots = sorted(rng.randint(0, len(queue)) for _ in mine)
    for (_, cid), slot in zip(mine, slots):
        due = queue[0] - 1 if slot == 0 else queue[slot - 1]
        print(f"card {cid}: position {due} (after {slot} of {len(queue)} queued)")
        if not args.dry_run:
            anki("setSpecificValueOfCard", card=cid, keys=["due"], newValues=[due])


if __name__ == "__main__":
    main()
