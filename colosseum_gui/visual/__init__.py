"""Visual regression and WCAG contrast helpers (stdlib PNG)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from colosseum_gui.visual.pngutil import read_png, write_png

if TYPE_CHECKING:
    from pathlib import Path


def pixel_diff_ratio(
    actual_path: Path,
    baseline_path: Path,
    *,
    threshold: int = 16,
) -> float:
    """Fraction of pixels that differ by more than ``threshold`` on any channel."""
    aw, ah, a_rgb = read_png(actual_path)
    bw, bh, b_rgb = read_png(baseline_path)
    if (aw, ah) != (bw, bh):
        raise ValueError(
            f"screenshot size {aw}x{ah} does not match baseline {bw}x{bh}",
        )
    differing = 0
    total = aw * ah
    for i in range(0, len(a_rgb), 3):
        if (
            abs(a_rgb[i] - b_rgb[i]) > threshold
            or abs(a_rgb[i + 1] - b_rgb[i + 1]) > threshold
            or abs(a_rgb[i + 2] - b_rgb[i + 2]) > threshold
        ):
            differing += 1
    return differing / float(total) if total else 0.0


def write_diff_png(actual_path: Path, baseline_path: Path, out_path: Path) -> None:
    """Write a red-highlight diff image for mismatched pixels."""
    aw, ah, a_rgb = read_png(actual_path)
    bw, bh, b_rgb = read_png(baseline_path)
    if (aw, ah) != (bw, bh):
        raise ValueError("sizes must match to write a diff PNG")
    out = bytearray()
    for i in range(0, len(a_rgb), 3):
        if a_rgb[i : i + 3] != b_rgb[i : i + 3]:
            out.extend((255, 0, 0))
        else:
            # Dim the matching pixel so mismatches stand out.
            out.append(a_rgb[i] // 3)
            out.append(a_rgb[i + 1] // 3)
            out.append(a_rgb[i + 2] // 3)
    write_png(out_path, aw, ah, bytes(out))


def _relative_luminance(r: int, g: int, b: int) -> float:
    def channel(c: int) -> float:
        s = c / 255.0
        return s / 12.92 if s <= 0.03928 else ((s + 0.055) / 1.055) ** 2.4

    return 0.2126 * channel(r) + 0.7152 * channel(g) + 0.0722 * channel(b)


def sample_mean_rgb(
    path: Path,
    *,
    x: int,
    y: int,
    width: int,
    height: int,
) -> tuple[int, int, int]:
    """Mean RGB of a rectangle inside a PNG (top-left origin)."""
    img_w, img_h, rgb = read_png(path)
    if x < 0 or y < 0 or width <= 0 or height <= 0:
        raise ValueError("sample rectangle must be positive and in-bounds")
    if x + width > img_w or y + height > img_h:
        raise ValueError(
            f"sample {x},{y} {width}x{height} outside image {img_w}x{img_h}",
        )
    total_r = total_g = total_b = 0
    count = 0
    for row in range(y, y + height):
        start = (row * img_w + x) * 3
        for _col in range(width):
            total_r += rgb[start]
            total_g += rgb[start + 1]
            total_b += rgb[start + 2]
            start += 3
            count += 1
    return total_r // count, total_g // count, total_b // count


def contrast_ratio(fg: tuple[int, int, int], bg: tuple[int, int, int]) -> float:
    """WCAG 2 relative-luminance contrast ratio."""
    l1 = _relative_luminance(*fg)
    l2 = _relative_luminance(*bg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def _patch_mean_abs_diff(
    haystack_rgb: bytes,
    hay_w: int,
    needle_rgb: bytes,
    needle_w: int,
    needle_h: int,
    *,
    x: int,
    y: int,
) -> float:
    total = 0
    count = 0
    for ny in range(needle_h):
        hay_off = ((y + ny) * hay_w + x) * 3
        needle_off = (ny * needle_w) * 3
        for _nx in range(needle_w):
            total += (
                abs(haystack_rgb[hay_off] - needle_rgb[needle_off])
                + abs(haystack_rgb[hay_off + 1] - needle_rgb[needle_off + 1])
                + abs(haystack_rgb[hay_off + 2] - needle_rgb[needle_off + 2])
            )
            hay_off += 3
            needle_off += 3
            count += 3
    return total / float(count) if count else 0.0


def find_template(
    haystack_rgb: bytes,
    hay_w: int,
    hay_h: int,
    needle_rgb: bytes,
    needle_w: int,
    needle_h: int,
    *,
    max_diff: int = 8,
) -> tuple[int, int] | None:
    """Return top-left ``(x, y)`` of the best template match within ``max_diff``."""
    if needle_w > hay_w or needle_h > hay_h:
        return None
    best: tuple[int, int] | None = None
    best_score = float("inf")
    for y in range(hay_h - needle_h + 1):
        for x in range(hay_w - needle_w + 1):
            score = _patch_mean_abs_diff(
                haystack_rgb,
                hay_w,
                needle_rgb,
                needle_w,
                needle_h,
                x=x,
                y=y,
            )
            if score <= max_diff and score < best_score:
                best = (x, y)
                best_score = score
    return best
