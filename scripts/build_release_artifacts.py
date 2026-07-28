#!/usr/bin/env python3
"""Build reproducible TEOS wheel and source-distribution artifacts."""

from __future__ import annotations

import argparse
import copy
import gzip
import hashlib
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def _commit_epoch() -> int:
    result = subprocess.run(
        ["git", "log", "-1", "--format=%ct"],
        cwd=REPOSITORY_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return int(result.stdout.strip())


def _normalize_sdist(source: Path, destination: Path, epoch: int) -> None:
    with (
        tarfile.open(source, "r:gz") as source_archive,
        destination.open("wb") as destination_stream,
        gzip.GzipFile(
            filename="",
            mode="wb",
            fileobj=destination_stream,
            mtime=epoch,
        ) as compressed_stream,
        tarfile.open(
            fileobj=compressed_stream,
            mode="w",
            format=tarfile.PAX_FORMAT,
        ) as destination_archive,
    ):
        for member in sorted(source_archive.getmembers(), key=lambda item: item.name):
            normalized = copy.copy(member)
            normalized.mtime = epoch
            normalized.uid = 0
            normalized.gid = 0
            normalized.uname = ""
            normalized.gname = ""
            normalized.pax_headers = {}
            content = source_archive.extractfile(member) if member.isfile() else None
            destination_archive.addfile(normalized, content)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_release_artifacts(output_directory: Path, epoch: int) -> tuple[Path, Path]:
    output_directory.mkdir(parents=True, exist_ok=True)
    if list(output_directory.glob("technicaleducationos-*.whl")) or list(
        output_directory.glob("technicaleducationos-*.tar.gz")
    ):
        raise FileExistsError(
            f"release artifacts already exist in {output_directory}"
        )

    environment = os.environ.copy()
    environment["SOURCE_DATE_EPOCH"] = str(epoch)
    with tempfile.TemporaryDirectory(prefix="teos-release-build-") as temporary:
        staging = Path(temporary)
        subprocess.run(
            [
                sys.executable,
                "-m",
                "build",
                "--outdir",
                str(staging),
            ],
            cwd=REPOSITORY_ROOT,
            env=environment,
            check=True,
        )
        wheels = list(staging.glob("technicaleducationos-*.whl"))
        sdists = list(staging.glob("technicaleducationos-*.tar.gz"))
        if len(wheels) != 1 or len(sdists) != 1:
            raise RuntimeError("build did not produce exactly one wheel and one sdist")
        wheel = output_directory / wheels[0].name
        sdist = output_directory / sdists[0].name
        shutil.copyfile(wheels[0], wheel)
        _normalize_sdist(sdists[0], sdist, epoch)
    return wheel, sdist


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=REPOSITORY_ROOT / "dist")
    parser.add_argument("--source-date-epoch", type=int)
    args = parser.parse_args()
    epoch = args.source_date_epoch if args.source_date_epoch is not None else _commit_epoch()
    wheel, sdist = build_release_artifacts(args.output.resolve(), epoch)
    for path in (wheel, sdist):
        print(f"{_sha256(path)}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
