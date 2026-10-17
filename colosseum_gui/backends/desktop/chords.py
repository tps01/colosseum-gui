"""Shared chord grammar for desktop ``press_key`` (FlaUI, generic, sim)."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ChordToken:
    """One modifier or key in a chord such as ``ctrl+shift+p``."""

    kind: str  # "modifier" | "key"
    name: str  # upper-case canonical name (CONTROL, SHIFT, P, F5, ENTER, …)


_MODIFIER_CANON = {
    "CTRL": "CONTROL",
    "CONTROL": "CONTROL",
    "SHIFT": "SHIFT",
    "ALT": "ALT",
    "MENU": "ALT",
    "WIN": "LWIN",
    "WINDOWS": "LWIN",
    "LWIN": "LWIN",
    "RWIN": "RWIN",
}

_FLAUI_MODIFIER = {
    "CONTROL": "CONTROL",
    "SHIFT": "SHIFT",
    "ALT": "ALT",
    "LWIN": "LWIN",
    "RWIN": "RWIN",
}

_VK_CODES = {
    "TAB": 0x09,
    "ENTER": 0x0D,
    "RETURN": 0x0D,
    "ESCAPE": 0x1B,
    "ESC": 0x1B,
    "SPACE": 0x20,
    "LEFT": 0x25,
    "UP": 0x26,
    "RIGHT": 0x27,
    "DOWN": 0x28,
    "CONTROL": 0x11,
    "SHIFT": 0x10,
    "ALT": 0x12,
    "LWIN": 0x5B,
    "RWIN": 0x5C,
}


def parse_chord(key: str) -> list[ChordToken]:
    """Parse ``ctrl+shift+p`` / ``F5`` / ``enter`` into canonical tokens."""
    text = key.strip()
    if not text:
        return []
    parts = [p.strip() for p in text.replace("-", "+").split("+") if p.strip()]
    tokens: list[ChordToken] = []
    for part in parts:
        upper = part.upper()
        if upper in _MODIFIER_CANON:
            tokens.append(ChordToken("modifier", _MODIFIER_CANON[upper]))
            continue
        if upper.startswith("F") and upper[1:].isdigit():
            tokens.append(ChordToken("key", upper))
            continue
        if len(upper) == 1 and upper.isalnum():
            tokens.append(ChordToken("key", upper))
            continue
        tokens.append(ChordToken("key", upper))
    return tokens


def format_chord(tokens: list[ChordToken]) -> str:
    """Normalize tokens back to a stable ``ctrl+shift+p`` string for sim/logs."""
    parts: list[str] = []
    for token in tokens:
        if token.name == "CONTROL":
            parts.append("ctrl")
        elif token.name == "LWIN":
            parts.append("win")
        else:
            parts.append(token.name.lower())
    return "+".join(parts)


def to_flaui_virtual_key_names(tokens: list[ChordToken]) -> list[str]:
    """Map tokens to FlaUI ``VirtualKeyShort`` member names."""
    names: list[str] = []
    for token in tokens:
        if token.kind == "modifier":
            names.append(_FLAUI_MODIFIER[token.name])
            continue
        if len(token.name) == 1 and token.name.isalnum():
            names.append(f"KEY_{token.name}")
            continue
        names.append(token.name)
    return names


def to_win32_vk_codes(tokens: list[ChordToken]) -> list[int]:
    """Map tokens to Win32 virtual-key codes."""
    if not tokens:
        raise ValueError("empty key")
    codes: list[int] = []
    for token in tokens:
        name = token.name
        if name in _VK_CODES:
            codes.append(_VK_CODES[name])
            continue
        if name.startswith("F") and name[1:].isdigit():
            n = int(name[1:])
            if 1 <= n <= 24:
                codes.append(0x70 + n - 1)
                continue
        if len(name) == 1 and name.isalnum():
            codes.append(ord(name.upper()))
            continue
        raise ValueError(f"unsupported key token {name!r}")
    return codes
