"""Unit-tier pytest fixtures."""

from __future__ import annotations

from typing import TYPE_CHECKING

import colosseum.context as context_module
import pytest
from colosseum.config import load_config
from colosseum.plugins.loader import ensure_plugins_loaded

if TYPE_CHECKING:
    from collections.abc import Iterator
    from pathlib import Path


@pytest.fixture
def ctx(tmp_path: Path) -> Iterator[context_module.RuntimeContext]:
    ctx = context_module.init_context(test_case_name="gui_unit")
    ctx.output_dir = tmp_path
    ctx.db.initialize(tmp_path / "execution.sqlite")
    ensure_plugins_loaded(ctx.plugin_registry)
    try:
        yield ctx
    finally:
        from colosseum_gui.connections import close_all

        close_all()
        ctx.db.close()


@pytest.fixture
def gui_config(tmp_path: Path) -> Path:
    path = tmp_path / "config.toml"
    path.write_text(
        """
[[gui.web]]
web_id = 1
driver = "sim"
url = "http://example.test/"

[[gui.desktop]]
desktop_id = 1
driver = "sim"
title = "SimWindow"
""",
        encoding="utf-8",
    )
    return path


@pytest.fixture
def loaded(ctx: context_module.RuntimeContext, gui_config: Path) -> context_module.RuntimeContext:
    load_config(str(gui_config))
    return ctx
