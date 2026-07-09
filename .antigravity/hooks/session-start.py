from __future__ import annotations

import contextlib

from _shared import SHARED_PKG

harness_lines = [
    "Antigravity repo harness active:",
    "- Shared rules: AGENTS.md",
    "- Repo workflows: .agents/skills/",
    "- Command hooks: .gemini/settings.json -> .antigravity/hooks/",
    "- Antigravity plugin assets: .antigravity/",
    "- Reasoning-level guards (F/G/H/I) live in AGENTS.md and apply to every conversation and review step.",
    "- Antigravity-specific files are thin adapters; shared governor policy lives in .agents/shared/governor/.",
]

parts = ["\n".join(harness_lines)]
with contextlib.suppress(Exception):
    import sys

    if str(SHARED_PKG) not in sys.path:
        sys.path.insert(0, str(SHARED_PKG))
    from work_ledger import build_session_summary  # noqa: PLC0415

    summary = build_session_summary()
    if summary:
        parts.append(summary)

print("\n\n".join(parts))
