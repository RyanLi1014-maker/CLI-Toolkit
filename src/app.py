"""CLI-Tookit Application"""

# Import libraries
from sys import version_info  # Python version
from pathlib import Path  # File path handling
import shlex  # Shell-like syntax parsing
import logging  # Logging module
from rich.console import Console  # Console
from rich.panel import Panel  # Panel

# Import modules
from src.plugin import PluginManager  # Plugin manager module
from src.util.config import Config  # Configuration utilities module

# Define constants
PYTHON_VERSION = (version_info.major, version_info.minor, version_info.micro)
CLIT_VERSION = (0, 1, 0)  # CLI-Toolkit version
CLIT_LOGO = r"""
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
"""
del version_info  # Delete the Python version variable after use


class CLI_Toolkit_App:
    """Command-line interface class."""

    VERSION = CLIT_VERSION  # Application version

    def __init__(self):
        """Initialize the CLI-Tookit application."""
        # Initialize the console
        self.console = Console()
        self.console.print(
            CLIT_LOGO, highlight=False
        )  # Print the logo when the application starts

        # Initialize the logger
        logging_directory = Path("log")
        if not logging_directory.exists():  # Check if the directory exists
            logging_directory.mkdir()
        logging.basicConfig(  # Initialize the logger
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] (%(filename)s:%(lineno)d) - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
            filename=logging_directory / "CLI-Toolkit.log",
            filemode="w",
            encoding="utf-8",
        )
        self.logger = logging.getLogger("CLI-Toolkit")  # Set the logger
        self.logger.debug(f"Logger initialized.")

        # Initialize the configuration
        self.config = Config(
            config_path=Path(  # Path to the configuration file
                "CLI-Toolkit/config.json"
            ),
            default_config={  # Default configuration values
                "plg": {
                    "load_on_start": True,  # Whether to automatically load all plugins in the plugin directory when the application starts
                },
            },
        )
        self.config.load()  # Load the configuration from the file
        self.logger.debug(f"Configuration loaded: {self.config}")

        # Initialize the plugin manager
        self.plugin_manager = PluginManager(self)  # Initialize the plugin manager
        if self.config["plg"]["load_on_start"]:  # Load all plugins
            self.plugin_manager.load_all_plugins()
        self.logger.debug(f"Plugin manager initialized.")

        # Initialize aliases
        self.aliases = Config(
            config_path=Path(
                "CLI-Toolkit/aliases.json"
            ),  # Path to the aliases configuration file
            default_config={  # Default aliases from the main configuration
                "?": "help",  # Alias "?" for "help" command
                "quit": "exit",  # Alias "quit" for "exit" command
            },
        )
        self.aliases.load()  # Load the aliases from the file

    def _dispatch(self, input_cmd: str):
        """Dispatch the command to the appropriate handler.
        Args:
            input_cmd (str): The raw input command entered by the user.
        """
        self.logger.info(f"Dispatching command: '{input_cmd}'")

        # Parse the command using shell-like syntax
        try:
            parsed_input = shlex.split(
                input_cmd
            )  # Parse the command using shell-like syntax
        except ValueError as e:  # Handle parsing errors
            self.console.print(
                f"[red]Error parsing command: {e}.[/red] Please check your command syntax and try again."
            )
            return

        # Get the command name
        cmd = parsed_input[0] if parsed_input else ""

        # Get the command arguments
        args = parsed_input[1:] if len(parsed_input) > 1 else []

        # If the method exists and is callable, call it with the arguments
        if callable(method := getattr(self, f"cmd_{cmd}", None)):
            self.logger.info(f"Calling method: {method}")
            try:
                method(args)
            except Exception as e:  # Catch any exceptions raised by the command method
                self.logger.error(
                    f"An unexpected error occurred while executing command '{cmd}'",
                    exc_info=True,
                )
                self.console.print(
                    f"An unexpected error occurred: {e}",
                    style="red",
                )

        elif (
            cmd in self.aliases
        ):  # If the command is an alias, resolve it and call the corresponding method
            alias_cmd = self.aliases[cmd]
            if alias_cmd in self.aliases.keys():
                self.logger.warning(
                    f"Alias '{cmd}' resolves to '{alias_cmd}', which is also an alias. This may cause unexpected behavior. Cancelling command dispatch..."
                )
                return
            self.logger.info(f"Resolving alias '{cmd}' to command '{alias_cmd}'")
            self._dispatch(alias_cmd)  # Recursively dispatch the resolved command

        else:  # If the command is not recognized, call the default handler
            self.show_unknown_cmd(cmd)

    def show_unknown_cmd(self, input_cmd: str = ""):
        """Show an error message for unknown/blank commands.
        Args:
            input_cmd (str): The input command that was not recognized.
        """
        if input_cmd:
            self.console.print(
                f"Unknown command: '{input_cmd}'. Please enter an existing command.",
                style="red",
            )
        else:  # If the input command is blank, ignore it
            self.console.print(
                "No command entered. Please enter an existing command.",
                style="red",
            )
            return

    def mainloop(self):
        """Start the command loop."""
        self.console.rule()
        self.console.print(  # Print the welcome message
            f"Welcome to [bold yellow]CLI-Toolkit[/bold yellow]!",
            "Type 'help' for a list of available commands.",
        )
        # Infinite loop to continuously prompt for user input and dispatch commands
        while True:
            try:
                command = self.console.input("[purple]CLI-Toolkit> [/purple]")
                self._dispatch(command)  # Dispatch the command
            except (KeyboardInterrupt, EOFError):  # Handle Ctrl+C and Ctrl+D gracefully
                self.console.print()  # Print a newline for better formatting after Ctrl+C or Ctrl+D
                self.logger.warning("Received interrupt signal.")
                self.console.print("Goodbye!")
                exit(0)  # Exit the application with code 0 on Ctrl+C

    def cmd_alias(self, args: list):
        """Create a command alias.

        Usage:
            alias: List all command aliases.
            alias <sub_command> [args]: Operate on an existing alias with the specified option.

        Options:
            sub_command: The sub-command to execute. Can be one of the following:
                create (or 'c'): Create a new alias. Requires two additional arguments: the alias name and the command it maps to.
                delete (or 'd'): Delete an existing alias. Requires one additional argument: the alias name to delete.
            args: The arguments for the sub-command, as described above.
        """
        # Handle the case where the user provides arguments, which means they want to create or delete an alias
        if args:
            self.logger.debug(f"Handling 'alias' command with arguments: {args}")

            # Get the sub-command and its arguments
            sub_command = args[0]
            sub_args = args[1:]
            self.logger.debug(f"Sub-command: '{sub_command}'")
            self.logger.debug(f"Sub-command arguments: '{sub_args}'")

            # Match the sub-command
            match sub_command:
                case "create" | "c":
                    if len(sub_args) == 2:  # Check if the required args are provided
                        # Extract the alias name and command from the sub-arguments
                        alias_name, command = sub_args
                        # Check if the command is already an alias
                        if command in self.aliases.keys():
                            self.logger.warning(
                                f"Cannot create alias '{alias_name}' for command '{command}' because it is already an alias."
                            )
                            self.console.print(
                                f"Cannot create alias '{alias_name}' for command '{command}' because it is already an alias.",
                                style="red",
                            )
                            return
                        # Add the alias to the configuration
                        self.aliases[alias_name] = command
                        self.aliases.save()  # Save the updated configuration to the file
                        self.logger.info(
                            f"Alias '{alias_name}' created for command '{command}'"
                        )
                        self.console.print(
                            f"Alias '{alias_name}' created for command '{command}'.",
                            style="green",
                        )
                    else:  # If the required arguments are not provided, show an error message
                        self.logger.info(
                            f"Invalid alias creation usage."
                        )
                        self.console.print(
                            "Invalid alias creation usage. For more information, type 'help alias'."
                        )
                case "delete" | "d":
                    if len(sub_args) == 1:  # Check if the required arg is provided
                        alias_name = sub_args[0]
                        if alias_name in self.aliases:
                            del self.aliases[alias_name]
                            self.aliases.save()  # Save the updated configuration to the file
                            self.logger.info(f"Alias '{alias_name}' deleted.")
                            self.console.print(
                                f"Alias '{alias_name}' deleted.", style="green"
                            )
                        else:
                            self.logger.warning(f"Alias '{alias_name}' not found.")
                            self.console.print(
                                f"Alias '{alias_name}' not found.", style="red"
                            )
                    else:  # If the required argument is not provided, show an error message
                        self.logger.info(
                            f"Invalid alias deletion usage."
                        )
                        self.console.print(
                            "Invalid alias deletion usage. For more information, type 'help alias'."
                        )
        # Handle the case where the user provides no arguments, which means they want to list all aliases
        else:
            self.logger.debug("Listing all command aliases.")

            if self.aliases:  # Check if there are any aliases defined
                alias_list = [  # Iterate over all aliases
                    f"[blue]{alias}[/blue]: {cmd}"
                    for alias, cmd in self.aliases.items()
                ]
                self.console.print(  # Print the list of aliases in a panel
                    Panel(
                        "\n".join(alias_list), title="Command Aliases", highlight=True
                    )
                )
            else:  # If there are no aliases defined, show a message
                self.console.print("No command aliases defined.")
                return

    def cmd_clear(self, _):
        """Clear the console screen.

        Usage:
            clear: Clear the console screen.
        """
        self.console.clear()  # Clear the console screen
        self.logger.info("Console cleared.")

    def cmd_exit(self, _):
        """Exit the application.
        Equivalent to Ctrl+C, this command exits the application with code 0.

        Usage:
            exit: Exit the application with code 0.
        """
        self.logger.info("Exit command received. Exiting...")
        self.console.print("Goodbye!")
        exit(0)  # Exit the application with code 0 on exit command

    def cmd_help(self, args: list):
        """Show help information for commands.

        Usage:
            help: Show command list.
            help <command>: Show detailed descriptions for <command>.

        Options:
            command: The specific command to show detailed help for.
        """
        if args:

            # Get the command name
            cmd_name = args[0]  # Get the command name from the arguments
            self.logger.debug(f"Showing help for command '{cmd_name}'")

            # If the method exists and is callable, show its docstring as detailed help
            if callable(method_attr := getattr(self, f"cmd_{cmd_name}", None)):
                if method_doc := method_attr.__doc__:
                    self.console.print(
                        Panel(
                            method_doc.strip(),
                            title=f"Detailed Help for '{cmd_name}' command",
                            highlight=True,
                        )
                    )
                else:  # If the method has no docstring, provide a default message
                    self.console.print(
                        f"Command '{cmd_name}' has no description available."
                    )
            else:  # If the method doesn't exist or isn't callable, show an error message
                self.show_unknown_cmd(cmd_name)

        else:  # If no specific command is provided, show a list of available commands
            self.logger.debug(f"Showing help for all commands.")

            # Iterate over all methods in the class
            command_list = []  # List to store command names
            for method_name in dir(self):
                # Ignore methods that don't start with "cmd_"
                if not method_name.startswith("cmd_"):
                    continue
                # If the method exists and is callable, add it to the command list
                if callable(method_attr := getattr(self, method_name, None)):
                    if method_doc := method_attr.__doc__:
                        self.logger.debug(
                            f"Method '{method_name}' has docstring. Adding to list."
                        )
                        command_list.append(
                            f"[blue]{method_name[4:]}[/blue]: {method_doc.splitlines()[0]}"
                        )
                    else:  # If the method has no docstring, provide a default message
                        self.logger.debug(
                            f"Method '{method_name}' has no docstring. Adding default message to list."
                        )
                        command_list.append(
                            f"[blue]{method_name[4:]}[/blue]: No description available."
                        )

            # Print command list message
            self.console.print(
                Panel(
                    "\n".join(command_list), title="Available Commands", highlight=True
                )
            )
            self.console.print(
                "To get detailed help for a specific command, type 'help <command>'."
            )

    def cmd_plg(self, args: list):
        """Plugin management commands.

        Usage:
            plg: List all plugins.
            plg <command> <plugin_name>: Manage plugins.

        Options:
            command: The command to execute. Can be one of the following:
                load: Load a plugin.
                unload: Unload a plugin.
                reload: Reload a plugin.
                load_all: Load all plugins in the plugin directory.
                unload_all: Unload all plugins that had already been loaded.
                reload_all: Reload all plugins that had already been loaded.
            plugin_name: The name of the plugin to load, unload, or reload.
        """
        if args:  # If arguments are provided, handle them
            self.logger.debug("Handling 'plg' command with arguments.")

            # Get the sub-command and its arguments
            sub_command = args[0]
            sub_args = args[1:]
            self.logger.debug(f"Sub-command: '{sub_command}'")
            self.logger.debug(f"Sub-command arguments: '{sub_args}'")

            # Match the sub-command
            match sub_command:
                case "load":
                    if sub_args:  # If an argument is provided, load the plugin
                        try:
                            self.plugin_manager.load_plugin(sub_args[0])
                        except Warning as w:  # Catch any warnings
                            self.logger.warning(
                                f"Failed to load plugin '{sub_args[0]}': {w}"
                            )
                            self.console.print(
                                f"Failed to load plugin '{sub_args[0]}': {w}",
                                style="yellow",
                            )
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                f"Failed to load plugin '{sub_args[0]}': {e}"
                            )
                            self.console.print(
                                f"Failed to load plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Loaded plugin: {sub_args[0]}", style="green"
                            )
                    else:  # Otherwise, show a message for blank command
                        self.logger.info(
                            "No plugin name provided for 'plg load' command."
                        )
                        self.show_unknown_cmd()
                case "unload":
                    if sub_args:  # If an argument is provided, unload the plugin
                        try:
                            self.plugin_manager.unload_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                f"Failed to unload plugin '{sub_args[0]}': {e}"
                            )
                            self.console.print(
                                f"Failed to unload plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Unloaded plugin: {sub_args[0]}", style="green"
                            )
                    else:  # Otherwise, show a message for blank command
                        self.logger.info(
                            "No plugin name provided for 'plg unload' command."
                        )
                        self.show_unknown_cmd()
                case "reload":
                    if sub_args:  # If an argument is provided, reload the plugin
                        try:
                            self.plugin_manager.reload_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                f"Failed to reload plugin '{sub_args[0]}': {e}"
                            )
                            self.console.print(
                                f"Failed to reload plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Reloaded plugin: {sub_args[0]}", style="green"
                            )
                    else:  # Otherwise, show a message for blank command
                        self.logger.info(
                            "No plugin name provided for 'plg reload' command."
                        )
                        self.show_unknown_cmd()
                case "load_all":
                    loaded_count = self.plugin_manager.load_all_plugins()
                    self.console.print(f"Loaded {loaded_count} plugins.", style="green")
                case "unload_all":
                    unloaded_count = self.plugin_manager.unload_all_plugins()
                    self.console.print(
                        f"Unloaded {unloaded_count} plugins.", style="green"
                    )
                case "reload_all":
                    reloaded_count = self.plugin_manager.reload_all_plugins()
                    self.console.print(
                        f"Reloaded {reloaded_count} plugins.", style="green"
                    )
                case unknown_command:
                    # If an unknown sub-command is provided, show it as an unknown command
                    self.show_unknown_cmd(unknown_command)

        else:  # If no arguments are provided, list all plugins
            self.logger.debug("Listing all plugins.")

            # Check if there are any plugins loaded
            if not self.plugin_manager.plugins:
                self.console.print("No plugins loaded.")
                return

            # Iterate over all plugins
            plugin_list = []  # List to hold plugin names and descriptions
            for plugin_name, plugin_instance in self.plugin_manager.plugins.items():
                if plugin_doc := plugin_instance.__doc__:
                    self.logger.debug(
                        f"Plugin '{plugin_name}' has docstring. Adding to list."
                    )
                    plugin_list.append(
                        f"[blue]{plugin_name}[/blue]: {plugin_doc.splitlines()[0]}"
                    )
                else:  # If the plugin has no docstring, show a default message
                    self.logger.debug(
                        f"Plugin '{plugin_name}' has no docstring. Adding default message to list."
                    )
                    plugin_list.append(
                        f"[blue]{plugin_name}[/blue]: No description available."
                    )

            # Print plugin list message
            self.console.print(
                Panel("\n".join(plugin_list), title="Loaded Plugins", highlight=True)
            )

    def cmd_version(self, _):
        """Display the version of CLI-Toolkit application and plugins.

        Usage:
            version: Display the version of the CLI-Toolkit application.
        """

        # Display Python version and CLI-Toolkit version
        app_version = [
            f"[blue]Python[/blue] v{".".join([str(part) for part in PYTHON_VERSION])}",
            f"[blue]CLI-Toolkit[/blue] v{".".join([str(part) for part in self.VERSION])}",
        ]
        self.console.print(Panel("\n".join(app_version), title="Application Versions"))

        # Display plugin versions
        plugin_versions_list = [
            f"[blue]{plugin_name}[/blue] v{".".join([str(part) for part in plugin.VERSION])}"
            for plugin_name, plugin in self.plugin_manager.plugins.items()
        ]
        self.console.print(
            Panel("\n".join(plugin_versions_list), title="Plugin Versions")
        )
