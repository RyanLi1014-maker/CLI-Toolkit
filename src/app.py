"""CLI-Tookit Application"""

from sys import version_info  # Python version
from pathlib import Path  # File path handling
from colorama import Fore, Style  # Import colorama for colored output in the terminal

from src.cli import CLI  # Command-line interface module
from src.plugin import PluginManager  # Plugin manager module
from src.util.config import Config  # Configuration utilities module
from src.util.message import *  # Message module

PYTHON_VERSION = (
    f"{version_info.major}.{version_info.minor}.{version_info.micro}"  # Python version
)
APP_VERSION = "0.1.0"  # Application version
APP_LOGO = r"""
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


class CLI_Toolkit_App(CLI):
    """Command-line interface class."""

    VERSION = APP_VERSION  # Application version

    def __init__(self):
        """Initialize the CLI-Tookit application."""
        print(APP_LOGO)  # Print the logo when the application starts
        self.config = Config(
            config_path=Path("CLI-Toolkit.json"),  # Path to the configuration file
            default_config={  # Default configuration values
                "plg": {
                    "load_on_start": True,  # Whether to automatically load all plugins in the plugin directory when the application starts
                }
            },
        )
        self.config.load()  # Load the configuration from the file
        self.plugin_manager = PluginManager(self)  # Initialize the plugin manager
        # If the plugin system is enabled, initialize the plugin manager
        if self.config["plg"]["load_on_start"]:
            self.plugin_manager.load_all_plugins()  # Load all plugins in the plugin directory
        print()  # Print a new line
        super().__init__(
            prompt="CLI-Toolkit> ",  # Prompt for user input
            intro=(  # Introduction message displayed when the application starts
                "Welcome to the CLI Toolkit! Type 'help' to list commands.\n"
                "Type 'exit' to exit the application."
            ),
        )

    def cmd_version(self, _):
        """Display the version of the CLI-Toolkit application."""
        # Display Python version and CLI-Toolkit version
        print(Fore.GREEN + "Application version:" + Style.RESET_ALL)
        print(Fore.BLUE + "    Python" + Style.RESET_ALL, f"v{PYTHON_VERSION}")
        print(Fore.BLUE + "    CLI-Toolkit" + Style.RESET_ALL, f"v{APP_VERSION}")
        # Display plugin versions
        print(Fore.GREEN + "Plugin version:" + Style.RESET_ALL)
        for plugin_name, plugin in self.plugin_manager.plugins.items():
            print(
                Fore.BLUE + f"    {plugin_name}" + Style.RESET_ALL,
                f"v{plugin.VERSION}",
            )

    def cmd_plg(self, args: list):
        """Plugin management commands.
        Usage:
            plg: List all plugins.
            plg <command> <plugin name>: Manage plugins.
        Options:
            <command>: The command to execute. Can be one of the following:
                load: Load a plugin.
                unload: Unload a plugin.
                reload: Reload a plugin.
                load_all: Load all plugins in the plugin directory.
                unload_all: Unload all plugins that had already been loaded.
                reload_all: Reload all plugins that had already been loaded.
            <plugin name>: The name of the plugin to load, unload, or reload.
        """
        if args:  # If arguments are provided, handle them
            sub_command = args[0]
            sub_args = args[1:]
            match sub_command:  # Match the sub-command
                case "load":
                    if sub_args:  # If an argument is provided, load the plugin
                        try:  # Try to load the plugin
                            self.plugin_manager.load_plugin(sub_args[0])
                        except Exception as e:
                            show_error("Plugin", f"Error loading plugin: {e}")
                        else:  # If the plugin was loaded successfully, display a success message
                            show_success("Plugin", f"Plugin '{sub_args[0]}' loaded.")
                    else:  # Otherwise, raise an ValurError
                        show_error("Plugin", "Please provide a plugin name.")
                case "unload":
                    if sub_args:  # If an argument is provided, unload the plugin
                        try:  # Try to unload the plugin
                            self.plugin_manager.unload_plugin(sub_args[0])
                        except Exception as e:
                            show_error("Plugin", f"Error unloading plugin: {e}")
                        else:  # If the plugin was unloaded successfully, display a success message
                            show_success("Plugin", f"Plugin '{sub_args[0]}' unloaded.")
                    else:  # Otherwise, raise an ValurError
                        show_error("Plugin", "Please provide a plugin name.")
                case "reload":
                    if sub_args:  # If an argument is provided, reload the plugin
                        try:  # Try to reload the plugin
                            self.plugin_manager.reload_plugin(sub_args[0])
                        except Exception as e:
                            show_error("Plugin", f"Error reloading plugin: {e}")
                        else:  # If the plugin was reloaded successfully, display a success message
                            show_success("Plugin", f"Plugin '{sub_args[0]}' reloaded.")
                    else:  # Otherwise, raise an ValurError
                        show_error("Plugin", "Please provide a plugin name.")
                case "load_all":
                    self.plugin_manager.load_all_plugins()
                case "unload_all":
                    self.plugin_manager.unload_all_plugins()
                case "reload_all":
                    self.plugin_manager.reload_all_plugins()
                case (
                    unknown_command
                ):  # If an unknown sub-command is provided, show an error message
                    self.show_unknown_cmd(unknown_command)
        else:  # If no arguments are provided, list all plugins
            if (
                not self.plugin_manager.plugins
            ):  # If no plugins are loaded, show a warning message
                show_info("Plugin", "No plugins loaded.")
                return
            print(Fore.GREEN + "Plugins:" + Style.RESET_ALL)
            for (
                plugin_name,
                plugin_instance,
            ) in self.plugin_manager.plugins.items():  # Iterate through all plugins
                if (
                    plugin_instance.__doc__
                ):  # If the plugin has a docstring, show it as description for the plugin
                    print(
                        Fore.BLUE + f"    {plugin_name}:" + Style.RESET_ALL,
                        plugin_instance.__doc__.splitlines()[
                            0
                        ],  # Show only the first line of the description for brevity
                    )
                else:  # If the plugin has no docstring, show a default message
                    print(
                        Fore.BLUE + f"    {plugin_name}:" + Style.RESET_ALL,
                        "No description available.",
                    )
