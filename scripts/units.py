#!/usr/bin/env python3
"""
Shared access to courses/<slug>/units.json — the vault's one scheduled object.

The unit is the atom. A course is a directory of units plus the material they share; nothing
else carries schedulable state. See SCHEMA.md.

Two things in here are load-bearing and deliberately not stored anywhere:

- `stage()` is derived from `placed`, `srs.reps` and the unit's concept states. Storing it would
  let it drift from the states that define it.
- `urgency()` ranks, and never thresholds. FSRS's memory model without FSRS's scheduler: there
  is no due date, so a three-week gap produces no backlog -- only a set of units that are all
  somewhat more urgent than they were, in the same order.
"""
import json
from datetime import date, datetime
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent
COURSES = VAULT / "courses"
SESSIONS = VAULT / "sessions"

STAGES = ("unknown", "new", "learning", "learned")
CONCEPT_STATES = ("unknown", "unseen", "seen")

# FSRS-ish defaults for a unit that has never been reviewed.
INIT_DIFFICULTY = 5.0
INIT_STABILITY = 0.0

# Grades. Deliberately three, not FSRS's four: `hard` and `good` are a distinction this vault
# cannot make honestly, because a unit's review is several questions and the aggregate is not a
# button press. See `skills/grader/SKILL.md` for what separates `partial` from `fail`.
GRADES = ("fail", "partial", "pass")

# First-review stability, in days, by grade. A unit reviewed once and passed cold is worth about
# a week; one that needed hints, two days; one that failed, half a day -- it comes back almost
# immediately, which is what a failure should buy.
INIT_S = {"fail": 0.5, "partial": 2.0, "pass": 7.0}

D_STEP = {"fail": +1.2, "partial": +0.15, "pass": -0.5}   # difficulty drift per review
S_GROW = {"partial": 1.4, "pass": 2.6}                    # stability multiplier ceiling
LAPSE_FACTOR = 0.4        # a failure MULTIPLIES stability rather than resetting it
MIN_STABILITY = 0.25

# --- course share ---------------------------------------------------------------------------
# `share` is a course-header field and it means one thing: out of this many sessions, how many
# should be this course. The shares are read as a ratio, so if they sum to SHARE_WINDOW they can
# be read directly as "sessions per SHARE_WINDOW", which is the point of setting them that way.
SHARE_WINDOW = 10

# Gaussian noise added to a unit's urgency during the study draw's second stage, so the unit
# chosen inside a course is not always one of the same few at the top of its ranking. It is small
# against the 0-5 range urgency actually occupies: enough to reorder units that are close, not
# enough to promote one that is genuinely cold over one that is genuinely due. The quiz draw does
# not use it -- there the ranking is the whole point.
UNIT_NOISE = 0.25


def course_slugs(include_archived=False):
    out = []
    for d in sorted(COURSES.iterdir()):
        if not d.is_dir():
            continue
        if d.name == "_archive":
            if include_archived:
                out += [f"_archive/{a.name}" for a in sorted(d.iterdir()) if a.is_dir()]
            continue
        out.append(d.name)
    return out


def load_course(slug):
    """The whole units.json for one course, or None if it has none."""
    p = COURSES / slug / "units.json"
    if not p.exists():
        return None
    return json.loads(p.read_text())


def save_course(slug, doc):
    p = COURSES / slug / "units.json"
    p.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n")


def load_all(include_archived=False):
    """Every unit in the vault, keyed by qualified id `<course>:<unit>`.

    Units also answer to their bare id when unambiguous, which is how within-course prereqs
    resolve without every file having to spell out its own course.
    """
    units, bare = {}, {}
    for slug in course_slugs(include_archived):
        doc = load_course(slug)
        if not doc:
            continue
        default = doc.get("default_priority", 1)
        for u in doc.get("units", []):
            u = dict(u)
            u["course"] = slug
            u["_default_priority"] = default
            units[f"{slug}:{u['id']}"] = u
            bare.setdefault(u["id"], []).append(f"{slug}:{u['id']}")
    for u in units.values():
        u["_resolve"] = bare
    return units


def resolve(ref, owner, units):
    """A prereq reference as written -> a key into `units`. `<course>:<unit>` is explicit;
    a bare id means a unit of the referencing course."""
    if ":" in ref:
        return ref
    key = f"{owner}:{ref}"
    return key if key in units else ref


def priority(u):
    p = u.get("priority")
    return u["_default_priority"] if p is None else p


def stage(u):
    """unknown -> new -> learning -> learned. Order of evaluation matters; see SCHEMA.md.

    Note what this ratchet guarantees: `srs.reps` only ever increases, so a unit that has reached
    `learning` can never fall back to `new` or `unknown`. Demoting a concept moves a unit from
    `learned` to `learning` and no further -- and since a prerequisite edge is satisfied at
    `learning`, **a demotion can never block anything downstream.** A bad review on one hard
    concept returns its own unit to the study pool without cascading through the graph.
    """
    if not u.get("placed"):
        return "unknown"
    concepts = u.get("concepts") or []
    if concepts and all(c.get("state") == "seen" for c in concepts):
        return "learned"
    if (u.get("srs") or {}).get("reps", 0) >= 1:
        return "learning"
    return "new"


def _days_since(iso, today=None):
    if not iso:
        return None
    today = today or date.today()
    return max(0, (today - datetime.fromisoformat(iso).date()).days)


def retrievability(u, today=None):
    """FSRS's power forgetting curve. A unit never reviewed has R = 0 -- maximally urgent among
    things that are eligible at all, which is what makes new material get picked up."""
    srs = u.get("srs") or {}
    s = srs.get("stability") or 0.0
    t = _days_since(srs.get("last_seen"), today)
    if t is None or s <= 0:
        return 0.0
    return (1 + t / (9 * s)) ** -1


def urgency(u, today=None):
    return (1 - retrievability(u, today)) * priority(u)


def review(u, grade, today=None):
    """Fold one review's outcome into the unit's SRS state, in place.

    This is the half of the memory model that was convention rather than code: `retrievability`
    has always been implemented, but nothing updated the `stability` and `difficulty` it reads,
    so the ranking was decaying toward plain priority order.

    Four properties are deliberate:

    - **A lapse multiplies stability, it does not reset it.** A unit learned once and lost is not
      in the same state as one never learned, and treating them alike is what makes conventional
      schedulers punishing after a gap. `LAPSE_FACTOR` is 0.4, so a failure costs about a
      half-life, not everything.
    - **Growth is damped by how retrievable the unit already was.** Reviewing something you would
      have recalled anyway teaches the schedule little, so the gain shrinks as R approaches 1.
      This is what makes early, easy reviews cheap and late, effortful ones valuable.
    - **Difficulty drifts, it never jumps.** One bad session on a unit you know is noise.
    - **A lapse is counted whenever the learner could not produce it cold**, on `partial` as well
      as `fail`, and on a unit's first review as much as its tenth. `lapses` is a record of how
      often the material has been lost, not a second copy of the stability decision, so it does
      not follow the branches above.

    Returns the updated `srs` dict.
    """
    if grade not in GRADES:
        raise ValueError(f"grade must be one of {GRADES}, not {grade!r}")
    today = today or date.today()
    srs = u.setdefault("srs", {})
    srs.setdefault("reps", 0)
    srs.setdefault("lapses", 0)
    d = srs.get("difficulty") or INIT_DIFFICULTY
    s = srs.get("stability") or 0.0

    d = min(10.0, max(1.0, d + D_STEP[grade]))

    # A lapse records that the learner could not produce this cold, which
    # `skills/grader/SKILL.md` counts for a retrieval failure (`partial`) as well as a model
    # failure (`fail`). It is a fact about the review, so it is counted independently of the
    # stability branch below, which is a decision about the schedule. Counting it inside that
    # branch was a bug twice over: it missed `partial` entirely, and it skipped even a `fail`
    # whenever the unit had no prior stability -- which is common when a course is initialised
    # to `learned` without ever being studied, and its first real review is exactly the one
    # worth recording.
    if grade in ("fail", "partial"):
        srs["lapses"] += 1

    if s <= 0 or not srs.get("last_seen"):
        s = INIT_S[grade]
    elif grade == "fail":
        s = max(MIN_STABILITY, s * LAPSE_FACTOR)
    else:
        r = retrievability(u, today)
        # (1 - r) is the "how much did this review actually teach us" term: near 0 for a unit
        # that was still fresh, near 1 for one on the edge of being lost.
        gain = 1 + (S_GROW[grade] - 1) * (1 - r) * (11 - d) / 10
        s = max(MIN_STABILITY, s * gain)

    srs["difficulty"] = round(d, 2)
    srs["stability"] = round(s, 2)
    srs["reps"] += 1
    srs["last_seen"] = today.isoformat()
    if not u.get("placed"):
        u["placed"] = today.isoformat()
    return srs


def prereqs_satisfied(u, units, today=None):
    """An edge is satisfied once its source reaches `learning` -- partial grasp, not completion.
    A prereq that does not resolve is reported, not silently treated as satisfied."""
    unmet, dangling = [], []
    for ref in u.get("prereqs", []):
        key = resolve(ref, u["course"], units)
        src = units.get(key)
        if src is None:
            dangling.append(ref)
        elif stage(src) in ("unknown", "new"):
            unmet.append(key)
    return unmet, dangling


def runnable(u):
    """Can this unit be studied at all -- is its reading actually in the vault."""
    return (u.get("reading") or {}).get("status") == "present"


def quiz_eligible(u, units, today=None):
    """Eligible to be quizzed on: worth asking about, and fair to ask about.

    `new` is excluded because it means studied zero times -- there is nothing to review yet, and
    a question drawn from it would be a test of never-learned material. `unknown` is excluded
    because it has not been placed. That leaves `learning` and `learned`, which is exactly the
    set the spacing effect applies to."""
    if priority(u) <= 0:
        return False
    if stage(u) not in ("learning", "learned"):
        return False
    unmet, _ = prereqs_satisfied(u, units, today)
    return not unmet


def study_eligible(u, units, today=None):
    """Eligible to be the session's study unit: has concepts left to cover, and its
    prerequisites are open. `learned` units are excluded -- if one has decayed, the quiz will
    demote it and it becomes eligible again on the next evaluation."""
    if priority(u) <= 0:
        return False
    if not runnable(u):
        return False
    if stage(u) == "learned":
        return False
    unmet, _ = prereqs_satisfied(u, units, today)
    return not unmet


def seen_concepts(u):
    return {c["id"] for c in (u.get("concepts") or []) if c.get("state") == "seen"}


def unit_questions(u):
    """Every question this unit owns: those attached to a concept, plus its own `questions`,
    which holds only the ones no concept claims. The two lists are disjoint by construction --
    that is why neither is redundant with the other."""
    out = list(u.get("questions") or [])
    for c in u.get("concepts") or []:
        out += c.get("questions") or []
    return sorted(set(out))


def askable(u):
    """Questions it is fair to ask right now: every concept a question tests has been seen.

    A question the unit owns but no concept claims is askable once the unit itself is at
    `learning` or better -- there is no finer-grained evidence to gate it on."""
    seen = seen_concepts(u)
    out = list(u.get("questions") or [])
    for c in u.get("concepts") or []:
        if c.get("state") == "seen":
            out += c.get("questions") or []
    # A question attached to several concepts is fair only if ALL of them are seen.
    owners = {}
    for c in u.get("concepts") or []:
        for q in c.get("questions") or []:
            owners.setdefault(q, []).append(c["id"])
    return sorted({q for q in set(out)
                   if all(o in seen for o in owners.get(q, ()))})


# ---------------------------------------------------------------------------------------------
# Course-level scheduling: how often each course comes up, as opposed to which of its units.
# ---------------------------------------------------------------------------------------------

def course_prefixes(include_archived=False):
    """Unit-id prefix -> course slug, derived from the units rather than configured.

    Every course's ids share a prefix by convention (for example `ex-`, `la-`, `db-`). A prefix
    claimed by two courses is dropped rather than guessed at.
    """
    owners = {}
    for slug in course_slugs(include_archived):
        doc = load_course(slug) or {}
        for u in doc.get("units", []):
            owners.setdefault(u["id"].split("-")[0], set()).add(slug)
    return {p: next(iter(cs)) for p, cs in owners.items() if len(cs) == 1}


def recent_study_courses(window=SHARE_WINDOW, include_archived=False):
    """The course of each of the last `window` study sessions, oldest last.

    Read off the `sessions/` filenames, which SCHEMA.md fixes as
    `<YYYY-MM-DD[-HHMM]>-<unit-id>.md`. **Nothing schedules on this.** The course draw is
    independent of history by design; this exists so `session.py` can show what the recent mix
    actually was, which is what the learner needs in order to decide whether to override the draw.
    A file whose remainder does not begin with a known course prefix is skipped -- a quiz-only
    record is named `mixed-retention` and correctly does not count as studying anything.
    """
    if not SESSIONS.is_dir():
        return []
    prefixes = course_prefixes(include_archived)
    seen = []
    for f in sorted(p.name for p in SESSIONS.glob("*.md")):
        rest = f[:-3][11:]                                   # drop `.md`, then `YYYY-MM-DD-`
        if len(rest) > 5 and rest[:4].isdigit() and rest[4] == "-":
            rest = rest[5:]                                  # drop the `NNNN-` sequence
        slug = prefixes.get(rest.split("-")[0])
        if slug:
            seen.append(slug)
    return seen[-window:]


def course_share(slug):
    """This course's target frequency. Falls back to `default_priority` for a course that has
    not been given a `share` yet, so an unmigrated or archived course still schedules."""
    doc = load_course(slug) or {}
    v = doc.get("share")
    return v if isinstance(v, int) and v >= 0 else (doc.get("default_priority") or 0)


def course_weights(courses, shares=None):
    """Probability of drawing each course this session: its `share`, renormalised.

    The draw is independent across sessions on purpose. A deficit scheme -- weighting by target
    minus what the last ten sessions served -- would make every window of ten hit the shares
    exactly, but it buys that by making the rotation a cycle, and it needs a history to read.
    Independence gives the right long-run frequency and a genuinely uncertain next session, at the
    cost of streaks. Streaks are cheap here: the learner can name a course and override the draw
    in one sentence, which is a better answer to an unlucky run than a scheduler that cannot
    produce one.

    `courses` are the slugs with something to offer this session; a course with no eligible unit
    holds no slot, and the shares renormalise over what is left, so muting or exhausting a course
    redistributes its share rather than wasting it.
    """
    shares = shares or {c: course_share(c) for c in courses}
    total = sum(shares.get(c, 0) for c in courses)
    if total <= 0:
        return {c: 1.0 / len(courses) for c in courses} if courses else {}
    return {c: shares.get(c, 0) / total for c in courses}


def jittered_urgency(u, rng, sigma=UNIT_NOISE, today=None):
    """`urgency` plus small Gaussian noise, clamped at zero. See UNIT_NOISE."""
    if not sigma:
        return urgency(u, today)
    return max(urgency(u, today) + rng.gauss(0.0, sigma), 0.0)
