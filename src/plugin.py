"""Plugin system for the CLI-Tookit application."""

import importlib.util  # Import importlib for dynamic module loading
from pathlib import Path  # Import Path from pathlib for handling file paths

from src.util.message import *  # Message module


class PluginError(Exception):
    """Exception raised when an error occurs during plugin loading."""

    pass


class PluginAlreadyLoadedError(PluginError):
    """Exception raised when a plugin is already loaded."""

    pass


class PluginNotFoundError(PluginError):
    """Exception raised when a plugin is not found."""

    pass


class BasePlugin:
    """Base class for plugins in the CLI-Tookit application."""

    VERSION = "1.0.0"  # Version number of the plugin

    def __init__(self, master):
        """Initialize the plugin.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
        """
        self.master = master  # Reference to the main application, can be used by plugins to interact with the application


class PluginManager:
    """Manager class for handling plugins in the CLI-Tookit application."""

    def __init__(self, master, plugin_dir: Path = Path("plugin")):
        """Initialize the plugin manager.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
            plugin_dir (Path, optional): The directory where plugins are stored. Defaults to "plugin
        """
        self.master = master  # Reference to the main application, can be used by plugins to interact with the application
        self.plugins: dict[str, BasePlugin] = {}  # Dictionary to store loaded plugins
        self.plugin_dir = plugin_dir  # Directory where plugins are stored
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            show_warning("Plugin", "Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir()

    def load_plugin(self, plugin_name: str):
        """load a new plugin.
        Args:
            plugin_name (str): The name of a plugin to be loaded.
        """
        if plugin_name in self.plugins:  # Check if the plugin is already loaded
            raise PluginAlreadyLoadedError(
                f"Plugin '{plugin_name}' is already loaded."
            )  # Raise a PluginAlreadyLoadedError
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            show_warning("Plugin", "Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir()
        plugin_path = self.plugin_dir / f"{plugin_name}.py"
        if plugin_path.exists():  # Check if the plugin file exists
            spec = importlib.util.spec_from_file_location(
                plugin_name, plugin_path
            )  # Create a module spec
            if not (spec and spec.loader):  # Check if the module spec is valid
                raise ImportError(f"Invalid module spec for plugin '{plugin_name}'.")
            module = importlib.util.module_from_spec(spec)  # Load the module
            spec.loader.exec_module(module)  # Execute the module to import the plugin
            if not hasattr(module, "Plugin"):  # Check if the plugin class exists
                raise AttributeError(
                    f"Plugin class not found in plugin '{plugin_name}'."
                )
            plugin_instance: BasePlugin = module.Plugin(
                self.master
            )  # Create an instance of the plugin
            self.plugins[plugin_name] = (
                plugin_instance  # Add the plugin to the plugin manager
            )
            for method_name in dir(
                plugin_instance
            ):  # Iterate through all methods in the plugin instance
                if not method_name.startswith(
                    "cmd_"
                ):  # Only consider methods that start with "cmd_" as commands to be added to the main application
                    continue
                # Get the method attribute from the plugin instance
                method_attr = getattr(plugin_instance, method_name, None)
                if callable(method_attr):  # Check if the method attribute is callable
                    setattr(
                        self.master, method_name, method_attr
                    )  # Add the method to the main application
        else:  # If the plugin file does not exist
            raise FileNotFoundError(
                f"Plugin file '{plugin_name}.py' not found."
            )  # raise a FileNotFoundError

    def unload_plugin(self, plugin_name: str):
        """Unload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be unloaded.
        """
        if plugin_name in self.plugins:  # Check if the plugin is loaded
            plugin_instance = self.plugins[plugin_name]  # Get the plugin instance
            for method_name in dir(
                plugin_instance
            ):  # Iterate through all methods in the plugin instance
                if not method_name.startswith(
                    "cmd_"
                ):  # Only consider methods that start with "cmd_" as commands to be added to the main application
                    continue
                method_attr = getattr(
                    plugin_instance, method_name, None
                )  # Get the method attribute from the plugin instance
                if callable(method_attr) and hasattr(
                    self.master, method_name
                ):  # Check if the method attribute is callable (i.e., it's a method) and if it exists in the main application)
                    delattr(
                        self.master, method_name
                    )  # Remove the method from the main application
            del self.plugins[
                plugin_name
            ]  # Remove the plugin from the dictionary of loaded plugins
        else:  # If the plugin was not found, raise a PluginNotFoundError
            raise PluginNotFoundError(
                f"Plugin {plugin_name} not found"
            )  # raise an error if the plugin was not found

    def reload_plugin(self, plugin_name: str):
        """Reload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be reloaded.
        """
        self.unload_plugin(plugin_name)  # Unload the plugin
        self.load_plugin(plugin_name)  # Load the plugin again

    def load_all_plugins(self):
        """Load all plugins in the plugin directory."""
        loaded_count = 0  # Count the number of loaded plugins
        for file in self.plugin_dir.iterdir():
            if (
                file.is_file() and file.suffix == ".py"
            ):  # Check if the file is a Python module
                plugin_name = file.stem  # Get the plugin name from the file name
                if plugin_name in self.plugins:  # Check if the plugin is already loaded
                    continue
                try:
                    self.load_plugin(plugin_name)  # Load the plugin
                except Exception as e:
                    show_error("Plugin", str(e))
                else:
                    loaded_count += 1
        show_success("Plugin", f"Loaded {loaded_count} plugins.")

    def unload_all_plugins(self):
        """Unload all plugins."""
        unloaded_count = 0  # Count the number of unloaded plugins
        for plugin_name in list(self.plugins.keys()):  # Iterate over all loaded plugins
            try:
                self.unload_plugin(plugin_name)  # Unload the plugin
            except Exception as e:
                show_error("Plugin", str(e))
            else:
                unloaded_count += 1
        show_success("Plugin", f"Unloaded {unloaded_count} plugins.")

    def reload_all_plugins(self):
        """Reload all plugins."""
        reloaded_count = 0  # Count the number of reloaded plugins
        for plugin_name in list(self.plugins.keys()):  # Iterate over all loaded plugins
            try:
                self.reload_plugin(plugin_name)  # Reload the plugin
            except Exception as e:
                show_error("Plugin", str(e))
            else:
                reloaded_count += 1
        show_success("Plugin", f"Reloaded {reloaded_count} plugins.")
