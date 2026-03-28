# Plugin Development

CLI-Toolkit provides a plugin system that allows you to add new commands to the CLI-Toolkit. You can add new commands to the CLI-Toolkit by register your commands as several lines of code.

## Contents

- [Plugin Development](#plugin-development)
  - [Contents](#contents)
- [First step](#first-step)
  - [Define a main class in the plugin file](#define-a-main-class-in-the-plugin-file)
  - [Let's add more arguments](#lets-add-more-arguments)
  - [I want to register a version number](#i-want-to-register-a-version-number)
- [More gracefully printing](#more-gracefully-printing)
  - [Print the information gracefully](#print-the-information-gracefully)
  - [I want to know the progress of a long-running task](#i-want-to-know-the-progress-of-a-long-running-task)
- [Advanced functions](#advanced-functions)
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

## I want to register a version number

CLI-Toolkit provides a simple way to register a version number for your plugin. You can register a version number for your plugin by setting the `VERSION` attribute of the plugin class.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.message import *  # Import the message utility functions


class Plugin(BasePlugin):
    """Description of the plugin."""

    VERSION = "1.2.3"

    def cmd_my_command(self, _): ...

```

In this example, we registered the version number `1.2.3` for our plugin.

If you want to know the version of the main application and loaded plugins, you can use the `version` command to see them.

# More gracefully printing

Have you ever hate the white and ugly output `print` function? CLI-Toolkit provides several functions to print information in a more user-friendly way. These functions will display the messages with appropriate colors and formatting to enhance readability.

## Print the information gracefully

CLI-Toolkit provides several functions to print information in a more user-friendly way. You can use these functions in your plugin to enhance the user experience.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.message import *  # Import the message utility functions


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_show_message(self, _):
        """Description of my_command."""
        show_info("MyPlugin", "This is an information message.", "Detail message...")
        show_success("MyPlugin", "This is a success message.", "Detail message...")
        show_warning("MyPlugin", "This is a warning message.", "Detail message...")
        show_error("MyPlugin", "This is an error message.", "Detail message...")

```

In this example, we used the `show_info`, `show_warning`, `show_error`, and `show_success` functions to print different types of messages. These functions will display the messages with appropriate colors and formatting to enhance readability.

- The first parameter is the category of the message, which will be displayed in the message box. You must provide a category for the message.
- The second parameter is the title of the message, which will be displayed in the message box.
- The third parameter is the detail message, which will be displayed in the message box.

## I want to know the progress of a long-running task

CLI-Toolkit provides a simple way to show the progress of a long-running task. You can use the `message` module to show the progress of a long-running task.

```python
import time  # Import the time module to simulate a long-running task

from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.message import *  # Import the message utility functions


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_long_running_task(self, _):
        """Show the progress of a long-running task."""
        progress_bar = ProgressBar(
            "TASK",  # The category of the progress bar
            100,  # The total number of steps
            "Progressing...",  # The describe of the progress bar
            1,  # Number of decimals in percent complete.
            50,  # The length of the progress bar
            "#",  # The character to use to build the progress bar
            "-",  # The character to use to fill the progress bar
        )  # Create a progress bar
        for _ in range(100):
            time.sleep(0.05)  # Simulate a long-running task
            progress_bar.update()  # Update the progress bar

```

In this example, we use the `ProgressBar` class to show the progress of a long-running task. The `ProgressBar` class has a `update` method that updates the progress bar.

The `ProgressBar` class can be customized by setting parameters. For details, please refer to the `ProgressBar` class.

The `update` method can be called multiple times to update the progress bar by one step or specific number of steps. When the progress bar reaches the end, it will automatically stop and delete itself.

If you want to stop the progress bar manually, you can use the `stop` method. Or you can use the `complete` method to complete and stop the progress bar manually.

# Advanced functions

After learning the basic usage of the plugin system, you may want to know more advanced functions. CLI-Toolkit provides several advanced functions that can be used in your plugin, such as manipulating the main application, read & write the config file, etc.

## What if I can manipulate the main application?

In the plugin system of CLI-Toolkit, the `Plugin` class's `__init__` method receives a reference to the main application (the `master` parameter).

This allows you to interact with the main application from your plugin, enabling you to perform more complex actions and integrate your plugin more deeply with the application.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.message import *  # Import the message utility functions


class Plugin(BasePlugin):
    """Description of the plugin."""

    def cmd_show_unknown(self, args: list):
        """Show unknown command."""
        self.master.show_unknown_cmd(
            args
        )  # Call the main application's method to show unknown command message

    def cmd_show_version(self, _):
        """Show the version of the main application."""
        show_info(
            "MyPlugin",
            "This is the version of the main application:",
            self.master.VERSION,
        )

```

In this example, we added two commands to the plugin: `cmd_show_unknown` and `cmd_show_version`.

The `cmd_show_unknown` command will use the `show_unknown_cmd` method of the main application to show an unknown command message. The `cmd_show_version` command will print the version of the main application. You can also use the `VERSION` constant of the main application to get the version of the main application and tell whether the plugin is compatible with the main application.

This demonstrates how you can use the `master` reference to interact with the main application and utilize its functionality in your plugin.

## More actions on the `__init__` method

You can also override the `__init__` method of the `Plugin` class to perform some initialization actions when the plugin is loaded. The `__init__` method will receive a reference to the main application, which can be used to interact with the application.

```python
from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.message import *  # Import the message utility functions


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
        show_info("MyPlugin", "Plugin initialized!")

    def cmd_my_command(self, _): ...

```

In this example, we override the `__init__` method to perform some initialization actions when the plugin is loaded. We call the parent class's `__init__` method to initialize the `master` reference, and then we use the `show_info` function to display a message indicating that the plugin has been initialized.

In actual development, you can use `__init__` to perform more complex initialization actions, such as setting up connections, loading resources, or registering event handlers with the main application.

## How can I save the configuration?

CLI-Toolkit provides a simple way to save the configuration of your plugin. You can use the `config` module to save the configuration of your plugin.

```python
from pathlib import Path  # Import the Path class from the pathlib module

from src.plugin import BasePlugin  # Import the BasePlugin class from the plugin module
from src.util.config import Config
from src.util.message import *  # Import the message utility functions


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
        show_info("MyPlugin", "Plugin initialized!")

    def cmd_show_config(self, _):
        """Show the configuration."""
        print(self.config)  # Print the configuration

    def cmd_set_config(self, args):
        """Set the configuration."""
        self.config[args[0]] = args[1]  # Set the value of the key
        self.config.save()  # Save the configuration

```

In this example, we use the `Config` class to save the configuration of our plugin. The `config_path` parameter specifies the path to the configuration file, and the `default_config` parameter specifies the default configuration.

The `config` class has a `load` method that loads the configuration from the configuration file, and a `save` method that saves the configuration to the configuration file.

The `config` class is based on the `dict` class, so you can use all the methods and properties of the `dict` class.
