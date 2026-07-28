#!/usr/bin/env python3
"""Smoke-test an installed TEOS wheel from outside the source tree."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


def _run(
    command: list[str],
    *,
    cwd: Path,
    expected_code: int = 0,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.pop("PYTHONPATH", None)
    result = subprocess.run(
        command,
        cwd=cwd,
        env=environment,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != expected_code:
        raise RuntimeError(
            f"{' '.join(command)} returned {result.returncode}, expected "
            f"{expected_code}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repository-root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args()
    repository_root = args.repository_root.resolve()

    import teos

    package_version = importlib.metadata.version("technicaleducationos")
    module_path = Path(teos.__file__).resolve()
    if module_path.is_relative_to(repository_root):
        raise RuntimeError(f"teos was imported from the source tree: {module_path}")
    if package_version != teos.__version__:
        raise RuntimeError(
            f"metadata version {package_version} != teos.__version__ "
            f"{teos.__version__}"
        )

    with tempfile.TemporaryDirectory(prefix="teos-wheel-smoke-") as temporary:
        work_directory = Path(temporary)
        teos_command = str(Path(sys.executable).parent / "teos")

        help_result = _run([teos_command, "--help"], cwd=work_directory)
        if "Validate, audit, and generate" not in help_result.stdout:
            raise RuntimeError("teos --help did not contain the expected diagnostic")

        build_result = _run(
            [
                teos_command,
                "build",
                "--course",
                str(repository_root / "curriculum/courses/dsl204"),
            ],
            cwd=work_directory,
        )
        if "Build passed:" not in build_result.stdout:
            raise RuntimeError("teos build did not report success")

        schedule_path = work_directory / "schedule.json"
        _run(
            [
                teos_command,
                "schedule",
                "--course",
                str(repository_root / "curriculum/courses/dsl204"),
                "--institution",
                str(repository_root / "institutions/j-tech/institution.json"),
                "--calendar",
                str(
                    repository_root
                    / "institutions/j-tech/calendars/fall-2026.json"
                ),
                "--meeting-pattern",
                "thursday-friday-am",
                "--output",
                str(schedule_path),
            ],
            cwd=work_directory,
        )
        schedule = json.loads(schedule_path.read_text(encoding="utf-8"))
        if not schedule.get("assignments"):
            raise RuntimeError("teos schedule did not produce JSON assignments")

        invalid_result = _run(
            [teos_command, "not-a-command"],
            cwd=work_directory,
            expected_code=2,
        )
        if "invalid choice" not in invalid_result.stderr:
            raise RuntimeError("invalid command did not produce a diagnostic")
        if "Traceback" in invalid_result.stderr:
            raise RuntimeError("invalid command exposed a Python traceback")

        mistake_result = _run(
            [
                teos_command,
                "build",
                "--course",
                str(work_directory / "missing-course"),
            ],
            cwd=work_directory,
            expected_code=2,
        )
        if not mistake_result.stderr.startswith("Error:"):
            raise RuntimeError("normal user mistake did not produce an Error diagnostic")
        if "Traceback" in mistake_result.stderr:
            raise RuntimeError("normal user mistake exposed a Python traceback")

    print(
        f"Installed-package verification passed for technicaleducationos "
        f"{package_version}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
