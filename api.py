"""API for plugins in the CLI-Toolkit application."""

from inspect import currentframe
from logging import getLogger

logger = getLogger("clit.plugin")


class BasePlugin:
    """Base class for plugins in the CLI-Toolkit application."""

    VERSION: tuple[int, int, int] = (0, 0, 0)

    def __init__(self, master) -> None:
        """Initialize the plugin.

        Args:
            master: A reference to the main application,
                can be used by plugins to interact with the application.

        """
        # Application version
        self.APP_VERSION = master.VERSION

        # Reference to the console
        self.console = master.console

        # Resolve the name of the plugin and set the logger
        frame = currentframe()
        plugin_name = "BasePlugin"  # Default fallback
        # Walk up the call stack to find the plugin file that instantiated this class
        while frame:
            # Get the module name from the frame's globals
            module_name = frame.f_globals.get("__name__", "")
            # Check if this is a plugin module (not api or other core modules)
            if module_name and module_name not in ("api", "__main__", "builtins"):
                # Extract just the plugin name (last part of module path)
                plugin_name = module_name.split(".")[-1]
                break
            # Move to the caller's frame
            frame = frame.f_back
        # Set the logger
        self.logger = logger.getChild(plugin_name)
