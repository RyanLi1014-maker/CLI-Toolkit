"""CLI-Tookit Application"""
from colorama import Fore, Style # Import colorama for colored output in the terminal

from src.cli import CLI # Command-line interface module
from src.plugin import PluginManager # Plugin manager module
from src.util.message import * # Message module

logo = r"""
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

class CLI_Toolkit_App(CLI):
    """Command-line interface class."""
    def __init__(self):
        """Initialize the CLI-Tookit application."""
        print(logo) # Print the logo when the application starts
        self.plugin_manager = PluginManager(self)
        self.plugin_manager.load_all_plugins()
        print() # Print a new line
        super().__init__(
            prompt="CLI-Toolkit> ", # Prompt for user input
            intro=( # Introduction message displayed when the application starts
                "Welcome to the CLI Toolkit! Type 'help' to list commands.\n"
                "Type 'exit' to exit the application."
            )
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
        if args: # If arguments are provided, handle them
            sub_command = args[0]
            sub_args = args[1:]
            match sub_command: # Match the sub-command
                case "load":
                    self.plugin_manager.load_plugin(sub_args[0]) if sub_args else show_error("Plugin", "Please provide a plugin name.")
                case "unload":
                    self.plugin_manager.unload_plugin(sub_args[0]) if sub_args else show_error("Plugin", "Please provide a plugin name.")
                case "reload":
                    self.plugin_manager.reload_plugin(sub_args[0]) if sub_args else show_error("Plugin", "Please provide a plugin name.")
                case "load_all":
                    self.plugin_manager.load_all_plugins()
                case "unload_all":
                    self.plugin_manager.unload_all_plugins()
                case "reload_all":
                    self.plugin_manager.reload_all_plugins()
                case unknown_command: # If an unknown sub-command is provided, show an error message
                    self.show_unknown_cmd(unknown_command)
        else: # If no arguments are provided, list all plugins
            if not self.plugin_manager.plugins: # If no plugins are loaded, show a warning message
                show_info("Plugin", "No plugins loaded.")
                return
            print(Fore.GREEN + "Plugins:" + Style.RESET_ALL)
            for plugin_name, plugin_instance in self.plugin_manager.plugins.items(): # Iterate through all plugins
                if plugin_instance.__doc__: # If the plugin has a docstring, show it as description for the plugin
                    print(
                        Fore.BLUE + f"    {plugin_name}:" + Style.RESET_ALL,
                        plugin_instance.__doc__.splitlines()[0] # Show only the first line of the description for brevity
                    )
                else: # If the plugin has no docstring, show a default message
                    print(
                        Fore.BLUE + f"    {plugin_name}:" + Style.RESET_ALL,
                        "No description available."
                    )