"""GUI plugin exceptions."""


class GuiError(RuntimeError):
    """Base error for colosseum-gui."""


class GuiConnectionError(GuiError):
    """Raised when a web or desktop surface cannot be opened."""


class GuiCapabilityError(GuiError):
    """Raised when a high-level API is not supported by the configured driver."""
