"""Apply a pre-review pass's actions to Anki (skills/flashcards/SKILL.md -> "Pre-review").

    python3 scripts/anki_prereview_apply.py <pass dir> --dry   # validate only
    python3 scripts/anki_prereview_apply.py <pass dir>         # apply

<pass dir> holds all.json (the unseen notes, grouped) and actions*.json (the reviewers' output).
Rejected notes are suspended and tagged `rejected autopass`; rewritten and merged notes are tagged
`autopass`. applied.json records every original note, so any change can be undone by hand.
"""
import glob, json, sys, urllib.request

D = sys.argv[1]
DRY = "--dry" in sys.argv


def anki(action, **p):
    body = json.dumps({"action": action, "version": 6, "params": p}).encode()
    with urllib.request.urlopen(urllib.request.Request("http://localhost:8765", body), timeout=120) as r:
        o = json.load(r)
    if o["error"]:
        raise RuntimeError(f"{action}: {o['error']}")
    return o["result"]


orig = {n["noteId"]: n for g in json.load(open(f"{D}/all.json")).values() for n in g}
actions = []
for f in sorted(glob.glob(f"{D}/actions*.json")):
    actions += json.load(open(f))

problems, seen = [], set()
for a in actions:
    ids = a.get("ids", [])
    if not ids or any(i not in orig for i in ids) or seen & set(ids):
        problems.append(("bad ids", a)); continue
    if a["action"] in ("rewrite", "merge"):
        f, m = a.get("fields", {}), a.get("model")
        need = {"Basic": {"Front", "Back"}, "Cloze": {"Text"}}.get(m)
        if not need or not need <= set(f) or not all(f[k].strip() for k in need):
            problems.append(("bad fields", a)); continue
        if m == "Cloze" and "{{c" not in f["Text"]:
            problems.append(("cloze without deletion", a)); continue
        if 'class="src"' not in (f.get("Front") or f.get("Text")):
            problems.append(("no source line", a)); continue
        if len({orig[i]["deck"] for i in ids}) > 1:
            problems.append(("merge across decks", a)); continue
    elif a["action"] != "reject":
        problems.append(("unknown action", a)); continue
    seen |= set(ids)
    a["_ok"] = True

ok = [a for a in actions if a.get("_ok")]
count = {k: sum(a["action"] == k for a in ok) for k in ("reject", "rewrite", "merge")}
print(f"{len(actions)} actions, {len(ok)} valid, {count}; {len(problems)} problems")
for why, a in problems:
    print("  PROBLEM", why, a.get("ids"), a.get("reason", "")[:80])
if DRY:
    sys.exit()

log = []
for a in ok:
    ids = a["ids"]
    if a["action"] == "reject":
        cards = [c for i in ids for c in anki("notesInfo", notes=[i])[0]["cards"]]
        anki("suspend", cards=cards)
        anki("addTags", notes=ids, tags="rejected autopass")
        log.append({**a, "new": None})
        continue
    m = a["model"]
    model_same = len(ids) == 1 and orig[ids[0]]["model"] == m
    if model_same:
        anki("updateNoteFields", note={"id": ids[0], "fields": a["fields"]})
        anki("addTags", notes=ids, tags="autopass")
        new = ids[0]
    else:
        tags = sorted({t for i in ids for t in orig[i]["tags"]} - {"marked"} | {"autopass"})
        fields = dict(a["fields"])
        if m == "Cloze":
            fields.setdefault("Back Extra", "")
        new = anki("addNote", note={"deckName": orig[ids[0]]["deck"], "modelName": m,
                                    "fields": fields, "tags": tags,
                                    "options": {"allowDuplicate": True}})
        anki("deleteNotes", notes=ids)
    log.append({**a, "new": new})

json.dump({"originals": {i: orig[i] for a in log for i in a["ids"]}, "actions": log},
          open(f"{D}/applied.json", "w"), ensure_ascii=False, indent=1)
print("applied", len(log))
