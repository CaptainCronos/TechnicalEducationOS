#!/usr/bin/env python3
"""Fail when a repository-local Markdown link target does not exist."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
IGNORED_PREFIXES = ("#", "http://", "https://", "mailto:")


def broken_links() -> list[str]:
    failures: list[str] = []
    for markdown_path in sorted(REPOSITORY_ROOT.rglob("*.md")):
        if any(part.startswith(".") for part in markdown_path.relative_to(REPOSITORY_ROOT).parts):
            continue
        content = markdown_path.read_text(encoding="utf-8")
        for line_number, line in enumerate(content.splitlines(), start=1):
            for match in LINK_PATTERN.finditer(line):
                raw_target = match.group(1).strip().strip("<>")
                if not raw_target or raw_target.startswith(IGNORED_PREFIXES):
                    continue
                path_text = unquote(raw_target.split("#", 1)[0].split("?", 1)[0])
                if not path_text:
                    continue
                if path_text.startswith("/"):
                    target = REPOSITORY_ROOT / path_text.lstrip("/")
                else:
                    target = markdown_path.parent / path_text
                if not target.exists():
                    relative_path = markdown_path.relative_to(REPOSITORY_ROOT)
                    failures.append(
                        f"{relative_path}:{line_number}: missing link target "
                        f"{raw_target!r}"
                    )
    return failures


def main() -> int:
    failures = broken_links()
    if failures:
        print("Markdown link validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Markdown link validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
