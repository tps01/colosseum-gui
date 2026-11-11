"""Pure GUI input validation; never opens a browser or sends keystrokes."""

from __future__ import annotations

import sys


def check_input(data: bytes) -> None:
    from colosseum_gui.backends.desktop.chords import (
        format_chord,
        parse_chord,
        to_flaui_virtual_key_names,
        to_win32_vk_codes,
    )
    from colosseum_gui.backends.web.select_choice import select_choice
    from colosseum_gui.locators import reject_desktop_locators, reject_web_locators

    data = data[:512]
    flags = data[0] if data else 0
    text = data[1:].decode("utf-8", errors="replace")
    # None is absence; an empty string is still a supplied locator/choice.
    choice = {
        "value": text if flags & 1 else None,
        "label": text if flags & 2 else None,
        "index": int.from_bytes(data[1:3], "little", signed=True) if flags & 4 else None,
    }
    expected = {key: value for key, value in choice.items() if value is not None}
    try:
        actual = select_choice(**choice)
    except ValueError:
        assert len(expected) != 1
    else:
        assert len(expected) == 1 and actual == expected
    for guard, kwargs, invalid in (
        (
            reject_web_locators,
            {"css": choice["value"], "test_id": choice["label"]},
            bool(flags & 3),
        ),
        (reject_desktop_locators, {"automation_id": choice["value"]}, bool(flags & 1)),
    ):
        try:
            guard(**kwargs)
        except ValueError:
            assert invalid
        else:
            assert not invalid

    # Generate known chords and independently specify their OS key representations.
    modifiers = (
        ("ctrl", "CONTROL", 0x11),
        ("shift", "SHIFT", 0x10),
        ("menu", "ALT", 0x12),
        ("windows", "LWIN", 0x5B),
    )
    key = chr(ord("A") + flags % 26)
    parts, names, codes = [], [], []
    for bit, (alias, canonical, code) in enumerate(modifiers):
        if flags & (1 << bit):
            parts.append(alias)
            names.append(canonical)
            codes.append(code)
    if flags & 16:
        number = flags % 24 + 1
        parts.append(f"f{number}")
        names.append(f"F{number}")
        codes.append(0x70 + number - 1)
    else:
        parts.append(key.lower())
        names.append("KEY_" + key)
        codes.append(ord(key))
    separator = " - " if flags & 32 else " + "
    tokens = parse_chord("  " + separator.join(parts) + "  ")
    assert to_flaui_virtual_key_names(tokens) == names
    assert to_win32_vk_codes(tokens) == codes
    assert parse_chord(format_chord(tokens)) == tokens
    for unsupported in ("", "F0", "F25", "not_a_key"):
        try:
            to_win32_vk_codes(parse_chord(unsupported))
        except ValueError:
            pass
        else:
            raise AssertionError("Unsupported key accepted")


def main() -> None:
    import atheris

    with atheris.instrument_imports(include=["colosseum_gui"]):
        import colosseum_gui.backends.desktop.chords  # noqa: F401
        import colosseum_gui.backends.web.select_choice  # noqa: F401
        import colosseum_gui.locators  # noqa: F401
    atheris.Setup(sys.argv, atheris.instrument_func(check_input))
    atheris.Fuzz()


if __name__ == "__main__":
    main()
