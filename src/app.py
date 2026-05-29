"""CLI-Toolkit Application."""

# Import libraries
import logging
import re
import shlex
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm

# Import modules
from src.plugin_manager import PluginManager
from src.util.config import DictConfig

# Define constants
PYTHON_VERSION = (
    sys.version_info.major,
    sys.version_info.minor,
    sys.version_info.micro,
)
CLIT_VERSION = (1, 1, 0)
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
logger = logging.getLogger("clit")


class CLIToolkitApp:
    """Command-line interface class."""

    VERSION = CLIT_VERSION

    def __init__(self) -> None:
        """Initialize the CLI-Toolkit application."""
        self.logger = logger.getChild("App")
        self.logger.debug("Logger initialized.")

        self.console = Console()
        self.console.print(CLIT_LOGO, highlight=False)

        self.config = DictConfig(
            config_path=Path("CLI-Toolkit/config.json"),
            default_config={
                "plugin": {
                    "load_on_enable": True,
                    "load_on_start": True,
                },
            },
            auto_load=True,
            validate_structure=True,
        )
        self.logger.debug("Configuration loaded: %s", self.config)

        self.plugin_manager = PluginManager(self)
        if self.config["plugin"]["load_on_start"]:
            self.plugin_manager.load_all_plugins(self.console)
        self.logger.debug("Plugin manager initialized.")

        self.aliases = DictConfig(config_path=Path("CLI-Toolkit/aliases.json"))
        self.logger.debug("Aliases loaded: %s", self.aliases)

        # Track the last Ctrl+C key press timestamp for double-press exit
        self._last_ctrl_c_time = 0.0

    def _dispatch(self, input_cmd: str) -> None:
        """Dispatch the command to the appropriate handler.

        Args:
            input_cmd (str): The raw input command entered by the user.

        """
        self.logger.info("Dispatching command: '%s'", input_cmd)

        try:
            parsed_input = shlex.split(input_cmd)
        except ValueError as e:
            self.console.print(
                f"[bold red]Error parsing command: {e}.[/bold red] "
                "Please check your command syntax and try again."
            )
            return

        cmd = parsed_input[0] if parsed_input else ""
        args = parsed_input[1:] if len(parsed_input) > 1 else []

        # Replace ${...} with the corresponding variable
        temp_args = args.copy()
        args.clear()
        for arg in temp_args:
            if matched := re.match(r"^\${(.+)}$", arg):
                match matched.group(1):
                    case "cwd":
                        args.append(str(Path.cwd().resolve()))
                    case unmatched:
                        args.append(unmatched)
            else:
                args.append(arg)

        # If the method exists and is callable, call it with the arguments
        if callable(method := getattr(self, f"cmd_{cmd}", None)):
            self.logger.info("Calling method: %s", method)
            try:
                method(args)
            except KeyboardInterrupt:
                self.console.print()
                self.logger.warning("Command '%s' interrupted by user.", cmd)
                self.console.print(
                    "[bold yellow]Command interrupted. "
                    "Returning to prompt.[/bold yellow]"
                )
            except Exception as e:
                self.logger.exception(
                    "An unexpected error occurred while executing command '%s'", cmd
                )
                self.console.print(
                    f"An unexpected error occurred: {e}",
                    style="bold red",
                )

        # If the command is an alias, resolve it and call the corresponding method
        elif cmd in self.aliases:
            alias_cmd = self.aliases[cmd]
            self.logger.info("Resolving alias '%s' to command '%s'", cmd, alias_cmd)
            self._dispatch(f"{alias_cmd} " + " ".join(args))

        # If the command is not recognized, call the default handler
        else:
            if cmd:
                self.console.print(
                    f"Unknown command: '{cmd}'. Please enter an existing command.",
                    style="bold red",
                )

    def mainloop(self) -> None:
        """Start the command loop."""
        self.console.rule()
        self.console.print(
            "Welcome to [bold yellow]CLI-Toolkit[/bold yellow]!",
            "Type 'help' for a list of available commands.",
        )
        while True:
            try:
                command = self.console.input("[bold purple]CLI-Toolkit>[/bold purple] ")
                self._dispatch(command)
            except KeyboardInterrupt:
                self.console.print()
                current_time = time.time()
                # Exit on second Ctrl+C within 2 seconds to prevent accidental exits
                if current_time - self._last_ctrl_c_time < 2.0:
                    self.logger.warning("Received second Ctrl+C press. Exiting.")
                    self.console.print("Goodbye!")
                    sys.exit(0)
                else:
                    self._last_ctrl_c_time = current_time
                    self.logger.warning("Received first Ctrl+C press.")
                    self.console.print(
                        "[bold yellow]Press Ctrl+C again "
                        "within 2 seconds to exit.[/bold yellow]"
                    )
            except EOFError:
                self.console.print()
                self.logger.warning("Received EOF signal. Exiting.")
                self.console.print("Goodbye!")
                sys.exit(0)

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
        if args:
            self.logger.debug("Handling 'alias' command with arguments: %s", args)
            sub_command = args[0]
            sub_args = args[1:]

            match sub_command:
                case "create" | "c":
                    if len(sub_args) == 2:
                        alias_name, command = sub_args
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
                                style="bold red",
                            )
                            return
                        self.aliases[alias_name] = command
                        self.aliases.save()
                        self.logger.info(
                            "Alias '%s' created for command '%s'",
                            alias_name,
                            command,
                        )
                        self.console.print(
                            f"Alias '{alias_name}' created for command '{command}'.",
                            style="bold green",
                        )
                    else:
                        self.logger.info("Invalid alias creation usage.")
                        self.console.print(
                            "Invalid alias creation usage. "
                            "For more information, type 'help alias'.",
                            style="bold red",
                        )
                case "delete" | "d":
                    if len(sub_args) == 1:
                        alias_name = sub_args[0]
                        if alias_name in self.aliases:
                            del self.aliases[alias_name]
                            self.aliases.save()
                            self.logger.info("Alias '%s' deleted.", alias_name)
                            self.console.print(
                                f"Alias '{alias_name}' deleted.", style="bold green"
                            )
                        else:
                            self.logger.warning("Alias '%s' not found.", alias_name)
                            self.console.print(
                                f"Alias '{alias_name}' not found.", style="bold red"
                            )
                    else:
                        self.logger.info("Invalid alias deletion usage.")
                        self.console.print(
                            "Invalid alias deletion usage. "
                            "For more information, type 'help alias'.",
                            style="bold red",
                        )
                case unknown_command:
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'. "
                        "Please enter an existing sub-command.",
                        style="bold red",
                    )

        else:
            self.logger.debug("Listing all command aliases.")

            if self.aliases:
                alias_list = [
                    f"[blue]{alias}[/blue]: {cmd}"
                    for alias, cmd in self.aliases.items()
                ]
                self.console.print(
                    Panel(
                        "\n".join(alias_list), title="Command Aliases", highlight=True
                    )
                )
            else:
                self.console.print("No command aliases defined.")
                return

    def cmd_clear(self, args: list[str]):  # noqa: D417
        """Clear the console screen.

        Usage:
            clear: Clear the console screen.

        """
        if args:
            self.logger.info("Invalid clear command usage.")
            self.console.print(
                "Invalid clear command usage. For more information, type 'help clear'.",
                style="bold red",
            )
            return
        self.console.clear()
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
        if args:
            self.logger.debug("Handling 'config' command with arguments.")
            sub_command = args[0]
            sub_args = args[1:]

            match sub_command:
                case "set" | "s":
                    if len(sub_args) == 3:
                        category = sub_args[0].lower()
                        key = sub_args[1].lower()
                        value = sub_args[2]
                        # Convert the value string to a boolean if necessary
                        match value.lower():
                            case "true":
                                value = True
                            case "false":
                                value = False
                        if category not in self.config:
                            self.logger.warning(
                                "Failed to set configuration value. "
                                "Category '%s' does not exist.",
                                category,
                            )
                            self.console.print(
                                "Failed to set configuration value. "
                                f"Category '{category}' does not exist.",
                                style="bold red",
                            )
                            return
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
                                style="bold red",
                            )
                            return
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
                                style="bold red",
                            )
                            return
                        self.config[category][key] = value
                        self.config.save()
                        self.logger.info(
                            "Configuration value set: %s.%s = %s",
                            category,
                            key,
                            value,
                        )
                        self.console.print(
                            "[bold green]Configuration value set:[/bold green] "
                            f"[blue]{category}.{key}[/blue]: {value}"
                        )
                    else:
                        self.logger.info("Invalid config usage.")
                        self.console.print(
                            "Invalid config usage. "
                            "For more information, type 'help config'.",
                            style="bold red",
                        )
                case "reset" | "rs":
                    if len(sub_args) == 2:
                        category = sub_args[0].lower()
                        key = sub_args[1].lower()
                        default_value = self.config.default.get(category, {}).get(key)
                        if category in self.config and key in self.config[category]:
                            if default_value is not None:
                                if Confirm().ask(
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
                                        "[bold green]Configuration "
                                        "value reset:[/bold green] "
                                        f"[blue]{category}.{key}[/blue]: "
                                        + str(default_value)
                                    )
                                else:
                                    self.logger.info("Operation aborted by user.")
                                    self.console.print(
                                        "Operation aborted.", style="bold yellow"
                                    )
                            else:
                                self.logger.info(
                                    "No default value found for "
                                    "category '%s' and key '%s'.",
                                    category,
                                    key,
                                )
                                self.console.print(
                                    f"No default value found for "
                                    f"category '{category}' and key '{key}'.",
                                    style="bold red",
                                )
                        else:
                            self.logger.info(
                                "Category '%s' or key '%s' not found.",
                                category,
                                key,
                            )
                            self.console.print(
                                f"Category '{category}' or key '{key}' not found.",
                                style="bold red",
                            )
                    else:
                        self.logger.info("Invalid config reset usage.")
                        self.console.print(
                            "Invalid config reset usage. "
                            "For more information, type 'help config'.",
                            style="bold red",
                        )
                case "reset_all" | "rsa":
                    if len(sub_args) == 0:
                        if Confirm().ask(
                            "Are you sure you want to reset all "
                            "configuration values to their default values?",
                            default=False,
                        ):
                            self.config.clear()
                            self.config.update(self.config.default)
                            self.config.save()
                            self.logger.info(
                                "All configuration values reset to defaults."
                            )
                            self.console.print(
                                "All configuration values reset to defaults.",
                                style="bold green",
                            )
                        else:
                            self.logger.info("Operation aborted by user.")
                            self.console.print(
                                "Operation aborted.", style="bold yellow"
                            )
                    else:
                        self.logger.info("Invalid config reset_all usage.")
                        self.console.print(
                            "Invalid config reset_all usage. "
                            "For more information, type 'help config'.",
                            style="bold red",
                        )
                case "reload" | "rl":
                    if len(sub_args) == 0:
                        self.config.load()
                        self.logger.info("Configuration reloaded from file.")
                        self.console.print(
                            "[bold green]Configuration reloaded from file.[/bold green]"
                        )
                    else:
                        self.logger.info("Invalid config reload usage.")
                        self.console.print(
                            "Invalid config reload usage. "
                            "For more information, type 'help config'.",
                            style="bold red",
                        )
                case unknown_command:
                    self.logger.warning("Unknown sub-command: '%s'", unknown_command)
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'", style="bold red"
                    )
                    return

        else:
            for category, settings in self.config.items():
                config_list = [
                    f"[blue]{key}[/blue]: {value}" for key, value in settings.items()
                ]
                self.console.print(
                    Panel(
                        "\n".join(config_list),
                        title=f"{category.capitalize()} Configuration",
                        highlight=True,
                    )
                )

    def cmd_echo(self, args: list[str]):  # noqa: D417
        """Echo the arguments.

        Usage:
            echo [args]: Echo the arguments.

        Arguments:
            args: The arguments to echo.

        """
        self.logger.info("Printing arguments: %s", args)
        self.console.print("\n".join(args))

    def cmd_exit(self, args: list[str]):  # noqa: D417
        """Exit the application.

        Equivalent to Ctrl+C, this command exits the application with code 0.

        Usage:
            exit: Exit the application with code 0.

        """
        if args:
            self.logger.info("Invalid exit command usage.")
            self.console.print(
                "Invalid exit command usage. For more information, type 'help exit'.",
                style="bold red",
            )
            return
        self.logger.info("Exit command received. Exiting...")
        self.console.print("Goodbye!")
        sys.exit(0)

    def cmd_help(self, args: list[str]):  # noqa: D417
        """Show help information for commands.

        Usage:
            help: Show command list.
            help <command>: Show detailed descriptions for <command>.

        Arguments:
            command: The specific command to show detailed help for.

        """
        if args:
            if len(args) > 1:
                self.logger.info("Invalid help command usage.")
                self.console.print(
                    "Invalid help command usage. "
                    "For more information, type 'help help'.",
                    style="bold red",
                )
                return
            cmd_name = args[0]
            self.logger.debug("Showing help for command '%s'", cmd_name)

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
                else:
                    self.console.print(
                        f"Command '{cmd_name}' has no description available."
                    )
            elif cmd_name in self.aliases:
                self.logger.debug("Showing help for alias '%s'", cmd_name)
                self.console.print(
                    f"Command '{cmd_name}' is an alias for '{self.aliases[cmd_name]}'."
                )
                self.console.print("Redirecting to the original command.")
                self.cmd_help([self.aliases[cmd_name].split(" ")[0]])
            else:
                self.console.print(
                    f"Command '{cmd_name}' not found. "
                    "Please enter an existing command.",
                    style="bold red",
                )

        else:
            self.logger.debug("Showing help for all commands.")

            command_list = []
            for method_name in dir(self):
                if not method_name.startswith("cmd_"):
                    continue
                if callable(method_attr := getattr(self, method_name, None)):
                    if method_doc := method_attr.__doc__:
                        self.logger.debug(
                            "Method '%s' has docstring. Adding to list.", method_name
                        )
                        command_list.append(
                            f"[blue]{method_name[4:]}[/blue]: "
                            + method_doc.splitlines()[0]
                        )
                    else:
                        self.logger.debug(
                            "Method '%s' has no docstring. "
                            "Adding default message to list.",
                            method_name,
                        )
                        command_list.append(
                            f"[blue]{method_name[4:]}[/blue]: No description available."
                        )

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
        if args:
            self.logger.debug("Handling 'plugin' command with arguments.")
            sub_command = args[0]
            sub_args = args[1:]

            match sub_command:
                case "load" | "l":
                    if len(sub_args) == 1:
                        try:
                            load_state = self.plugin_manager.load_plugin(sub_args[0])
                        except Exception as e:
                            self.logger.error(
                                "Failed to load plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to load plugin '{sub_args[0]}': {e}",
                                style="bold red",
                            )
                        else:
                            self.console.print(
                                f"Loaded plugin: {sub_args[0]}",
                                style="bold green",
                            ) if load_state else self.console.print(
                                f"Plugin '{sub_args[0]}' is already loaded.",
                                style="bold yellow",
                            )
                    else:
                        self.logger.info("Invalid plugin load usage.")
                        self.console.print(
                            "Invalid plugin load usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "unload" | "u":
                    if len(sub_args) == 1:
                        try:
                            self.plugin_manager.unload_plugin(sub_args[0])
                        except Exception as e:
                            self.logger.error(
                                "Failed to unload plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to unload plugin '{sub_args[0]}': {e}",
                                style="bold red",
                            )
                        else:
                            self.console.print(
                                f"Unloaded plugin: {sub_args[0]}", style="bold green"
                            )
                    else:
                        self.logger.info("Invalid plugin unload usage.")
                        self.console.print(
                            "Invalid plugin unload usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "reload" | "r":
                    if len(sub_args) == 1:
                        try:
                            self.plugin_manager.reload_plugin(sub_args[0])
                        except Exception as e:
                            self.logger.error(
                                "Failed to reload plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to reload plugin '{sub_args[0]}': {e}",
                                style="bold red",
                            )
                        else:
                            self.console.print(
                                f"Reloaded plugin: {sub_args[0]}", style="bold green"
                            )
                    else:
                        self.logger.info("Invalid plugin reload usage.")
                        self.console.print(
                            "Invalid plugin reload usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "disable" | "dis":
                    if len(sub_args) == 1:
                        try:
                            self.plugin_manager.disable_plugin(sub_args[0])
                        except Exception as e:
                            self.logger.error(
                                "Failed to disable plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to disable plugin '{sub_args[0]}': {e}",
                                style="bold red",
                            )
                        else:
                            self.console.print(
                                f"Disabled plugin: {sub_args[0]}", style="bold green"
                            )
                    else:
                        self.logger.info("Invalid plugin disable usage.")
                        self.console.print(
                            "Invalid plugin disable usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "enable" | "en":
                    if len(sub_args) == 1:
                        try:
                            self.plugin_manager.enable_plugin(sub_args[0])
                        except Exception as e:
                            self.logger.error(
                                "Failed to enable plugin '%s': %s", sub_args[0], e
                            )
                            self.console.print(
                                f"Failed to enable plugin '{sub_args[0]}': {e}",
                                style="bold red",
                            )
                        else:
                            self.console.print(
                                f"Enabled plugin: {sub_args[0]}", style="bold green"
                            )
                    else:
                        self.logger.info("Invalid plugin enable usage.")
                        self.console.print(
                            "Invalid plugin enable usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "help" | "h":
                    if len(sub_args) == 1:
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
                            else:
                                self.console.print(
                                    f"Plugin '{plugin_name}' has "
                                    "no description available."
                                )
                        else:
                            self.console.print(
                                f"Plugin '{plugin_name}' not found. "
                                "Please enter an existing plugin name.",
                                style="bold red",
                            )
                    else:
                        self.logger.info("Invalid plugin help usage.")
                        self.console.print(
                            "Invalid plugin help usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "load_all" | "la":
                    if not sub_args:
                        loaded_count = self.plugin_manager.load_all_plugins(
                            self.console
                        )
                        self.console.print(
                            f"Loaded {loaded_count} plugins.", style="bold green"
                        )
                    else:
                        self.logger.info("Invalid plugin load_all usage.")
                        self.console.print(
                            "Invalid plugin load_all usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "unload_all" | "ua":
                    if not sub_args:
                        unloaded_count = self.plugin_manager.unload_all_plugins()
                        self.console.print(
                            f"Unloaded {unloaded_count} plugins.", style="bold green"
                        )
                    else:
                        self.logger.info("Invalid plugin unload_all usage.")
                        self.console.print(
                            "Invalid plugin unload_all usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case "reload_all" | "ra":
                    if not sub_args:
                        reloaded_count = self.plugin_manager.reload_all_plugins()
                        self.console.print(
                            f"Reloaded {reloaded_count} plugins.", style="bold green"
                        )
                    else:
                        self.logger.info("Invalid plugin reload_all usage.")
                        self.console.print(
                            "Invalid plugin reload_all usage. "
                            "For more information, type 'help plugin'.",
                            style="bold red",
                        )
                case unknown_command:
                    self.console.print(
                        f"Unknown sub-command: '{unknown_command}'. "
                        "Please enter an existing sub-command.",
                        style="bold red",
                    )

        else:
            self.logger.debug("Listing all plugins.")

            loaded_plugin = []
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
                else:
                    self.logger.debug(
                        "Plugin '%s' has no docstring. Adding default message to list.",
                        plugin_name,
                    )
                    loaded_plugin.append(
                        f"[blue]{plugin_name}[/blue]: No description available."
                    )

            unloaded_plugin = []
            for file in self.plugin_manager.plugin_dir.iterdir():
                if file.is_file() and file.suffix == ".py":
                    plugin_name = file.stem
                    if plugin_name not in self.plugin_manager.plugin_instances:
                        unloaded_plugin.append(f"[blue]{plugin_name}[/blue]: Unloaded")

            disabled_plugin = []
            for plugin_name in self.plugin_manager.disabled_plugins:
                disabled_plugin.append(f"[blue]{plugin_name}[/blue]: Disabled")

            (
                self.console.print(
                    Panel(
                        "\n".join(loaded_plugin), title="Loaded Plugins", highlight=True
                    )
                )
                if loaded_plugin
                else self.console.print("No plugins loaded.")
            )
            (
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
            (
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

    def cmd_run(self, args: list[str]):  # noqa: D417
        """Run a command in the shell.

        Usage:
            run <command>: Run a command in the shell.

        Arguments:
            command: The command to run.

        """
        self.logger.debug("Running command: %s", args)
        try:
            subprocess.run(args, shell=True, text=True)
        except Exception as e:
            self.logger.error("Command failed: %s", e)
            self.console.print(
                f"Command '{' '.join(args)}' failed: {e}", style="bold red"
            )
            return

    def cmd_version(self, args: list[str]):  # noqa: D417
        """Display the version of CLI-Toolkit application and plugins.

        Usage:
            version: Display the version of the CLI-Toolkit application.
        """
        if args:
            self.logger.info("Invalid version command usage.")
            self.console.print(
                "Invalid version command usage. "
                "For more information, type 'help version'.",
                style="bold red",
            )
            return
        app_version = [
            "[blue]Python[/blue] v" + ".".join([str(part) for part in PYTHON_VERSION]),
            "[blue]CLI-Toolkit[/blue] v"
            + ".".join([str(part) for part in self.VERSION]),
        ]
        self.console.print(Panel("\n".join(app_version), title="Application Versions"))

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
