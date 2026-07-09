from __future__ import annotations

import contextlib
import shutil
import subprocess
import sys
from pathlib import Path

from _shared import REPO_ROOT, command_from_payload, extract_python_paths, load_payload


def _format_python_paths(command: str) -> None:
    paths = extract_python_paths(command)
    if not paths or shutil.which("ruff") is None:
        return
    for path in paths:
        subprocess.run(  # noqa: S603
            ["ruff", "format", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        subprocess.run(  # noqa: S603
            ["ruff", "check", "--fix", str(path)],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )


def _extract_exit_code(payload: dict) -> int | None:
    candidates: list[object] = [payload.get("exit_code"), payload.get("returncode")]
    for key in ("tool_response", "tool_output", "result", "response"):
        value = payload.get(key)
        if isinstance(value, dict):
            candidates.extend(
                [
                    value.get("exit_code"),
                    value.get("returncode"),
                    value.get("status"),
                ]
            )
            success = value.get("success")
            if isinstance(success, bool):
                candidates.append(0 if success else 1)
    for candidate in candidates:
        if isinstance(candidate, bool):
            return 0 if candidate else 1
        if isinstance(candidate, int):
            return candidate
        if isinstance(candidate, str) and candidate.isdigit():
            return int(candidate)
    return None


def _record_verify_class(command: str, payload: dict) -> None:
    from verify_first import append_verify_log  # noqa: PLC0415

    if append_verify_log(command) is None:
        return
    exit_code = _extract_exit_code(payload)
    if exit_code is None:
        return
    shared = Path(__file__).resolve().parents[2] / ".agents" / "shared"
    if str(shared) not in sys.path:
        sys.path.insert(0, str(shared))
    with contextlib.suppress(Exception):
        from work_ledger import mark_verified  # noqa: PLC0415

        mark_verified(command, passed=exit_code == 0)


def main() -> int:
    try:
        payload = load_payload()
        command = command_from_payload(payload)
        if not command:
            return 0
        with contextlib.suppress(Exception):
            _format_python_paths(command)
        with contextlib.suppress(Exception):
            _record_verify_class(command, payload)
    except Exception:  # noqa: BLE001
        return 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
