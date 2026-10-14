#!/bin/bash
set -euo pipefail

# This vault is pure-stdlib Python (see README.md "Running the scripts") -- no
# package.json/requirements.txt/pyproject.toml, nothing to install. This hook
# runs in cloud and local sessions alike, and its job is to confirm python3 is
# present and that the vault's integrity gate is clean before the session
# starts, so a broken checkout is caught immediately instead of mid-session.
#
# It also restates the one rule that is invisible from inside a transcript:
# the terminal cannot render mathematics, so a session run in chat silently
# degrades. See "Everything goes in the artifact" in skills/session/SKILL.md.
cd "$CLAUDE_PROJECT_DIR"
python3 scripts/check_vault.py

cat <<'RULE'

────────────────────────────────────────────────────────────────────────────
EVERYTHING GOES IN THE ARTIFACT.

Every question, every answer, every derivation, every diagram, every piece of
grading feedback and every word of teaching is written to the session
Artifact. This applies to quiz, placement and study alike, and to any one-off
question-and-answer exchange.

This interface renders GitHub-flavoured markdown and nothing else. It has no
LaTeX and no image surface, so `$\lim_{x\to a} f(x)$` reaches the learner as
literal backslashes and a diagram cannot reach them at all. A session run in
chat does not look slightly worse; its mathematics is unreadable and its
figures do not exist.

Chat carries turn-taking only: which question is live, that an answer landed,
what was written back. The content lives on the page.

  skills/session/SKILL.md -> "Everything goes in the artifact"
────────────────────────────────────────────────────────────────────────────
RULE

# A handoff from an earlier session, if one is pending.
if [ -f NEXT.md ]; then
  printf '\n── NEXT.md (pending handoff, read before anything else) ──\n\n'
  cat NEXT.md
fi
