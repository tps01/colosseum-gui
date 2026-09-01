"""Colosseum GUI plugin (product UI automation: web and desktop)."""

from importlib import metadata

from colosseum.config.sections import ConfigSectionSpec
from colosseum.logging import get_logger
from colosseum.plugins.registry import PluginRegistry

__colosseum_domain__ = "gui"

try:
    __version__ = metadata.version("colosseum-gui")
except metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0.0.0"

_logger = get_logger("colosseum.gui")

_CONFIG_SPECS = (
    ConfigSectionSpec(
        "gui.web",
        "web_id",
        required_keys=(),
        optional_keys=(
            "driver",
            "url",
            "browser",
            "headed",
            "cdp_url",
            "viewport",
            "timeout_s",
        ),
    ),
    ConfigSectionSpec(
        "gui.desktop",
        "desktop_id",
        required_keys=(),
        optional_keys=(
            "driver",
            "title",
            "exe",
            "process_id",
            "timeout_s",
            "dpi_scale",
            "display",
        ),
    ),
)


def register(registry: PluginRegistry) -> None:
    from colosseum_gui import api
    from colosseum_gui.connections import close_all

    registry.register_namespace("gui", api)
    _logger.debug("Registered col.gui namespace")
    registry.register_shutdown(close_all)
    for spec in _CONFIG_SPECS:
        registry.register_config_section(spec)
