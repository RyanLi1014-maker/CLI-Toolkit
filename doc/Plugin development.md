# Plugin Development

CLI-Toolkit includes a plugin system that makes it easy to add new commands. You can register plugin commands with just a few lines of code.

## Contents

- [Plugin Development](#plugin-development)
  - [Contents](#contents)
- [Getting Started](#getting-started)
  - [Creating Your First Plugin](#creating-your-first-plugin)
  - [Adding Arguments to Commands](#adding-arguments-to-commands)
- [Enhancing Your Plugin](#enhancing-your-plugin)
  - [Registering a Version Number](#registering-a-version-number)
  - [Standardized Printing](#standardized-printing)
  - [Logging Messages](#logging-messages)
  - [Saving Configuration](#saving-configuration)
- [Advanced Features](#advanced-features)
  - [Custom Initialization](#custom-initialization)
  - [Interacting with the Main Application](#interacting-with-the-main-application)

# Getting Started

Create a new Python file in the `plugin` directory. The file name becomes the plugin name (for example, `my_plugin.py`).
If the `plugin` directory does not exist in the project root yet, run the application once and it will be created automatically.

## Creating Your First Plugin

Define a class named `Plugin` in your plugin file. This class contains the methods that CLI-Toolkit will expose.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_my_command(self, _):
        """Description of my_command."""
        print("This is my command!")
```

In this example, the command method `cmd_my_command` will be added to CLI-Toolkit. The method name must start with `cmd_` to be recognized as a command.

When you run the command, CLI-Toolkit calls this method and passes a list of arguments to it. In this example, the arguments are ignored by using `_`.

To run the command, enter `my_command` after loading the plugin.

## Adding Arguments to Commands

Now that you have defined a command method in your plugin, you can accept arguments to make it more useful. The `args` parameter contains a list of the arguments passed to the command.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_my_command(self, args: list):
        """Description of my_command."""
        print("This is my command!")
        print("Arguments passed to the command:", args)
```

In this example, the `args` parameter receives the arguments passed to `cmd_my_command`. For example, when you run `my_command arg1 arg2`, `args` will contain `['arg1', 'arg2']`.

Of course, using the `print` function is not recommended because it does not support formatting. CLI-Toolkit provides a `self.console.print` method that supports formatting. If you need to use the `print` function, you should use the `self.console.print` method instead.

# Enhancing Your Plugin

After creating your first plugin, you may want to use standardized output. Consistent output makes plugins easier for users to understand. The sections below show how to add versioning, format console output, and log messages.

## Registering a Version Number

CLI-Toolkit supports plugin versioning through the plugin class's `VERSION` attribute.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    VERSION = (1, 2, 3)  # Register the version number for the plugin

    def cmd_my_command(self, _):
        ...
```

In this example, the plugin version is `1.2.3`.

If you want to see the version of the main application and loaded plugins, use the `version` command. If there is no version number registered, CLI-Toolkit will display `0.0.0` on `version` command.

## Standardized Printing

CLI-Toolkit provides a simple way to print styled messages to the console. Use the `self.console.print` method to display output.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_print(self, _):
        """Print messages."""
        self.console.print("This is a message.")
        self.console.print("This is a red message.", style="red")
        self.console.print("This is a bold green message.", style="bold green")
        self.console.print("This is an italic blue message.", style="italic blue")
        self.console.print(
            "This is an underlined yellow message.", style="underline yellow"
        )
        self.console.print("This is a red [red]word[/red].")
        self.console.print("This is a bold green [bold green]word[/bold green].")
        self.console.print("This is an italic blue [italic blue]word[/italic blue].")
        self.console.print(
            "This is an underlined yellow [underline yellow]word[/underline yellow]."
        )
```

In this example, the `style` parameter controls the message appearance. You can also use markup tags such as `[red]` and `[/red]` to apply inline styles. For more details, see the [rich](https://github.com/Textualize/rich) documentation.

## Logging Messages

CLI-Toolkit provides a logger instance for plugins. Using the main application logger is convenient, but it is often better to create a plugin-specific logger. A separate logger makes debugging easier and avoids cluttering the main application logs.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_log(self, _):
        """Log messages."""
        self.logger.debug("This is a debug message.")
        self.logger.info("This is an info message.")
        self.logger.warning("This is a warning message.")
        self.logger.error("This is an error message.")
        self.logger.critical("This is a critical message.")
```

In this example, the plugin uses its own logger instance.

**_Note: Debug-level messages are the lowest level and may not be written to the log file unless the logging level is configured to include debug output._**

## Saving Configuration

CLI-Toolkit provides a simple way to save plugin configuration using the `config` module.

```python
from pathlib import Path  # Import the Path class from the pathlib module

from api import BasePlugin  # Import the BasePlugin class from the api module
from util.config import DictConfig


class Plugin(BasePlugin):
    """Description of the plugin."""

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, which plugins can use to interact with the app.
        """
        super().__init__(master)
        self.config = DictConfig(
            config_path=Path("my_plugin.json"),
            default_config={
                "key1": "value1",
                "key2": {"key3": "value3"},
            },
        )
        self.console.print("Config loaded!")

    def cmd_show_config(self, _):
        """Show the configuration."""
        self.console.print(self.config)

    def cmd_set_config(self, args):
        """Set the configuration."""
        if len(args) < 2:
            self.master.logger.warning("Usage: set_config <key> <value>")
            return
        self.config[args[0]] = args[1]
        self.config.save()
```

In this example, `DictConfig` stores the plugin configuration. The `config_path` parameter specifies the file path, and `default_config` provides default values.

`DictConfig` has a `load` method to read configuration from the file and a `save` method to write it back.

Because `DictConfig` is based on `dict`, you can use all standard dictionary methods and properties.

# Advanced Features

Once you understand the basic plugin workflow, you can use more advanced features such as interacting with the main application and saving plugin configuration.

## Custom Initialization

You can override the `__init__` method of the `Plugin` class to perform initialization when the plugin is loaded. The constructor receives a reference to the main application.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, which plugins can use to interact with the app.
        """
        super().__init__(master)
        self.console.print("Plugin initialized!")

    def cmd_my_command(self, _):
        ...
```

In this example, `__init__` performs initialization when the plugin loads and stores the `master` reference. If you want to access the main application from a plugin, you can use the `master` reference.

In practice, `__init__` can be used to set up resources, initialize connections, or register event handlers with the main application.

## Interacting with the Main Application

CLI-Toolkit provides a `master` reference to the main application in the plugin constructor. This reference can be used to interact with the main application, such as registering event handlers or accessing the configuration. If you want to access the main application from a plugin, you must save the `master` reference as the plugin instance attribute in `__init__` method. Here is an example.

```python
from api import BasePlugin  # Import the BasePlugin class from the api module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def __init__(self, master):
        """Initialize the plugin."""
        super().__init__(master)
        self.master = master

    def cmd_show_master(self, _):
        """Show the master object."""
        self.console.print(self.master)
```

In this example, the `show_master` command prints the `master` object. The `master` object provides access to the main application, which can be used to interact with the attributes and methods of the main application. Such as `master.config`, `master.logger`, `master.plugin_manager`.
