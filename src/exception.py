"""Exceptions collection for CLI-Toolkit."""


# CLI-Toolkit exceptions========================================================
class CLITException(Exception):
    """Custom exception class for CLI-Toolkit."""

    pass


class CLITWarning(Warning):
    """Custom warning class for CLI-Toolkit."""

    pass


# Plugin errors==================================================================
class PluginError(CLITException):
    """Custom error class for plugin-related errors."""

    pass


class PluginDisabledError(PluginError):
    """Error raised when a plugin is disabled."""

    pass


class PluginNotFoundError(PluginError):
    """Error raised when a plugin is not found."""

    pass


# Plugin warnings================================================================
class PluginWarning(Warning):
    """Custom warning class for plugin-related warnings."""

    pass


class PluginAlreadyLoadedWarning(PluginWarning):
    """Warning raised when a plugin is already loaded."""

    pass
