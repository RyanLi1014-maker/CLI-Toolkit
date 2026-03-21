# CLI-Toolkit

A flexible and customizable command-line interface (CLI) application, featuring built-in command handling, colored output, and intuitive user interaction.

## Features

### Currently had

- Clean, modular CLI architecture
- Colored terminal output for better user experience
- `help` command based on smart docstring recognition
- Shell-like command parsing (supports quotes and special characters)
- A very easy-to-develop plugin system

### Todo

- None

# Installation

**_Precautions: The project required Python3.6 or above._**

1. Clone this repository:

   ```
   git clone https://github.com/RyanLi1014-maker/CLI-Toolkit.git
   cd CLI-Toolkit
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Run the Application

Execute the main entry point to start the CLI-Toolkit:

```
python main.py
```

### Basic Commands

| Command | Description                                                             |
| ------- | ----------------------------------------------------------------------- |
| `help`  | Show list of available commands or detailed help for a specific command |
| `exit`  | Exit the application.                                                   |

### Example Workflow

1. Start the application:
   ```
   python main.py
   ```
2. You'll see the CLI-Toolkit logo and welcome message:

   ```
            ________      ___           ___
           |\   ____\    |\  \         |\  \
           \ \  \___|    \ \  \        \ \  \    ____________
            \ \  \        \ \  \        \ \  \  |\____________\
             \ \  \____    \ \  \____    \ \  \ \|____________|
              \ \_______\   \ \_______\   \ \__\
               \|_______|    \|_______|    \|__|

    _________    ________      ________      ___           ___  __        ___      _________
   |\___   ___\ |\   __  \    |\   __  \    |\  \         |\  \|\  \     |\  \    |\___   ___\
   \|___ \  \_| \ \  \|\  \   \ \  \|\  \   \ \  \        \ \  \/  /|_   \ \  \   \|___ \  \_|
        \ \  \   \ \  \\\  \   \ \  \\\  \   \ \  \        \ \   ___  \   \ \  \       \ \  \
         \ \  \   \ \  \\\  \   \ \  \\\  \   \ \  \____    \ \  \\ \  \   \ \  \       \ \  \
          \ \__\   \ \_______\   \ \_______\   \ \_______\   \ \__\\ \__\   \ \__\       \ \__\
           \|__|    \|_______|    \|_______|    \|_______|    \|__| \|__|    \|__|        \|__|

   Welcome to the CLI-Toolkit! Type 'help' to list commands.
   Type 'exit' to exit the application.
   CLI-Toolkit>
   ```

3. Interact with the application:
   - List all commands:
     ```
     CLI-Toolkit> help
     ```
   - Get detailed help for a command:
     ```
     CLI-Toolkit> help [command_name]
     ```
   - Exit the application:
     ```
     CLI-Toolkit> exit
     ```

# Plugin Development

To create a plugin for CLI-Toolkit, follow these steps.

## First step

Create a new Python file in the `plugins` directory. The file name will be the plugin name (e.g., `my_plugin.py`).
If you can't find the `plugins` directory in the root directory of the project, you can try to run the application first, and the directory will be automatically created.

## Define a main class in the plugin file

Define a class named `Plugin` in your plugin file. This class will contain the methods that you want to add to the CLI-Toolkit.

```python
from plugin import BasePlugin # Import the BasePlugin class from the plugin module

class Plugin(BasePlugin):
   """Description of the plugin."""
   def cmd_my_command(self, _):
      """Description of my_command."""
      print("This is my command!")
```

In this example, we defined a command method `cmd_my_command` that will be added to the CLI-Toolkit. The method name must start with `cmd_` to be recognized as a command. During running the command, CLI-Toolkit will call this method and pass a list of arguments to it (in this example, we ignore the arguments by using `_`).
To run the command, enter `my_command` in the CLI-Toolkit after loading the plugin.

## Let's add more arguments

Now you have already defined a command method in your plugin. You can also add arguments to the command method to make it more useful. The `args` parameter will contain a list of arguments passed to the command.

```python
from plugin import BasePlugin # Import the BasePlugin class from the plugin module

class Plugin(BasePlugin):
   """Description of the plugin."""
   def cmd_my_command(self, args: list):
      """Description of my_command."""
      print("This is my command!")
      print("Arguments passed to the command:", args)
```

In this example, we added an `args` parameter to the `cmd_my_command` method. When you run the command with arguments (e.g., `my_command arg1 arg2`), the `args` parameter will contain a list of the arguments passed to the command (in this case, `['arg1', 'arg2']`).

## Print the information gracefully

CLI-Toolkit provides several functions to print information in a more user-friendly way. You can use these functions in your plugin to enhance the user experience.

```python
from plugin import BasePlugin # Import the BasePlugin class from the plugin module
from util.message import * # Import the message utility functions

class Plugin(BasePlugin):
   """Description of the plugin."""
   def cmd_my_command(self, args: list):
      """Description of my_command."""
      show_info("MyPlugin", "This is my command!")
      show_info("MyPlugin", f"Arguments passed to the command: {args}")
      show_warning("MyPlugin", "This is a warning message.")
      show_error("MyPlugin", "This is an error message.")
      show_success("MyPlugin", "Command executed successfully!")
```

In this example, we used the `show_info`, `show_warning`, `show_error`, and `show_success` functions to print different types of messages. These functions will display the messages with appropriate colors and formatting to enhance readability.

## What if I can manipulate the main application?
In the plugin system of CLI-Toolkit, the `Plugin` class's `__init__` method receives a reference to the main application (the `master` parameter). This allows you to interact with the main application from your plugin, enabling you to perform more complex actions and integrate your plugin more deeply with the application.
```python
from plugin import BasePlugin # Import the BasePlugin class from the plugin module
from util.message import * # Import the message utility functions

class Plugin(BasePlugin):
   """Description of the plugin."""
   def cmd_my_command(self, args: list):
      """Description of my_command."""
      show_info("MyPlugin", "This is my command!")
      show_info("MyPlugin", f"Arguments passed to the command: {args}")
      show_warning("MyPlugin", "This is a warning message.")
      show_error("MyPlugin", "This is an error message.")
      show_success("MyPlugin", "Command executed successfully!")

   def cmd_show_unknown(self, args: list):
      """Show unknown command."""
      self.master.show_unknown_cmd(args) # Call the main application's method to show unknown command message
```
In this example, we added a new command method `cmd_show_unknown` that calls the main application's `show_unknown_cmd` method to display an unknown command message. This demonstrates how you can use the `master` reference to interact with the main application and utilize its functionality in your plugin.

## More actions on the `__init__` method

You can also override the `__init__` method of the `Plugin` class to perform some initialization actions when the plugin is loaded. The `__init__` method will receive a reference to the main application, which can be used to interact with the application.

```python
from plugin import BasePlugin # Import the BasePlugin class from the plugin module
from util.message import * # Import the message utility functions

class Plugin(BasePlugin):
   """Description of the plugin."""
   def __init__(self, master):
      """Initialize the plugin.
      Args:
          master: A reference to the main application, can be used by plugins to interact with the application.
      """
      super().__init__(master) # Call the parent class's __init__ method to initialize the master reference
      show_info("MyPlugin", "Plugin initialized!")

   def cmd_my_command(self, args: list):
      """Description of my_command."""
      show_info("MyPlugin", "This is my command!")
      show_info("MyPlugin", f"Arguments passed to the command: {args}")
      show_warning("MyPlugin", "This is a warning message.")
      show_error("MyPlugin", "This is an error message.")
      show_success("MyPlugin", "Command executed successfully!")

   def cmd_show_unknown(self, args: list):
      """Show unknown command."""
      self.master.show_unknown_cmd(args) # Call the main application's method to show unknown command message
```

In this example, we override the `__init__` method to perform some initialization actions when the plugin is loaded. We call the parent class's `__init__` method to initialize the `master` reference, and then we use the `show_info` function to display a message indicating that the plugin has been initialized.
In actual development, you can use `__init__` to perform more complex initialization actions, such as setting up connections, loading resources, or registering event handlers with the main application.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
