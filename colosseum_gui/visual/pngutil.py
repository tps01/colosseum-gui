"""RGB PNG encode/decode helpers for visual checks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from PIL import Image, UnidentifiedImageError

if TYPE_CHECKING:
    from pathlib import Path


def write_png(path: Path, width: int, height: int, rgb: bytes) -> None:
    """Write an 8-bit RGB PNG from packed ``RGBRGB...`` bytes."""
    expected = width * height * 3
    if len(rgb) != expected:
        raise ValueError(f"rgb length {len(rgb)} != {expected}")
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.frombytes("RGB", (width, height), rgb).save(path, format="PNG")


def read_png(path: Path) -> tuple[int, int, bytes]:
    """Return ``(width, height, rgb_bytes)`` for a PNG image."""
    try:
        with Image.open(path) as image:
            if image.format != "PNG":
                raise ValueError(f"not a PNG: {path}")
            rgb_image = image.convert("RGB")
            width, height = rgb_image.size
            return width, height, rgb_image.tobytes()
    except UnidentifiedImageError as exc:
        raise ValueError(f"not a PNG: {path}") from exc


def solid_rgb(width: int, height: int, color: tuple[int, int, int]) -> bytes:
    r, g, b = color
    return bytes([r, g, b]) * (width * height)
