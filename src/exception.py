"""Exceptions collection for CLI-Toolkit."""


# CLI-Toolkit exceptions========================================================
class CLITError(Exception):
    """Custom exception class for CLI-Toolkit."""


# Plugin errors==================================================================
class PluginError(CLITError):
    """Custom error class for plugin-related errors."""


class PluginDisabledError(PluginError):
    """Error raised when a plugin is disabled."""


class PluginNotDisabledError(PluginError):
    """Raised when enabling a plugin that is not in the disabled list."""


class PluginNotFoundError(PluginError):
    """Error raised when a plugin is not found."""


class PluginLoadedError(PluginError):
    """Error raised when a plugin is unexpectedly already loaded."""
