#!/usr/bin/env python3
"""Candidate words for the vocabulary deck, from word lists to the sorting page and back.

    vocabulary/sources/*.txt   public word lists (SAT, GRE, word-of-the-day archives), one word a line
    vocabulary/pool.json       every candidate: its most common form, Zipf frequency, and lists
    vocabulary/words.json      every word the learner has sorted, with its verdict
    vocabulary/batches/*.json  each batch as shown on the sorting page, definitions included
    vocabulary/sort.html       the sorting page (an artifact); `page` loads a batch into it

Subcommands:

    python3 scripts/vocab.py pool                  # rebuild pool.json (needs `pip install wordfreq`)
    python3 scripts/vocab.py next 100              # the next 100 unsorted words in the band, as JSON
    python3 scripts/vocab.py page <batch.json>     # put a batch into sort.html
    python3 scripts/vocab.py ingest <verdicts.json>  # merge the page's verdicts into words.json

A batch file is a JSON list of {w, p, d, z}: headword, part of speech, short definition, Zipf.
The agent writes `p` and `d`. A verdicts file is the `verdicts` collection of the sorting page's
store, as ArtifactData returns it: a list of {word, verdict, batch, at}, or that list wrapped
in documents with a `data` field.

The band is Zipf 1.9 to 3.2 on the most common form (`--lo`, `--hi`). Zipf is log10 of
occurrences per billion words, so 3 is once per million. Words at the target level (capricious
2.79, sanguine 2.74, flummoxed 2.08) sit inside it and vouchsafe (1.73) sits below.
Words on more lists come first, because several lists agreeing is the best sign a word is
worth knowing.
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

VOCAB = Path(__file__).resolve().parent.parent / "vocabulary"
SOURCES, POOL, WORDS = VOCAB / "sources", VOCAB / "pool.json", VOCAB / "words.json"
PAGE = VOCAB / "sort.html"
VERDICTS = ("new-add", "new-skip", "known-add", "known-skip")


def forms(w):
    """The word and its participles, so `flummox` can be carded as `flummoxed`. Plurals are
    left out: a noun is carded in the singular even when the plural is more common."""
    out = {w, w + "ed", w + "d", w + "ing"}
    if w.endswith("e"):
        out |= {w[:-1] + "ing"}
    if w.endswith("y"):
        out |= {w[:-1] + "ied"}
    return out


def build_pool(_):
    try:
        from wordfreq import zipf_frequency
    except ImportError:
        sys.exit("pool needs wordfreq: pip install wordfreq")
    lists = {}
    for f in sorted(SOURCES.glob("*.txt")):
        for line in f.read_text().splitlines():
            w = line.strip().lower()
            if re.fullmatch(r"[a-z][a-z-]*[a-z]", w):
                lists.setdefault(w, set()).add(f.stem)
    pool = []
    for w, src in sorted(lists.items()):
        # An inflection only wins when it is clearly more common, so `sanguine` never becomes
        # `sanguines`. A form that is itself a list entry is left to that entry.
        best, bz = w, zipf_frequency(w, "en")
        for f in sorted(forms(w) - {w}):
            z = zipf_frequency(f, "en")
            if z > bz + 0.3 and f not in lists:
                best, bz = f, z
        pool.append({"w": best, "base": w, "z": round(bz, 2), "lists": sorted(src)})
    POOL.write_text(json.dumps(pool, indent=1) + "\n")
    print(f"{len(pool)} words from {len(list(SOURCES.glob('*.txt')))} lists -> {POOL.name}")


def load_words():
    return json.loads(WORDS.read_text()) if WORDS.exists() else {}


def next_batch(args):
    pool, seen = json.loads(POOL.read_text()), load_words()
    batched = set()
    for f in (VOCAB / "batches").glob("*.json"):
        batched |= {e["w"] for e in json.loads(f.read_text())}
    out = [e for e in pool
           if args.lo <= e["z"] <= args.hi and e["w"] not in seen and e["base"] not in seen
           and e["w"] not in batched]
    out.sort(key=lambda e: (-len(e["lists"]), -e["z"], e["w"]))
    json.dump([{"w": e["w"], "z": e["z"]} for e in out[:args.n]], sys.stdout, indent=1)
    print(f"\n{len(out)} unsorted words in band", file=sys.stderr)


def page(args):
    batch = json.loads(Path(args.batch).read_text())
    html = PAGE.read_text()
    html = re.sub(r"^const BATCH = .*;$", lambda _: "const BATCH = " + json.dumps(batch) + ";",
                  html, count=1, flags=re.M)
    html = re.sub(r'^const BATCH_ID = ".*";$', lambda _: f'const BATCH_ID = "{Path(args.batch).stem}";',
                  html, count=1, flags=re.M)
    PAGE.write_text(html)
    print(f"{len(batch)} words -> {PAGE.name}")


def ingest(args):
    raw = json.loads(Path(args.verdicts).read_text())
    if isinstance(raw, dict):
        raw = raw.get("docs") or raw.get("documents") or list(raw.values())
    words, n = load_words(), 0
    for d in raw:
        d = d.get("data", d)
        if d.get("verdict") not in VERDICTS:
            continue
        rec = words.setdefault(d["word"], {})
        if rec.get("verdict") != d["verdict"]:
            n += 1
        rec.update(verdict=d["verdict"], batch=d.get("batch", ""),
                   sorted=(d.get("at") or date.today().isoformat())[:10])
    WORDS.write_text(json.dumps(dict(sorted(words.items())), indent=1) + "\n")
    adds = [w for w, r in words.items() if r["verdict"].endswith("-add") and "note" not in r]
    print(f"{n} verdicts merged; {len(words)} words sorted; {len(adds)} to card")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("pool").set_defaults(fn=build_pool)
    p = sub.add_parser("next")
    p.add_argument("n", type=int)
    p.add_argument("--lo", type=float, default=1.9)
    p.add_argument("--hi", type=float, default=3.2)
    p.set_defaults(fn=next_batch)
    p = sub.add_parser("page")
    p.add_argument("batch")
    p.set_defaults(fn=page)
    p = sub.add_parser("ingest")
    p.add_argument("verdicts")
    p.set_defaults(fn=ingest)
    args = ap.parse_args()
    args.fn(args)


if __name__ == "__main__":
    main()
