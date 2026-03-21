"""Plugin system for the CLI-Tookit application."""
import importlib.util # Import importlib for dynamic module loading
import os # Import os for file system operations
from pathlib import Path # Import Path from pathlib for handling file paths

from src.util.message import * # Message module

class BasePlugin:
    """Base class for plugins in the CLI-Tookit application."""
    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
        """
        self.master = master # Reference to the main application, can be used by plugins to interact with the application

class PluginManager:
    """Manager class for handling plugins in the CLI-Tookit application."""
    def __init__(self, master, plugin_dir: Path = Path("plugin")):
        """Initialize the plugin manager.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
            plugin_dir (Path, optional): The directory where plugins are stored. Defaults to "plugin
        """
        self.master = master # Reference to the main application, can be used by plugins to interact with the application
        self.plugins: dict[str, BasePlugin] = {} # Dictionary to store loaded plugins
        self.plugin_dir = plugin_dir # Directory where plugins are stored
        if not self.plugin_dir.exists(): # Check if the plugin directory exists
            show_warning("Plugin", "Plugin directory does not exist. Creating...")
            os.mkdir(self.plugin_dir) # Create the plugin directory if it does not exist
        show_info("Plugin", "Plugin manager initialized.")

    def load_plugin(self, plugin_name: str):
        """load a new plugin.
        Args:
            plugin_name (str): The name of a plugin to be loaded.
        """
        if plugin_name in self.plugins: # Check if the plugin is already loaded
            show_error("Plugin", f"Plugin '{plugin_name}' is already loaded.")
            return
        plugin_path = self.plugin_dir / f"{plugin_name}.py"
        if plugin_path.exists(): # Check if the plugin file exists
            try: # Try to load the plugin
                spec = importlib.util.spec_from_file_location(plugin_name, plugin_path) # Create a module spec
                if not (spec and spec.loader): # Check if the module spec is valid
                    raise ImportError("Invalid module spec")
                module = importlib.util.module_from_spec(spec) # Load the module
                spec.loader.exec_module(module) # Execute the module to import the plugin
                if not hasattr(module, "Plugin"): # Check if the plugin class exists
                    raise AttributeError("Plugin class not found in module")
                plugin_instance: BasePlugin = module.Plugin(self.master) # Create an instance of the plugin
                self.plugins[plugin_name] = plugin_instance # Add the plugin to the plugin manager
                for method_name in dir(plugin_instance):
                    if not method_name.startswith("cmd_"): # Only consider methods that start with "cmd_" as commands to be added to the main application
                        continue
                    method_attr = getattr(plugin_instance, method_name, None) # Get the method attribute from the plugin instance
                    if callable(method_attr): # Check if the method attribute is callable (i.e., it's a method)
                        setattr(self.master, method_name, method_attr)
                show_success("Plugin", f"Plugin '{plugin_name}' loaded successfully.")
            except Exception as e: # If an error occurs during loading, display an error message
                show_error(
                    "Plugin",
                    f"Failed to load plugin '{plugin_name}': {str(e)}."
                )
                return
        else: # If the plugin file does not exist, display an error message
            show_error("Plugin", f"Plugin file '{plugin_name}.py' not found.")
            return

    def unload_plugin(self, plugin_name: str):
        """Unload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be unloaded.
        """
        if plugin_name in self.plugins: # Check if the plugin is loaded
            del self.plugins[plugin_name] # Remove the plugin from the dictionary of loaded plugins
            show_success("Plugin", f"Plugin '{plugin_name}' unloaded successfully.")
        else:
            show_error("Plugin", f"Plugin '{plugin_name}' not found.")
    
    def reload_plugin(self, plugin_name: str):
        """Reload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be reloaded.
        """
        if plugin_name in self.plugins: # Check if the plugin is loaded
            self.unload_plugin(plugin_name) # Unload the plugin
            self.load_plugin(plugin_name) # Load the plugin again
            show_success("Plugin", f"Plugin '{plugin_name}' reloaded successfully.")
        else: # If the plugin is not loaded, display an error message
            show_error("Plugin", f"Plugin '{plugin_name}' not found.")
            return

    def load_all_plugins(self):
        """Load all plugins in the plugin directory."""
        for file in self.plugin_dir.iterdir(): # Iterate over all files in the plugin directory
            if file.is_file() and file.suffix == ".py": # Check if the file is a Python module
                plugin_name = file.stem # Get the plugin name from the file name
                if plugin_name in self.plugins: # Check if the plugin is already loaded
                    continue
                self.load_plugin(plugin_name) # Load the plugin
        show_success("Plugin", f"All plugins loaded successfully.")

    def unload_all_plugins(self):
        """Unload all plugins."""
        for plugin_name in list(self.plugins.keys()): # Iterate over all loaded plugins
            self.unload_plugin(plugin_name) # Unload the plugin
        show_success("Plugin", f"All plugins unloaded successfully.")

    def reload_all_plugins(self):
        """Reload all plugins."""
        for plugin_name in list(self.plugins.keys()): # Iterate over all loaded plugins
            self.reload_plugin(plugin_name) # Reload the plugin
        show_success("Plugin", f"All plugins reloaded successfully.")