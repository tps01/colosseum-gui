"""Shared ``select_option`` choice validation for Playwright and web sim."""

from __future__ import annotations


def select_choice(
    *,
    value: str | None,
    label: str | None,
    index: int | None,
) -> dict[str, str | int]:
    """Return exactly one of value/label/index for a native ``<select>``."""
    choice: dict[str, str | int] = {}
    if value is not None:
        choice["value"] = value
    if label is not None:
        choice["label"] = label
    if index is not None:
        choice["index"] = index
    if len(choice) != 1:
        raise ValueError("provide exactly one of value, label, or index")
    return choice
