"""API for plugins in the CLI-Toolkit application."""

# Import modules
from inspect import currentframe  # Get the current frame
from logging import getLogger  # Get the logger

logger = getLogger("Plugin")


class BasePlugin:
    """Base class for plugins in the CLI-Toolkit application."""

    VERSION: tuple[int, int, int] = (0, 0, 0)  # Version number of the plugin

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
        """
        # Application version
        self.APP_VERSION = master.VERSION

        # Reference to the console
        self.console = master.console

        # Resolve the name of the plugin and set the logger
        frame = currentframe()
        self.logger = logger.getChild(frame.f_code.co_name if frame else "BasePlugin")
