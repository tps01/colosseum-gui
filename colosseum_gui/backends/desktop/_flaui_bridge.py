"""Load vendored FlaUI DLLs through pythonnet (Windows only)."""

from __future__ import annotations

import os
import sys
from functools import lru_cache
from importlib import resources
from pathlib import Path
from typing import Any

_BRIDGE_READY = False


def vendor_dir() -> Path:
    return Path(str(resources.files("colosseum_gui").joinpath("vendor", "flaui")))


def _ensure_netfx() -> None:
    """Use .NET Framework, not CoreCLR (pythonnet default can follow ``dotnet``).

    FlaUI's inbox sample is Win32 (Notepad). CoreCLR plus netstandard
    System.Drawing.Common stubs throw PlatformNotSupportedException even on
    Windows. Pin netfx before ``import clr``.
    """
    os.environ["PYTHONNET_RUNTIME"] = "netfx"
    try:
        from pythonnet import load

        load("netfx")
    except Exception:  # noqa: BLE001 - already initialized
        return


def setup_flaui_bridge() -> None:
    """Load FlaUI assemblies into the CLR. Idempotent."""
    global _BRIDGE_READY  # noqa: PLW0603
    if _BRIDGE_READY:
        return
    if not sys.platform.startswith("win"):
        raise OSError("FlaUI is only available on Windows")
    _ensure_netfx()
    try:
        import clr
    except ImportError as exc:
        raise OSError(
            "pythonnet is not installed; reinstall colosseum-gui on Windows",
        ) from exc

    bin_dir = vendor_dir()
    # Microsoft.Win32.Registry must be the Windows RID build
    # (runtimes/win/...), not NuGet's netstandard stub.
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
