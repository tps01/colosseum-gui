"""Desktop GUI APIs (``col.gui.desktop``)."""

from __future__ import annotations

import time

from colosseum.decorators import VerificationResult, command, measurement, verification

from colosseum_gui.api import _visual
from colosseum_gui.connections import get_desktop

__all__ = [
    "connect",
    "click",
    "type_text",
    "press_key",
    "hover",
    "wait",
    "wait_stable",
    "capture_screenshot",
    "capture_tree",
    "measure_action_latency_ms",
    "measure_contrast_ratio",
    "verify_text",
    "verify_visible",
    "verify_enabled",
    "verify_visual",
    "verify_contrast",
]


@command
def connect(*, desktop_id: int) -> None:
    """Open (or reuse) a configured desktop surface.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int

    :returns: None

    :raises GuiConnectionError: Desktop backend could not be opened.
    :raises OSError: ``driver=pywinauto`` on a non-Windows host.
    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_desktop(desktop_id)


@command
def click(
    *,
    desktop_id: int,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
    input: str | None = None,
    css: str | None = None,
    xpath: str | None = None,
    test_id: str | None = None,
) -> None:
    """Click a control (generic: image/coords; pywinauto: AutomationId/Name).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param role: UIA control role/type (``driver=pywinauto`` / sim).
    :type role: str | None
    :param name: Accessible name (``driver=pywinauto`` / sim).
    :type name: str | None
    :param automation_id: UIA AutomationId (``driver=pywinauto`` / sim).
    :type automation_id: str | None
    :param image: Template PNG path for best-effort image click (``generic`` / sim).
    :type image: str | None
    :param x: Screen or window X for coordinate click.
    :type x: float | None
    :param y: Screen or window Y for coordinate click.
    :type y: float | None
    :param input: ``invoke`` (UIA default) or ``mouse``.
    :type input: str | None
    :param css: Not supported on desktop (web-only); raises ``ValueError``.
    :type css: str | None
    :param xpath: Not supported on desktop (web-only); raises ``ValueError``.
    :type xpath: str | None
    :param test_id: Not supported on desktop (web-only); raises ``ValueError``.
    :type test_id: str | None

    :returns: None

    :raises GuiCapabilityError: Locator requires a different driver.
    :raises ValueError: Web-only locators (css/xpath/test_id) were passed.
    """
    get_desktop(desktop_id).click(
        role=role,
        name=name,
        automation_id=automation_id,
        image=image,
        x=x,
        y=y,
        input=input,
        css=css,
        xpath=xpath,
        test_id=test_id,
    )


@command
def type_text(
    *,
    desktop_id: int,
    text: str,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
    input: str | None = None,
) -> None:
    """Type text into a desktop control or at a click target.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param text: Text to enter.
    :type text: str

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_desktop(desktop_id).type_text(
        text=text,
        role=role,
        name=name,
        automation_id=automation_id,
        image=image,
        x=x,
        y=y,
        input=input,
    )


@command
def press_key(*, desktop_id: int, key: str) -> None:
    """Press a key (best-effort OS input).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param key: Key name (for example ``tab`` or ``enter``).
    :type key: str

    :returns: None
    """
    get_desktop(desktop_id).press_key(key=key)


@command
def hover(
    *,
    desktop_id: int,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> None:
    """Move the pointer over a control or coordinate.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int

    :returns: None

    :raises GuiCapabilityError: Operation not supported by the configured driver.
    """
    get_desktop(desktop_id).hover(
        role=role,
        name=name,
        automation_id=automation_id,
        image=image,
        x=x,
        y=y,
    )


@command
def wait(
    *,
    desktop_id: int,
    until: str,
    timeout_s: float = 10.0,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    text: str | None = None,
) -> None:
    """Wait until a UIA condition holds (``driver=pywinauto`` / sim).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param until: ``visible``, ``enabled``, or ``text``.
    :type until: str
    :param timeout_s: Timeout in seconds.
    :type timeout_s: float

    :returns: None

    :raises GuiCapabilityError: Tree waits are unsupported on ``driver=generic``.
    """
    get_desktop(desktop_id).wait(
        until=until,
        timeout_s=timeout_s,
        role=role,
        name=name,
        automation_id=automation_id,
        text=text,
    )


@command
def wait_stable(*, desktop_id: int, timeout_s: float = 2.0) -> None:
    """Wait until the window screenshot/geometry settles (best-effort).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param timeout_s: Maximum settle time.
    :type timeout_s: float

    :returns: None
    """
    get_desktop(desktop_id).wait_stable(timeout_s=timeout_s)


@command
def capture_screenshot(*, desktop_id: int, path: str) -> None:
    """Capture a window/desktop screenshot and register it as a run artifact.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param path: Path relative to the run output directory.
    :type path: str

    :returns: None
    """
    _visual.save_screenshot_artifact(
        get_desktop(desktop_id), path=path, kind="gui_desktop_screenshot"
    )


@command
def capture_tree(*, desktop_id: int, path: str = "captures/desktop_tree.json") -> None:
    """Dump window list (generic) or UIA tree (pywinauto) as JSON.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param path: Path relative to the run output directory.
    :type path: str

    :returns: None
    """
    _visual.save_tree_artifact(get_desktop(desktop_id), path=path, kind="gui_desktop_tree")


@measurement
def measure_action_latency_ms(
    *,
    desktop_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    image: str | None = None,
    x: float | None = None,
    y: float | None = None,
) -> float:
    """Click a target and measure wall time until the call returns.

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param key: Unique measurement key within domain ``gui``.
    :type key: str

    :returns: Action latency in milliseconds.
    :rtype: float
    """
    _ = key
    backend = get_desktop(desktop_id)
    started = time.perf_counter()
    backend.click(
        role=role,
        name=name,
        automation_id=automation_id,
        image=image,
        x=x,
        y=y,
    )
    return (time.perf_counter() - started) * 1000.0


@measurement
def measure_contrast_ratio(
    *,
    desktop_id: int,
    key: str,
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
    """Sample two rectangles from a prior screenshot and measure WCAG contrast.

    :param desktop_id: Unused for sampling; kept for kind symmetry.
    :type desktop_id: int
    :param key: Unique measurement key within domain ``gui``.
    :type key: str
    :param path: Screenshot path relative to the run output directory.
    :type path: str

    :returns: Contrast ratio.
    :rtype: float
    """
    _ = (desktop_id, key)
    return _visual.measure_contrast_ratio_from_path(
        path=path,
        fg_x=fg_x,
        fg_y=fg_y,
        fg_w=fg_w,
        fg_h=fg_h,
        bg_x=bg_x,
        bg_y=bg_y,
        bg_w=bg_w,
        bg_h=bg_h,
    )


@verification
def verify_text(
    *,
    desktop_id: int,
    key: str,
    expected: str,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify control text equals ``expected`` (``pywinauto`` / sim).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param key: Verification key.
    :type key: str
    :param expected: Expected text.
    :type expected: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult

    :raises GuiCapabilityError: Unsupported on ``driver=generic``.
    """
    _ = key
    actual = get_desktop(desktop_id).get_text(
        role=role, name=name, automation_id=automation_id
    )
    if actual == expected:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message=f"expected {expected!r}, got {actual!r}",
        optional=optional,
        actual=actual,
    )


@verification
def verify_visible(
    *,
    desktop_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify a control is visible (``pywinauto`` / sim).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param key: Verification key.
    :type key: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult

    :raises GuiCapabilityError: Unsupported on ``driver=generic``.
    """
    _ = key
    actual = get_desktop(desktop_id).is_visible(
        role=role, name=name, automation_id=automation_id
    )
    if actual:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message="control is not visible",
        optional=optional,
        actual=actual,
    )


@verification
def verify_enabled(
    *,
    desktop_id: int,
    key: str,
    role: str | None = None,
    name: str | None = None,
    automation_id: str | None = None,
    optional: bool = False,
) -> VerificationResult:
    """Verify a control is enabled (``pywinauto`` / sim).

    :param desktop_id: Configured ``gui.desktop`` id from bench TOML.
    :type desktop_id: int
    :param key: Verification key.
    :type key: str
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult

    :raises GuiCapabilityError: Unsupported on ``driver=generic``.
    """
    _ = key
    actual = get_desktop(desktop_id).is_enabled(
        role=role, name=name, automation_id=automation_id
    )
    if actual:
        return VerificationResult(status="PASS", message="", optional=optional, actual=actual)
    return VerificationResult(
        status="FAIL",
        message="control is not enabled",
        optional=optional,
        actual=actual,
    )


@verification
def verify_visual(
    *,
    key: str,
    path: str,
    baseline: str,
    max_diff_ratio: float = 0.01,
    threshold: int = 16,
    optional: bool = False,
) -> VerificationResult:
    """Compare a desktop screenshot to a baseline PNG.

    :param key: Verification key.
    :type key: str
    :param path: Actual screenshot path.
    :type path: str
    :param baseline: Baseline PNG path.
    :type baseline: str
    :param max_diff_ratio: Maximum allowed differing-pixel fraction.
    :type max_diff_ratio: float
    :param threshold: Per-channel difference threshold.
    :type threshold: int
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    _ = key
    return _visual.verify_visual_paths(
        path=path,
        baseline=baseline,
        max_diff_ratio=max_diff_ratio,
        threshold=threshold,
        optional=optional,
    )


@verification
def verify_contrast(
    *,
    key: str,
    minimum: float = 4.5,
    optional: bool = False,
) -> VerificationResult:
    """Verify a prior ``measure_contrast_ratio`` meets ``minimum``.

    :param key: Measurement key shared with ``measure_contrast_ratio``.
    :type key: str
    :param minimum: Minimum contrast ratio.
    :type minimum: float
    :param optional: When true, FAIL does not fail the run.
    :type optional: bool

    :returns: Pass/fail result.
    :rtype: VerificationResult
    """
    return _visual.verify_contrast_key(
        key=key,
        command_candidates=("desktop.measure_contrast_ratio",),
        minimum=minimum,
        optional=optional,
    )
