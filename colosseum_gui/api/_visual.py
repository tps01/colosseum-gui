"""Shared visual helpers for web and desktop APIs (no evidence decorators)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

from colosseum.context import get_context
from colosseum.decorators import VerificationResult, missing_measurement_result
from colosseum.output.artifacts import register_artifact, resolve_artifact_path

from colosseum_gui.visual import (
    contrast_ratio,
    pixel_diff_ratio,
    sample_mean_rgb,
    write_diff_png,
)


def save_screenshot_artifact(
    backend: Any,  # noqa: ANN401
    *,
    path: str,
    kind: str,
) -> Path:
    artifact = cast(Path, resolve_artifact_path(path))
    backend.capture_screenshot(path=artifact)
    meta = backend.capture_meta()
    meta_path = artifact.with_suffix(artifact.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8")
    register_artifact(kind, artifact, description=f"{kind} screenshot")
    register_artifact(f"{kind}_meta", meta_path, description=f"{kind} capture metadata")
    return artifact


def save_tree_artifact(backend: Any, *, path: str, kind: str) -> Path:  # noqa: ANN401
    artifact = cast(Path, resolve_artifact_path(path))
    tree = backend.capture_tree()
    artifact.write_text(json.dumps(tree, indent=2, sort_keys=True), encoding="utf-8")
    register_artifact(kind, artifact, description=f"{kind} tree dump")
    return artifact


def resolve_shot(path: str) -> Path:
    candidate = Path(path)
    if candidate.is_file():
        return candidate
    return cast(Path, resolve_artifact_path(path))


def measure_contrast_ratio_from_path(
    *,
    path: str,
    fg_x: int,
    fg_y: int,
    fg_w: int,
    fg_h: int,
    bg_x: int,
    bg_y: int,
    bg_w: int,
    bg_h: int,
) -> float:
    shot = resolve_shot(path)
    fg = sample_mean_rgb(shot, x=fg_x, y=fg_y, width=fg_w, height=fg_h)
    bg = sample_mean_rgb(shot, x=bg_x, y=bg_y, width=bg_w, height=bg_h)
    return float(contrast_ratio(fg, bg))


def verify_visual_paths(
    *,
    path: str,
    baseline: str,
    max_diff_ratio: float = 0.01,
    threshold: int = 16,
    optional: bool = False,
) -> VerificationResult:
    actual = resolve_shot(path)
    base = Path(baseline)
    if not base.is_file():
        return VerificationResult(
            status="ERROR",
            message=f"baseline not found: {baseline}",
            optional=optional,
        )
    try:
        ratio = pixel_diff_ratio(actual, base, threshold=threshold)
    except ValueError as exc:
        return VerificationResult(status="ERROR", message=str(exc), optional=optional)
    if ratio <= max_diff_ratio:
        return VerificationResult(status="PASS", message="", optional=optional, actual=ratio)
    diff_path = actual.with_name(actual.stem + "_diff.png")
    try:
        write_diff_png(actual, base, diff_path)
        register_artifact("gui_visual_diff", diff_path, description="visual regression diff")
    except Exception:  # noqa: BLE001 - diff is best-effort
        pass
    return VerificationResult(
        status="FAIL",
        message=f"diff ratio {ratio:.4f} exceeds max {max_diff_ratio}",
        optional=optional,
        actual=ratio,
    )


def verify_contrast_key(
    *,
    key: str,
    command_candidates: tuple[str, ...],
    minimum: float = 4.5,
    optional: bool = False,
) -> VerificationResult:
    ctx = get_context()
    row = None
    for command in command_candidates:
        row = ctx.db.get_measurement("gui", command, key, row_index=0)
        if row is not None:
            break
    if row is None or row.value is None:
        return missing_measurement_result(key=key, optional=optional)
    actual = float(str(row.value))
    if actual >= minimum:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message=f"contrast {actual:.2f} below minimum {minimum}",
        optional=optional,
        actual=actual,
    )
