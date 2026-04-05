# Plugin Development

CLI-Toolkit provides a plugin system that allows you to add new commands to the CLI-Toolkit. You can add new commands to the CLI-Toolkit by register your commands as several lines of code.

## Contents

- [Plugin Development](#plugin-development)
  - [Contents](#contents)
- [First step](#first-step)
  - [Define a main class in the plugin file](#define-a-main-class-in-the-plugin-file)
  - [Let's add more arguments](#lets-add-more-arguments)
- [Standardized output](#standardized-output)
  - [Register a version number](#register-a-version-number)
  - [Standardized printing](#standardized-printing)
  - [Logging](#logging)
- [Advanced features](#advanced-features)
  - [What if I can manipulate the main application?](#what-if-i-can-manipulate-the-main-application)
  - [More actions on the `__init__` method](#more-actions-on-the-__init__-method)
  - [How can I save the configuration?](#how-can-i-save-the-configuration)

# First step

Create a new Python file in the `plugin` directory. The file name will be the plugin name (e.g., `my_plugin.py`).
If you can't find the `plugin` directory in the root directory of the project, you can try to run the application first, and the directory will be automatically created.

## Define a main class in the plugin file

Define a class named `Plugin` in your plugin file. This class will contain the methods that you want to add to the CLI-Toolkit.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_my_command(self, _):
        """Description of my_command."""
        print("This is my command!")

```

In this example, we defined a command method `cmd_my_command` that will be added to the CLI-Toolkit. The method name must start with `cmd_` to be recognized as a command.

During running the command, CLI-Toolkit will call this method and pass a list of arguments to it (in this example, we ignore the arguments by using `_`).

To run the command, enter `my_command` in the CLI-Toolkit after loading the plugin.

## Let's add more arguments

Now you have already defined a command method in your plugin. You can also add arguments to the command method to make it more useful. The `args` parameter will contain a list of arguments passed to the command.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_my_command(self, args: list):
        """Description of my_command."""
        print("This is my command!")
        print("Arguments passed to the command:", args)

```

In this example, we added an `args` parameter to the `cmd_my_command` method. When you run the command with arguments (e.g., `my_command arg1 arg2`), the `args` parameter will contain a list of the arguments passed to the command (in this case, `['arg1', 'arg2']`).

# Standardized output

After finishing your first plugin, you may want to learn how to writing a plugin with a standardized output. Standardized output is an important requirement for plugin development. If your plugin doesn't have a standardized output, users will not be able to understand the output of your plugin. So, let's learn how to write a plugin with a standardized output.

## Register a version number

CLI-Toolkit provides a simple way to register a version number for your plugin. You can register a version number for your plugin by setting the `VERSION` attribute of the plugin class.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    VERSION = "1.2.3"

    def cmd_my_command(self, _): ...

```

In this example, we registered the version number `1.2.3` for our plugin.

If you want to know the version of the main application and loaded plugins, you can use the `version` command to see them.

## Standardized printing

CLI-Toolkit provides a simple way to print messages to the console. You can print messages to the console by using the `print` method of the `self.master.console` object.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    VERSION = "1.2.3"

    def cmd_print(self, _):
        """Log messages."""
        self.master.console.print("This is a message.")
        self.master.console.print("This is a red message.", style="red")
        self.master.console.print("This is a bold green message.", style="bold green")
        self.master.console.print("This is a italic blue message.", style="italic blue")
        self.master.console.print(
            "This is a underline yellow message.", style="underline yellow"
        )
        self.master.console.print("This is a red [red]word[/red].")
        self.master.console.print("This is a bold green [bold green]word[/bold green].")
        self.master.console.print("This is a italic blue [italic blue]word[/italic blue].")
        self.master.console.print(
            "This is a underline yellow [underline yellow]word[/underline yellow]."
        )

```

In this example, we printed some messages to the console. The `style` parameter is used to set the style of the message. You can also use labels to style the message. For example, you can use `[red]` to set the style of the message to red and `[/red]` to cancel the style. For more information, please refer to the [rich](https://github.com/Textualize/rich) module documentation.

## Logging

CLI-Toolkit provides a simple way to log messages to `log/CLI-Toolkit.log`. You can log messages to the file by using the `info`, `warning`, `error`, `debug`, `critical` methods of the `self.master.logger` object.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    VERSION = "1.2.3"

    def cmd_log(self, _):
        """Log messages."""
        self.master.logger.debug("This is a debug message.")
        self.master.logger.info("This is an info message.")
        self.master.logger.warning("This is a warning message.")
        self.master.logger.error("This is an error message.")
        self.master.logger.critical("This is a critical message.")

```

In this example, we logged some messages to the file.

**_Precaution: The debug level is the lowest level, which won't be recorded in the file. If you want to record debug messages, you need to set the log level in the source code._**

# Advanced features

After learning the basic usage of the plugin system, you may want to know more advanced functions. CLI-Toolkit provides several advanced functions that can be used in your plugin, such as manipulating the main application, read & write the config file, etc.

## What if I can manipulate the main application?

In the previous examples, we have seen an object named `self.master`. This object is a reference to the main application, which can be used to interact with the application.

There is a list of objects that can be used in your plugin:

- `self.master.console`: A reference to the console object, which can be used to interact with the console. This object is based on the `Console` class in the [rich](https://github.com/Textualize/rich) module. For more information, please refer to the [Using the Console](https://github.com/Textualize/rich?tab=readme-ov-file#using-the-console) section of the [rich](https://github.com/Textualize/rich) module.
- `self.master.logger`: A reference to the logger object, which can be used to log messages to the console. This object is based on the `Logger` class in the Python standard library `logging`.
- `self.master.config`: A reference to the main application config object, which can be used to read & write the main application config file.
- `self.master.plugin_manager`: A reference to the plugin manager object, which can be used to load & unload plugins.

## More actions on the `__init__` method

You can also override the `__init__` method of the `Plugin` class to perform some initialization actions when the plugin is loaded. The `__init__` method will receive a reference to the main application, which can be used to interact with the application.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module


class Plugin(BasePlugin):
    """Description of the plugin."""

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
        """
        super().__init__(
            master
        )  # Call the parent class's __init__ method to initialize the master reference
        self.master.console.print("Plugin initialized!")

    def cmd_my_command(self, _): ...

```

In this example, we override the `__init__` method to perform some initialization actions when the plugin is loaded. We call the parent class's `__init__` method to initialize the `master` reference.

In actual development, you can use `__init__` to perform more complex initialization actions, such as setting up connections, loading resources, or registering event handlers with the main application.

## How can I save the configuration?

CLI-Toolkit provides a simple way to save the configuration of your plugin. You can use the `config` module to save the configuration of your plugin.

```python
from pathlib import Path  # Import the Path class from the pathlib module

from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.config import Config


class Plugin(BasePlugin):
    """Description of the plugin."""

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
        """
        super().__init__(
            master
        )  # Call the parent class's __init__ method to initialize the master reference
        self.config = Config(
            config_path=Path("my_plugin.json"),  # The path to the configuration file
            default_config={  # The default configuration
                "key1": "value1",
                "key2": {"key3": "value3"},
            },
        )
        self.config.load()  # Load the configuration
        self.master.console.print("Config loaded!")

    def cmd_show_config(self, _):
        """Show the configuration."""
        print(self.config)  # Print the configuration

    def cmd_set_config(self, args):
        """Set the configuration."""
        if len(args) < 2:  # Check if the number of arguments is less than 2
            self.master.logger.warning("Usage: set_config <key> <value>")
            return
        self.config[args[0]] = args[1]  # Set the value of the key
        self.config.save()  # Save the configuration

```

In this example, we use the `Config` class to save the configuration of our plugin. The `config_path` parameter specifies the path to the configuration file, and the `default_config` parameter specifies the default configuration.

The `config` class has a `load` method that loads the configuration from the configuration file, and a `save` method that saves the configuration to the configuration file.

The `config` class is based on the `dict` class, so you can use all the methods and properties of the `dict` class.
