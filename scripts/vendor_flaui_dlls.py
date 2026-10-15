#!/usr/bin/env python3
"""Download FlaUI and transitive DLLs into colosseum_gui/vendor/flaui/.

Re-run when bumping the pinned FlaUI version. Requires network access.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

FLAUI_VERSION = "4.0.0"
INTEROP_VERSION = "10.19041.0"
DEPS = (
    ("Microsoft.Win32.Registry", "5.0.0"),
    ("System.Drawing.Common", "5.0.2"),
    ("System.Management", "8.0.0"),
)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _download_nupkg(name: str, version: str, dest: Path) -> Path:
    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / f"{name}.{version}.nupkg"
    url = f"https://www.nuget.org/api/v2/package/{name}/{version}"
    subprocess.check_call(["curl", "-fsSL", "-o", str(archive), url])
    return archive


def _dll_rank(path: Path) -> int:
    """Prefer Windows RID implementations; skip NuGet ref/ stubs."""
    parts = {part.lower() for part in path.parts}
    if "ref" in parts:
        return 0
    parent = path.parent.name.lower()
    win_rid = "runtimes" in parts and "win" in parts
    if win_rid and parent == "netstandard2.0":
        return 5
    if win_rid:
        return 4
    if parent in {"net48", "net472", "net461"} or "windows" in parent:
        return 2
    if parent == "netstandard2.0":
        return 1
    return 0


def _extract_dll(archive: Path, work: Path) -> dict[str, Path]:
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(work)
    found: dict[str, Path] = {}
    for path in work.rglob("*.dll"):
        rank = _dll_rank(path)
        if rank == 0:
            continue
        current = found.get(path.name)
        if current is None or _dll_rank(current) < rank:
            found[path.name] = path
    return found


def main() -> int:
    out_dir = _repo_root() / "colosseum_gui" / "vendor" / "flaui"
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True)

    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        bundles = [
            ("FlaUI.Core", FLAUI_VERSION),
            ("FlaUI.UIA3", FLAUI_VERSION),
            ("Interop.UIAutomationClient", INTEROP_VERSION),
            *DEPS,
        ]
        copied: set[str] = set()
        for name, version in bundles:
            archive = _download_nupkg(name, version, work / "downloads")
            extract_root = work / "extract" / name
            dlls = _extract_dll(archive, extract_root)
            for dll_name, dll_path in sorted(dlls.items()):
                if dll_name in copied:
                    continue
                shutil.copy2(dll_path, out_dir / dll_name)
                copied.add(dll_name)
                print(f"vendor {dll_name}")

        license_src = work / "extract" / "FlaUI.Core" / "LICENSE.txt"
        if license_src.is_file():
            shutil.copy2(license_src, out_dir / "FlaUI-LICENSE.txt")

    print(f"wrote {len(copied)} DLLs to {out_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
