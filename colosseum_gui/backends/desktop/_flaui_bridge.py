"""Load vendored FlaUI DLLs through pythonnet (Windows only)."""

from __future__ import annotations

import sys
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

_BRIDGE_READY = False


def vendor_dir() -> Path:
    return Path(str(resources.files("colosseum_gui").joinpath("vendor", "flaui")))


def setup_flaui_bridge() -> None:
    """Load FlaUI assemblies into the CLR. Idempotent."""
    global _BRIDGE_READY  # noqa: PLW0603
    if _BRIDGE_READY:
        return
    if not sys.platform.startswith("win"):
        raise OSError("FlaUI is only available on Windows")
    try:
        import clr
    except ImportError as exc:
        raise OSError(
            "pythonnet is not installed; reinstall colosseum-gui on Windows",
        ) from exc

    bin_dir = vendor_dir()
    load_order = (
        "Microsoft.Win32.Registry.dll",
        "System.Drawing.Common.dll",
        "System.Management.dll",
        "Interop.UIAutomationClient.dll",
        "FlaUI.Core.dll",
        "FlaUI.UIA3.dll",
    )
    for name in load_order:
        dll = bin_dir / name
        if not dll.is_file():
            raise FileNotFoundError(f"FlaUI vendor DLL missing: {dll}")
        clr.AddReference(str(dll))
    _BRIDGE_READY = True


@lru_cache(maxsize=1)
def uia3_automation() -> Any:  # noqa: ANN401
    setup_flaui_bridge()
    from FlaUI.UIA3 import UIA3Automation

    return UIA3Automation()
