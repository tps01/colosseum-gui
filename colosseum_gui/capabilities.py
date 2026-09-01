from __future__ import annotations

import json
from contextlib import suppress
from typing import NoReturn, Protocol

from colosseum_gui._paths import resolve_artifact_path
from colosseum_gui.exceptions import GuiCapabilityError


class _TreeBackend(Protocol):
    def capture_tree(self) -> object: ...


def unsupported(
    driver: str,
    operation: str,
    *,
    detail: str = "",
    backend: _TreeBackend | None = None,
) -> NoReturn:
    """Raise :class:`GuiCapabilityError` for an unsupported driver operation."""
    message = f"{operation} is not supported by driver `{driver}`"
    if detail:
        message = f"{message} ({detail})"
    if backend is not None:
        with suppress(Exception):
            tree = backend.capture_tree()
            path = resolve_artifact_path("captures/capability_debug_tree.json")
            path.write_text(json.dumps(tree, indent=2), encoding="utf-8")
            message = f"{message}; tree saved to {path.name}"
    raise GuiCapabilityError(message)
