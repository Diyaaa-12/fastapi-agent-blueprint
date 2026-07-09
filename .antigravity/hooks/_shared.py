from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
STATE_ROOT = Path(os.environ.get("HARNESS_STATE_ROOT", REPO_ROOT))
STATE_DIR = STATE_ROOT / ".antigravity" / "state"

SHARED_PKG = REPO_ROOT / ".agents" / "shared"
if str(SHARED_PKG) not in sys.path:
    sys.path.insert(0, str(SHARED_PKG))


try:
    from harness_debug import debug_log  # noqa: E402
except Exception:  # noqa: BLE001

    def debug_log(event: str, exc: BaseException | None = None) -> None:
        return


def load_payload() -> dict[str, Any]:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        debug_log("antigravity hook payload parse failed", exc)
        return {}
    return payload if isinstance(payload, dict) else {}


def run_command(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603
        args,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def changed_files() -> list[str]:
    tracked = run_command(["git", "diff", "--name-only", "HEAD"])
    untracked = run_command(["git", "ls-files", "--others", "--exclude-standard"])
    return sorted(
        {
            line
            for chunk in (tracked.stdout, untracked.stdout)
            for line in chunk.splitlines()
            if line
        }
    )


def tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "toolName", "tool", "name"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    for key in ("tool_input", "toolInput", "input", "args", "arguments"):
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def command_from_payload(payload: dict[str, Any]) -> str:
    inp = tool_input(payload)
    for key in ("command", "cmd", "shell_command"):
        value = inp.get(key)
        if isinstance(value, str):
            return value
    for key in ("command", "cmd", "shell_command"):
        value = payload.get(key)
        if isinstance(value, str):
            return value
    return ""


def extract_python_paths(command: str) -> list[Path]:
    matches = re.findall(r"([A-Za-z0-9_./-]+\.py)\b", command)
    paths: list[Path] = []
    for match in matches:
        candidate = (
            (REPO_ROOT / match).resolve() if not match.startswith("/") else Path(match)
        )
        try:
            candidate.relative_to(REPO_ROOT)
        except ValueError:
            continue
        if candidate.exists() and candidate.is_file():
            paths.append(candidate)
    return list(dict.fromkeys(paths))


def session_env_id() -> str | None:
    for key in (
        "ANTIGRAVITY_SESSION_ID",
        "GEMINI_SESSION_ID",
        "GEMINI_CLI_SESSION_ID",
        "AGENT_SESSION_ID",
    ):
        value = os.environ.get(key)
        if value:
            return value
    return None
