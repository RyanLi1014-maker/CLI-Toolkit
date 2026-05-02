"""Exceptions collection for CLI-Toolkit."""


# CLI-Toolkit exceptions========================================================
class CLITError(Exception):
    """Custom exception class for CLI-Toolkit."""


class CLITWarning(Warning):
    """Custom warning class for CLI-Toolkit."""


# Plugin errors==================================================================
class PluginError(CLITError):
    """Custom error class for plugin-related errors."""


class PluginDisabledError(PluginError):
    """Error raised when a plugin is disabled."""


class PluginNotFoundError(PluginError):
    """Error raised when a plugin is not found."""


class PluginNotDisabledError(PluginError):
    """Raised when enabling a plugin that is not in the disabled list."""


# Plugin warnings================================================================
class PluginWarning(Warning):
    """Custom warning class for plugin-related warnings."""


class PluginAlreadyLoadedWarning(PluginWarning):
    """Warning raised when a plugin is already loaded."""
