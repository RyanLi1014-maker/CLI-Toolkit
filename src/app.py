"""CLI-Toolkit Application."""

# Import libraries
import logging  # Logging module
import shlex  # Shell-like syntax parsing
import sys  # System
from pathlib import Path  # Path

from rich.console import Console  # Console
from rich.panel import Panel  # Panel
from rich.prompt import Confirm  # Confirm prompt

# Import modules
from src.plugin_manager import PluginManager  # Plugin manager module
from src.util.config import DictConfig  # Configuration module

# Define constants
PYTHON_VERSION = (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro,
)
CLIT_VERSION = (1, 0, 1)
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
"""  # noqa: E501

# Define variables
logger = logging.getLogger("CLI-Toolkit")


class CLIToolkitApp:
    """Command-line interface class."""

    VERSION = CLIT_VERSION  # Application version

    def __init__(self) -> None:
        """Initialize the CLI-Toolkit application."""
        # Initialize the logger
        self.logger = logger.getChild("App")
        self.logger.debug("Logger initialized.")

        # Initialize the console
        self.console = Console()
        self.console.print(  # Print the logo when the application starts
            CLIT_LOGO, highlight=False
        )

        # Initialize the configuration
        self.config = DictConfig(
            config_path=Path(  # Path to the configuration file
                "CLI-Toolkit/config.json"
            ),
            default_config={  # Default configuration values
                "plugin": {
                    "load_on_enable": True,
                    "load_on_start": True,
                },
            },
            auto_load=True,
            validate_structure=True,
        )
        self.logger.debug("Configuration loaded: %s", self.config)

        # Initialize the plugin manager
        self.plugin_manager = PluginManager(self)
        if self.config["plugin"]["load_on_start"]:  # Load all plugins
            self.plugin_manager.load_all_plugins(self.console)
        self.logger.debug("Plugin manager initialized.")

        # Initialize aliases
        self.aliases = DictConfig(config_path=Path("CLI-Toolkit/aliases.json"))
        self.logger.debug("Aliases loaded: %s", self.aliases)

    def _dispatch(self, input_cmd: str) -> None:
        """Dispatch the command to the appropriate handler.

        Args:
            input_cmd (str): The raw input command entered by the user.

        """
        self.logger.info("Dispatching command: '%s'", input_cmd)

        # Parse the command using shell-like syntax
        try:
            parsed_input = shlex.split(
                input_cmd
            )  # Parse the command using shell-like syntax
        except ValueError as e:  # Handle parsing errors
            self.console.print(
                f"[red]Error parsing command: {e}.[/red] "
                "Please check your command syntax and try again."
            )
            return

        # Get the command name
        cmd = parsed_input[0] if parsed_input else ""

        # Get the command arguments
        args = parsed_input[1:] if len(parsed_input) > 1 else []

        # If the method exists and is callable, call it with the arguments
        if callable(method := getattr(self, f"cmd_{cmd}", None)):
            self.logger.info("Calling method: %s", method)
            try:
                method(args)
            except Exception as e:  # Catch any exceptions raised by the command method
                self.logger.exception(
                    "An unexpected error occurred while executing command '%s'", cmd
                )
                self.console.print(
                    f"An unexpected error occurred: {e}",
                    style="red",
                )

        # If the command is an alias, resolve it and call the corresponding method
        elif cmd in self.aliases:
            alias_cmd = self.aliases[cmd]
            self.logger.info("Resolving alias '%s' to command '%s'", cmd, alias_cmd)
            self._dispatch(  # Recursively dispatch the resolved command
                f"{alias_cmd} " + " ".join(args)
            )

        # If the command is not recognized, call the default handler
        else:
            if cmd:  # If the command is not blank, show it as an unknown command
                self.console.print(
                    f"Unknown command: '{cmd}'. Please enter an existing command.",
                    style="red",
                )

    def mainloop(self) -> None:
        """Start the command loop."""
        self.console.rule()
        self.console.print(  # Print the welcome message
            "Welcome to [bold yellow]CLI-Toolkit[/bold yellow]!",
            "Type 'help' for a list of available commands.",
        )
        # Start the command loop
        while True:
            try:
                command = self.console.input("[bold purple]CLI-Toolkit>[/bold purple] ")
                self._dispatch(command)  # Dispatch the command
            except KeyboardInterrupt, EOFError:  # Handle Ctrl+C and Ctrl+D gracefully
                self.console.print()  # Print a newline
                self.logger.warning("Received interrupt signal.")
                self.console.print("Goodbye!")
                sys.exit(0)  # Exit the application with code 0 on Ctrl+C

    def cmd_alias(self, args: list[str]):  # noqa: D417
        """Create a command alias.

        Usage:
            alias: List all command aliases.
            alias <sub_command>: Operate on an existing alias with the specified option.

        Sub-commands:
            create <alias_name>: Create a new alias.
                Can be simplified to 'c <alias_name>'.
            delete <alias_name>: Delete an existing alias.
                Can be simplified to 'd <alias_name>'.

        Arguments:
            alias_name: The name of the alias to create or delete.

        """
        # Handle the 'alias' command with arguments
        if args:
            self.logger.debug("Handling 'alias' command with arguments: %s", args)

            # Get the sub-command and its arguments
            sub_command = args[0]
            sub_args = args[1:]
            self.logger.debug("Sub-command: '%s'", sub_command)
            self.logger.debug("Sub-command arguments: '%s'", sub_args)

            # Match the sub-command
            match sub_command:
                case "create" | "c":
                    if len(sub_args) == 2:  # Check if the required args are provided
                        # Extract the alias name and command from the sub-arguments
                        alias_name, command = sub_args
                        # Check if the command is already an alias
                        if command in self.aliases or alias_name in [
                            cmd.split(" ")[0] for cmd in self.aliases.values()
                        ]:
                            self.logger.warning(
                                "Cannot create alias '%s' for command '%s' "
                                "because it is already an alias.",
                                alias_name,
                                command,
                            )
                            self.console.print(
                                f"Cannot create alias '{alias_name}' for "
                                f"command '{command}' because it is already an alias.",
                                style="red",
                            )
                            return
                        # Add the alias to the configuration
                        self.aliases[alias_name] = command
                        self.aliases.save()  # Save the updated configuration
                        self.logger.info(
                            "Alias '%s' created for command '%s'",
                            alias_name,
                            command,
                        )
                        self.console.print(
                            f"Alias '{alias_name}' created for command '{command}'.",
                            style="green",
                        )
                    else:  # If the required arguments are not provided
                        self.logger.info("Invalid alias creation usage.")
                        self.console.print(
                            "Invalid alias creation usage. "
                            "For more information, type 'help alias'."
                        )
                case "delete" | "d":
                    if len(sub_args) == 1:  # Check if the required arg is provided
                        alias_name = sub_args[0]
                        if alias_name in self.aliases:
                            del self.aliases[alias_name]
                            self.aliases.save()  # Save the updated configuration
                            self.logger.info("Alias '%s' deleted.", alias_name)
                            self.console.print(
                                f"Alias '{alias_name}' deleted.", style="green"
                            )
                        else:
                            self.logger.warning("Alias '%s' not found.", alias_name)
                            self.console.print(
                                f"Alias '{alias_name}' not found.", style="red"
                            )
                    else:  # If the required argument is not provided
                        self.logger.info("Invalid alias deletion usage.")
                        self.console.print(
                            "Invalid alias deletion usage. "
                            "For more information, type 'help alias'."
                        )
                case unknown_command:
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'. "
                        "Please enter an existing sub-command.",
                        style="red",
                    )

        # Handle the 'alias' command without arguments
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

    def cmd_clear(self, _):  # noqa: D417
        """Clear the console screen.

        Usage:
            clear: Clear the console screen.

        """
        self.console.clear()  # Clear the console screen
        self.logger.info("Console cleared.")

    def cmd_config(self, args: list[str]):  # noqa: D417
        """Show or set configuration values.

        Usage:
            config: Show all configuration values.
            config <sub-command>: Set a configuration value.

        Sub-Commands:
            set <category> <key> <value>: Set a configuration value.
                Can be simplified to 's <category> <key> <value>'.
            reset <category> <key>: Reset a configuration value to its default setting.
                Can be simplified to 'rs <category> <key>'.
            reset_all: Reset all configuration values to their default settings.
                Can be simplified to 'rsa'.
            reload: Reload the configuration from the file.
                Can be simplified to 'rl'.

        Arguments:
            category: The category of the configuration to set.
            key: The key of the configuration to set.
            value: The value to set for the configuration.

        """
        if args:  # If arguments are provided, attempt to set a configuration value
            self.logger.debug("Handling 'config' command with arguments.")

            # Get the sub-command and its arguments
            sub_command = args[0]
            sub_args = args[1:]
            self.logger.debug("Sub-command: '%s'", sub_command)
            self.logger.debug("Sub-arguments: '%s'", sub_args)

            # Match the sub-command
            match sub_command:
                case "set" | "s":
                    if len(sub_args) == 3:
                        # Extract the category, key, and value from the arguments
                        category = sub_args[0].lower()
                        key = sub_args[1].lower()
                        value = sub_args[2]
                        # Convert the value to a boolean if necessary
                        match value.lower():
                            case "true":
                                value = True
                            case "false":
                                value = False
                        # Check if the category exists
                        if category not in self.config:
                            self.logger.warning(
                                "Failed to set configuration value. "
                                "Category '%s' does not exist.",
                                category,
                            )
                            self.console.print(
                                "Failed to set configuration value. "
                                f"Category '{category}' does not exist.",
                                style="red",
                            )
                            return
                        # Check if the key exists
                        if key not in self.config[category]:
                            self.logger.warning(
                                "Failed to set configuration value. "
                                "Key '%s' does not exist in category '%s'.",
                                key,
                                category,
                            )
                            self.console.print(
                                "Failed to set configuration value. "
                                f"Key '{key}' does not exist in category '{category}'.",
                                style="red",
                            )
                            return
                        # Check if the value is of the correct type
                        if type(value) is not type(self.config[category][key]):
                            self.logger.warning(
                                "Failed to set configuration value. "
                                "Value '%s' is not of the correct type "
                                "for key '%s' in category '%s'.",
                                value,
                                key,
                                category,
                            )
                            self.console.print(
                                "Failed to set configuration value. "
                                f"Value '{value}' is not of the correct type "
                                f"for key '{key}' in category '{category}'.",
                                style="red",
                            )
                            return
                        # Set the configuration value
                        self.config[category][key] = value
                        self.config.save()
                        self.logger.info(
                            "Configuration value set: %s.%s = %s",
                            category,
                            key,
                            value,
                        )
                        self.console.print(
                            "[green]Configuration value set:[/green] "
                            f"[blue]{category}.{key}[/blue]: {value}"
                        )
                    else:  # If the required arguments are not provided
                        self.logger.info("Invalid config usage.")
                        self.console.print(
                            "Invalid config usage. "
                            "For more information, type 'help config'."
                        )
                case "reset" | "rs":
                    if len(sub_args) == 2:
                        category = sub_args[0].lower()
                        key = sub_args[1].lower()
                        default_value = self.config.default.get(category, {}).get(key)
                        if category in self.config and key in self.config[category]:
                            if default_value is not None:
                                if Confirm().ask(  # Ask for confirmation
                                    "Are you sure you want to "
                                    f"reset config {category}.{key} "
                                    "to default value?",
                                    default=False,
                                ):
                                    self.config[category][key] = default_value
                                    self.config.save()
                                    self.logger.info(
                                        "Configuration value reset: %s.%s = %s",
                                        category,
                                        key,
                                        default_value,
                                    )
                                    self.console.print(
                                        f"[green]Configuration value reset:[/green] "
                                        f"[blue]{category}.{key}[/blue]: "
                                        + str(default_value)
                                    )
                                else:  # If the user does not confirm
                                    self.logger.info("Operation aborted by user.")
                                    self.console.print(
                                        "Operation aborted.", style="yellow"
                                    )
                            else:  # If there is no default value
                                self.logger.info(
                                    "No default value found for "
                                    "category '%s' and key '%s'.",
                                    category,
                                    key,
                                )
                                self.console.print(
                                    f"No default value found for "
                                    f"category '{category}' and key '{key}'.",
                                    style="red",
                                )
                        else:  # If the category or key does not exist
                            self.logger.info(
                                "Category '%s' or key '%s' not found.",
                                category,
                                key,
                            )
                            self.console.print(
                                f"Category '{category}' or key '{key}' not found.",
                                style="red",
                            )
                    else:  # If the required arguments are not provided
                        self.logger.info("Invalid config reset usage.")
                        self.console.print(
                            "Invalid config reset usage. "
                            "For more information, type 'help config'.",
                            style="red",
                        )
                case "reset_all" | "rsa":
                    if len(sub_args) == 0:
                        if Confirm().ask(  # Ask for confirmation
                            "Are you sure you want to reset all "
                            "configuration values to their default values?",
                            default=False,
                        ):
                            # Reset to default configuration
                            self.config.clear()  # Clear the current config
                            self.config.update(self.config.default)  # Reset to default
                            self.config.save()  # Save the updated configuration
                            # Log the reset action and show a confirmation message
                            self.logger.info(
                                "All configuration values reset to defaults."
                            )
                            self.console.print(
                                "All configuration values reset to defaults.",
                                style="green",
                            )
                        else:  # If the user does not confirm
                            self.logger.info("Operation aborted by user.")
                            self.console.print("Operation aborted.", style="yellow")
                    else:  # If arguments are provided, show an error message
                        self.logger.info("Invalid config reset_all usage.")
                        self.console.print(
                            "Invalid config reset_all usage. "
                            "For more information, type 'help config'.",
                            style="red",
                        )
                case "reload" | "rl":
                    if len(sub_args) == 0:
                        self.config.load()  # Reload the configuration from the file
                        self.logger.info("Configuration reloaded from file.")
                        self.console.print(
                            "[green]Configuration reloaded from file.[/green]"
                        )
                    else:  # If arguments are provided, show an error message
                        self.logger.info("Invalid config reload usage.")
                        self.console.print(
                            "Invalid config reload usage. "
                            "For more information, type 'help config'.",
                            style="red",
                        )
                case unknown_command:
                    self.logger.warning("Unknown sub-command: '%s'", unknown_command)
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'", style="red"
                    )
                    return

        else:  # If no arguments are provided, show all configuration values
            for category, settings in self.config.items():
                # Create a list of configuration values for the category
                config_list = [
                    f"[blue]{key}[/blue]: {value}" for key, value in settings.items()
                ]
                # Print the configuration values for the category in a panel
                self.console.print(
                    Panel(
                        "\n".join(config_list),
                        title=f"{category.capitalize()} Configuration",
                        highlight=True,
                    )
                )

    def cmd_exit(self, _):  # noqa: D417
        """Exit the application.

        Equivalent to Ctrl+C, this command exits the application with code 0.

        Usage:
            exit: Exit the application with code 0.

        """
        self.logger.info("Exit command received. Exiting...")
        self.console.print("Goodbye!")
        sys.exit(0)  # Exit the application with code 0 on exit command

    def cmd_help(self, args: list[str]):  # noqa: D417
        """Show help information for commands.

        Usage:
            help: Show command list.
            help <command>: Show detailed descriptions for <command>.

        Arguments:
            command: The specific command to show detailed help for.

        """
        if args:
            # Get the command name
            cmd_name = args[0]  # Get the command name from the arguments
            self.logger.debug("Showing help for command '%s'", cmd_name)

            # If the method exists and is callable, show its docstring as detailed help
            if callable(method_attr := getattr(self, f"cmd_{cmd_name}", None)):
                if method_doc := method_attr.__doc__:
                    self.console.print(
                        Panel(
                            method_doc.strip(),
                            title=f"Detailed Help for '{cmd_name}' command",
                            highlight=True,
                        ),
                        markup=False,
                    )
                else:  # If the method has no docstring, provide a default message
                    self.console.print(
                        f"Command '{cmd_name}' has no description available."
                    )
            elif cmd_name in self.aliases:  # If the command is an alias
                self.logger.debug("Showing help for alias '%s'", cmd_name)
                self.console.print(
                    f"Command '{cmd_name}' is an alias for '{self.aliases[cmd_name]}'."
                )
                self.console.print("Redirecting to the original command.")
                self.cmd_help([self.aliases[cmd_name].split(" ")[0]])
            else:  # If the method doesn't exist or isn't callable
                self.console.print(
                    f"Command '{cmd_name}' not found. "
                    "Please enter an existing command.",
                    style="red",
                )

        else:  # If no specific command is provided, show a list of available commands
            self.logger.debug("Showing help for all commands.")

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
                            "Method '%s' has docstring. Adding to list.", method_name
                        )
                        command_list.append(
                            f"[blue]{method_name[4:]}[/blue]: "
                            + method_doc.splitlines()[0]
                        )
                    else:  # If the method has no docstring, provide a default message
                        self.logger.debug(
                            "Method '%s' has no docstring. "
                            "Adding default message to list.",
                            method_name,
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

    def cmd_plugin(self, args: list[str]):  # noqa: D417
        """Plugin management commands.

        Usage:
            plugin: List all plugins.
            plugin <sub-command>: Manage plugins.

        Sub-Commands:
            load <plugin_name>: Load a plugin.
                Can be simplified to 'l <plugin_name>'.
            unload <plugin_name>: Unload a plugin.
                Can be simplified to 'u <plugin_name>'.
            reload <plugin_name>: Reload a plugin.
                Can be simplified to 'r <plugin_name>'.
            disable <plugin_name>: Disable a plugin.
                Can be simplified to 'dis <plugin_name>'.
            enable <plugin_name>: Enable a plugin.
                Can be simplified to 'en <plugin_name>'.
            help <plugin_name>: Show help for plugin commands.
                Can be simplified to 'h <plugin_name>'.
            load_all: Load all plugins. Can be simplified to 'la'.
            unload_all: Unload all plugins. Can be simplified to 'ua'.
            reload_all: Reload all plugins. Can be simplified to 'ra'.

        Arguments:
            plugin_name: The name of the plugin to manage.
            key: The key of the plugin configuration to set.
            value: The value to set for the plugin configuration.

        """
        if args:  # If arguments are provided, handle them
            self.logger.debug("Handling 'plugin' command with arguments.")

            # Get the sub-command and its arguments
            sub_command = args[0]
            sub_args = args[1:]
            self.logger.debug("Sub-command: '%s'", sub_command)
            self.logger.debug("Sub-command arguments: '%s'", sub_args)

            # Match the sub-command
            match sub_command:
                case "load" | "l":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        try:
                            load_state = self.plugin_manager.load_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                "Failed to load plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to load plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Loaded plugin: {sub_args[0]}",
                                style="green",
                            ) if load_state else self.console.print(
                                f"Plugin '{sub_args[0]}' is already loaded.",
                                style="yellow",
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin load usage.")
                        self.console.print(
                            "Invalid plugin load usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "unload" | "u":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        try:
                            self.plugin_manager.unload_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                "Failed to unload plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to unload plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Unloaded plugin: {sub_args[0]}", style="green"
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin unload usage.")
                        self.console.print(
                            "Invalid plugin unload usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "reload" | "r":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        try:
                            self.plugin_manager.reload_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                "Failed to reload plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to reload plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Reloaded plugin: {sub_args[0]}", style="green"
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin reload usage.")
                        self.console.print(
                            "Invalid plugin reload usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "disable" | "dis":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        try:
                            self.plugin_manager.disable_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                "Failed to disable plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to disable plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Disabled plugin: {sub_args[0]}", style="green"
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin disable usage.")
                        self.console.print(
                            "Invalid plugin disable usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "enable" | "en":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        try:
                            self.plugin_manager.enable_plugin(sub_args[0])
                        except Exception as e:  # Catch any exceptions
                            self.logger.error(
                                "Failed to enable plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to enable plugin '{sub_args[0]}': {e}",
                                style="red",
                            )
                        else:
                            self.console.print(
                                f"Enabled plugin: {sub_args[0]}", style="green"
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin enable usage.")
                        self.console.print(
                            "Invalid plugin enable usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "help" | "h":
                    if len(sub_args) == 1:  # Check if the arguments are valid
                        plugin_name = sub_args[0]
                        self.logger.debug("Showing help for plugin '%s'", plugin_name)
                        if plugin_instance := self.plugin_manager.plugin_instances.get(
                            plugin_name
                        ):
                            if plugin_doc := plugin_instance.__doc__:
                                self.console.print(
                                    Panel(
                                        plugin_doc.strip(),
                                        title=f"Help for '{plugin_name}' plugin",
                                        highlight=True,
                                    ),
                                    markup=False,
                                )
                            else:  # If the plugin has no docstring, show a message
                                self.console.print(
                                    f"Plugin '{plugin_name}' has "
                                    "no description available."
                                )
                        else:  # If the plugin is not found, show an error message
                            self.console.print(
                                f"Plugin '{plugin_name}' not found. "
                                "Please enter an existing plugin name.",
                                style="red",
                            )
                    else:  # If the arguments are not valid, show an error message
                        self.logger.info("Invalid plugin help usage.")
                        self.console.print(
                            "Invalid plugin help usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "load_all" | "la":
                    if not sub_args:  # If no arguments are provided, load all plugins
                        loaded_count = self.plugin_manager.load_all_plugins(
                            self.console
                        )
                        self.console.print(
                            f"Loaded {loaded_count} plugins.", style="green"
                        )
                    else:  # If arguments are provided, show an error message
                        self.logger.info("Invalid plugin load_all usage.")
                        self.console.print(
                            "Invalid plugin load_all usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "unload_all" | "ua":
                    if not sub_args:  # If no arguments are provided, unload all plugins
                        unloaded_count = self.plugin_manager.unload_all_plugins()
                        self.console.print(
                            f"Unloaded {unloaded_count} plugins.", style="green"
                        )
                    else:  # If arguments are provided, show an error message
                        self.logger.info("Invalid plugin unload_all usage.")
                        self.console.print(
                            "Invalid plugin unload_all usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case "reload_all" | "ra":
                    if not sub_args:  # If no arguments are provided, reload all plugins
                        reloaded_count = self.plugin_manager.reload_all_plugins()
                        self.console.print(
                            f"Reloaded {reloaded_count} plugins.", style="green"
                        )
                    else:  # If arguments are provided, show an error message
                        self.logger.info("Invalid plugin reload_all usage.")
                        self.console.print(
                            "Invalid plugin reload_all usage. "
                            "For more information, type 'help plugin'.",
                            style="red",
                        )
                case unknown_command:
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'. "
                        "Please enter an existing sub-command.",
                        style="red",
                    )

        else:  # If no arguments are provided, list all plugins
            self.logger.debug("Listing all plugins.")

            # Iterate over all loaded plugins
            loaded_plugin = []  # List to hold loaded plugin names and descriptions
            for (
                plugin_name,
                plugin_instance,
            ) in self.plugin_manager.plugin_instances.items():
                if plugin_doc := plugin_instance.__doc__:
                    self.logger.debug(
                        "Plugin '%s' has docstring. Adding to list.", plugin_name
                    )
                    loaded_plugin.append(
                        f"[blue]{plugin_name}[/blue]: {plugin_doc.splitlines()[0]}"
                    )
                else:  # If the plugin has no docstring, show a default message
                    self.logger.debug(
                        "Plugin '%s' has no docstring. Adding default message to list.",
                        plugin_name,
                    )
                    loaded_plugin.append(
                        f"[blue]{plugin_name}[/blue]: No description available."
                    )

            # Check for unloaded plugins in the plugin directory
            unloaded_plugin = []  # List to hold unloaded plugin names and descriptions
            for file in self.plugin_manager.plugin_dir.iterdir():
                if file.is_file() and file.suffix == ".py":  # Skip non-Python files
                    # Get the plugin name from the file name
                    plugin_name = file.stem
                    if plugin_name not in self.plugin_manager.plugin_instances:
                        unloaded_plugin.append(f"[blue]{plugin_name}[/blue]: Unloaded")

            disabled_plugin = []  # List to hold disabled plugin names and descriptions
            for plugin_name in self.plugin_manager.disabled_plugins:
                disabled_plugin.append(f"[blue]{plugin_name}[/blue]: Disabled")

            # Print plugin list message
            (  # Print the list of loaded plugins in a panel
                self.console.print(
                    Panel(
                        "\n".join(loaded_plugin), title="Loaded Plugins", highlight=True
                    )
                )
                if loaded_plugin
                else self.console.print("No plugins loaded.")
            )
            (  # Print the list of unloaded plugins in a panel
                self.console.print(
                    Panel(
                        "\n".join(unloaded_plugin),
                        title="Unloaded Plugins",
                        highlight=True,
                    )
                )
                if unloaded_plugin
                else self.console.print(
                    "No unloaded plugins found in the plugin directory."
                )
            )
            (  # Print the list of disabled plugins in a panel
                self.console.print(
                    Panel(
                        "\n".join(disabled_plugin),
                        title="Disabled Plugins",
                        highlight=True,
                    )
                )
                if disabled_plugin
                else self.console.print("No disabled plugins.")
            )

    def cmd_version(self, _):  # noqa: D417
        """Display the version of CLI-Toolkit application and plugins.

        Usage:
            version: Display the version of the CLI-Toolkit application.
        """
        # Display Python version and CLI-Toolkit version
        app_version = [
            "[blue]Python[/blue] v" + ".".join([str(part) for part in PYTHON_VERSION]),
            "[blue]CLI-Toolkit[/blue] v"
            + ".".join([str(part) for part in self.VERSION]),
        ]
        self.console.print(Panel("\n".join(app_version), title="Application Versions"))

        # Display plugin versions
        plugin_versions_list = [
            f"[blue]{plugin_name}[/blue] v"
            + ".".join([str(part) for part in plugin.VERSION])
            for plugin_name, plugin in self.plugin_manager.plugin_instances.items()
        ]
        (
            self.console.print(
                Panel("\n".join(plugin_versions_list), title="Plugin Versions")
            )
            if plugin_versions_list
            else self.console.print("No plugins loaded.")
        )
