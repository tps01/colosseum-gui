"""Build wheel and sdist into dist/."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    root = Path(__file__).resolve().parents[2]
    subprocess.check_call([sys.executable, "-m", "build", "--outdir", "dist"], cwd=root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
