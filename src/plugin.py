"""Plugin system for the CLI-Tookit application."""

import importlib.util  # Import importlib for dynamic module loading
from pathlib import Path  # Import Path from pathlib for handling file paths
import logging  # Import logging for logging


class PluginWarning(Warning):
    """Custom warning class for plugin-related warnings."""

    pass


class PluginAlreadyLoadedWarning(PluginWarning):
    """Warning raised when a plugin is already loaded."""

    pass


class PluginNotFoundWarning(PluginWarning):
    """Warning raised when a plugin is not found."""

    pass


class BasePlugin:
    """Base class for plugins in the CLI-Tookit application."""

    VERSION = "0.0.0"  # Version number of the plugin

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
        self.logger = logging.getLogger("PluginManager")
        self.plugins: dict[str, BasePlugin] = {}  # Dictionary to store loaded plugins
        self.plugin_dir = plugin_dir  # Directory where plugins are stored
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            self.logger.warning("Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir()

    def load_plugin(self, plugin_name: str):
        """load a new plugin.
        Args:
            plugin_name (str): The name of a plugin to be loaded.
        """
        self.logger.info(f"Loading plugin '{plugin_name}'.")

        # Check before loading
        if plugin_name in self.plugins:  # Check if the plugin is already loaded
            raise PluginAlreadyLoadedWarning(
                f"Plugin '{plugin_name}' is already loaded."
            )
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            self.logger.warning("Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir()

        # Get the path to the plugin file
        plugin_path = self.plugin_dir / f"{plugin_name}.py"
        if plugin_path.exists():  # Check if the plugin file exists

            # Create a module spec
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not (spec and spec.loader):  # Check if the module spec is invalid
                raise ValueError("Invalid module spec.")

            # Load the module
            module = importlib.util.module_from_spec(spec)  # Load the module
            spec.loader.exec_module(module)  # Execute the module to import the plugin
            if not hasattr(module, "Plugin"):  # Check if the plugin class exists
                self.logger.error("Plugin class does not exist.")

            # Create an instance of the plugin class
            plugin_instance: BasePlugin = module.Plugin(self.master)
            self.plugins[plugin_name] = plugin_instance
            self.logger.debug(f"Plugin instance: {plugin_instance}")

            # Add all methods in the plugin instance to the main application
            for method_name in dir(plugin_instance):
                # Skip object name that don't start with "cmd_"
                if not method_name.startswith("cmd_"):
                    continue
                # Get the object attribute from the plugin instance
                method_attr = getattr(plugin_instance, method_name, None)
                # Add the method to the main application
                if callable(method_attr):  # Check if the method attribute is callable
                    setattr(self.master, method_name, method_attr)
                    self.logger.debug(f"Added command '{method_name[4:]}' to CLI.")

            # Log a message
            self.logger.info(f"Loaded plugin '{plugin_name}'.")

        else:  # If the plugin file does not exist, raise an error
            raise FileNotFoundError(f"Plugin file '{plugin_name}.py' does not exist.")

    def unload_plugin(self, plugin_name: str):
        """Unload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be unloaded.
        """
        self.logger.info(f"Unloading plugin '{plugin_name}'.")

        # Check if the plugin is loaded
        if plugin_name in self.plugins:

            # Get the plugin instance
            plugin_instance = self.plugins[plugin_name]
            self.logger.debug(f"Plugin instance: {plugin_instance}")

            # Remove all methods in the plugin instance from the main application
            for method_name in dir(plugin_instance):
                # Skip methods that don't start with "cmd_"
                if not method_name.startswith("cmd_"):
                    continue
                # Get the method attribute
                method_attr = getattr(plugin_instance, method_name, None)
                # Remove the method from the main application
                if callable(method_attr) and hasattr(self.master, method_name):
                    delattr(self.master, method_name)
                    self.logger.debug(f"Removed command '{method_name[4:]}' from CLI.")

            # Remove the plugin from the dictionary of loaded plugins
            del self.plugins[plugin_name]

            # Log a message
            self.logger.info(f"Unloaded plugin '{plugin_name}'.")

        else:  # If the plugin was not found, raise an error
            raise PluginNotFoundWarning(f"Plugin '{plugin_name}' not found.")

    def reload_plugin(self, plugin_name: str):
        """Reload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be reloaded.
        """
        self.logger.info(f"Reloading plugin '{plugin_name}'.")
        self.unload_plugin(plugin_name)  # Unload the plugin
        self.load_plugin(plugin_name)  # Load the plugin again
        self.logger.info(f"Reloaded plugin '{plugin_name}'.")

    def load_all_plugins(self):
        """Load all plugins in the plugin directory.
        Returns:
            int: The number of plugins loaded.
        """
        self.logger.info("Loading all plugins.")
        loaded_count = 0  # Count the number of loaded plugins

        # Iterate over all files in the plugin directory
        for file in self.plugin_dir.iterdir():
            if file.is_file() and file.suffix == ".py":  # Skip non-Python files
                # Get the plugin name from the file name
                plugin_name = file.stem
                # Load the plugin
                try:  # Try to load the plugin
                    self.load_plugin(plugin_name)
                except Warning as w:  # If a warning occurs, log it as a warning
                    self.logger.warning(f"Failed to load plugin '{plugin_name}': {w}")
                    self.master.console.print(  # Log the warning message to the console
                        f"Failed to load plugin '{plugin_name}': {w}", style="yellow"
                    )
                except Exception as e:  # If any other exception occurs, log an error
                    self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")
                    self.master.console.print(  # Log the error message to the console
                        f"Failed to load plugin '{plugin_name}': {e}", style="red"
                    )
                else:  # If the plugin was loaded successfully, log an info
                    loaded_count += 1

        self.logger.info(f"Loaded {loaded_count} plugins.")
        return loaded_count

    def unload_all_plugins(self):
        """Unload all plugins.
        Returns:
            int: The number of plugins unloaded.
        """
        self.logger.info("Unloading all plugins.")
        unloaded_count = 0  # Count the number of unloaded plugins

        # Iterate over all loaded plugins
        for plugin_name in list(self.plugins.keys()):
            self.unload_plugin(plugin_name)  # Unload the plugin
            unloaded_count += 1

        self.logger.info(f"Unloaded {unloaded_count} plugins.")
        return unloaded_count

    def reload_all_plugins(self):
        """Reload all plugins.
        Returns:
            int: The number of plugins reloaded.
        """
        self.logger.info("Reloading all plugins.")
        reloaded_count = 0  # Count the number of reloaded plugins

        # Iterate over all loaded plugins
        for plugin_name in list(self.plugins.keys()):
            self.reload_plugin(plugin_name)  # Reload the plugin
            reloaded_count += 1

        self.logger.info(f"Reloaded {reloaded_count} plugins.")
        return reloaded_count
