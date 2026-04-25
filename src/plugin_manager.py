"""Plugin Manager"""

# Import libraries
import importlib.util
from logging import getLogger
from pathlib import Path

# Import modules
from api import BasePlugin
from util.config import SetConfig
from exception import (
    PluginDisabledError,
    PluginNotFoundError,
    PluginAlreadyLoadedWarning,
)


# Set up the base logger
logger = getLogger("CLI-Toolkit")


class PluginManager:
    """Manager class for handling plugins in the CLI-Toolkit application."""

    def __init__(self, master, plugin_dir: Path = Path("plugin")):
        """Initialize the plugin manager.
        Args:
            master: A reference to the main application, can be used by plugins to interact with the application.
            plugin_dir (Path, optional): The directory where plugins are stored. Defaults to "plugin".
        """
        self.master = master  # Reference to the main application, can be used by plugins to interact with the application
        self.logger = logger.getChild("PluginManager")
        # Dictionary to store loaded plugins
        self.plugin_instances: dict[str, BasePlugin] = {}

        # Get the core commands from the main application
        self._core_commands: set[str] = {  # Set of core commands
            method_name
            for method_name in dir(master)
            if method_name.startswith("cmd_")
            and callable(getattr(master, method_name, None))
        }
        # Dictionary to store commands registered by plugins
        self._plugin_commands: dict[str, set[str]] = {}
        # Dictionary to store the owner of each command
        self._command_owners: dict[str, str] = {}

        # Initialize the plugin directory and disabled plugins
        self.plugin_dir = plugin_dir  # Directory where plugins are stored
        self.disabled_plugins = SetConfig(  # Set of disabled plugins
            Path("CLI-Toolkit/disabled_plugins.json")
        )
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            self.logger.warning("Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir(parents=True)

    def load_plugin(self, plugin_name: str):
        """Load a new plugin.
        Args:
            plugin_name (str): The name of a plugin to be loaded.
        """
        self.logger.info(f"Loading plugin '{plugin_name}'.")

        # Check before loading
        if plugin_name in self.disabled_plugins:  # Check if the plugin is disabled
            raise PluginDisabledError(f"Plugin '{plugin_name}' is disabled.")
        if (
            plugin_name in self.plugin_instances
        ):  # Check if the plugin is already loaded
            raise PluginAlreadyLoadedWarning(
                f"Plugin '{plugin_name}' is already loaded."
            )
        if (  # Check if the plugin name is valid
            ".." in plugin_name or "/" in plugin_name or "\\" in plugin_name
        ):
            raise ValueError(f"Invalid plugin name: {plugin_name}")
        if not self.plugin_dir.exists():  # Check if the plugin directory exists
            self.logger.warning("Plugin directory does not exist. Creating...")
            self.plugin_dir.mkdir(parents=True)

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
                raise AttributeError(
                    f"Plugin '{plugin_name}' does not have a 'Plugin' class."
                )
            if not issubclass(  # Check if the plugin class is a subclass of BasePlugin
                module.Plugin, BasePlugin
            ):
                raise TypeError(
                    f"Plugin '{plugin_name}' does not inherit from BasePlugin."
                )

            # Create an instance of the plugin class
            plugin_instance: BasePlugin = module.Plugin(self.master)
            self.logger.debug(f"Plugin instance: {plugin_instance}")

            # Collect all command methods exported by the plugin
            plugin_methods: dict[str, object] = {}
            for method_name in dir(plugin_instance):
                if not method_name.startswith("cmd_"):
                    continue
                if callable(method_attr := getattr(plugin_instance, method_name, None)):
                    plugin_methods[method_name] = method_attr

            # Validate command collisions before injecting methods into the app
            for method_name in plugin_methods:
                if method_name in self._core_commands:
                    raise ValueError(
                        f"Plugin '{plugin_name}' command '{method_name[4:]}' conflicts with a built-in command."
                    )
                if method_name in self._command_owners:
                    raise ValueError(
                        f"Plugin '{plugin_name}' command '{method_name[4:]}' conflicts with command from plugin '{self._command_owners[method_name]}'."
                    )

            # Add validated plugin commands into the main application
            registered_commands: set[str] = set()
            for method_name, method_attr in plugin_methods.items():
                setattr(self.master, method_name, method_attr)
                self._command_owners[method_name] = plugin_name
                registered_commands.add(method_name)
                self.logger.debug(f"Added command '{method_name[4:]}' to CLI.")
            self.plugin_instances[plugin_name] = plugin_instance
            self._plugin_commands[plugin_name] = registered_commands

            # Log a message
            self.logger.info(f"Loaded plugin '{plugin_name}'.")

        else:  # If the plugin file does not exist, raise an error
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

    def unload_plugin(self, plugin_name: str):
        """Unload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be unloaded.
        """
        self.logger.info(f"Unloading plugin '{plugin_name}'.")

        # Check if the plugin is loaded
        if plugin_name in self.plugin_instances:
            # Get the plugin instance
            plugin_instance = self.plugin_instances[plugin_name]
            self.logger.debug(f"Plugin instance: {plugin_instance}")

            # Remove only commands previously registered by this plugin
            for method_name in self._plugin_commands.get(plugin_name, set()):
                if self._command_owners.get(method_name) != plugin_name:
                    continue
                if hasattr(self.master, method_name):
                    delattr(self.master, method_name)
                    self.logger.debug(f"Removed command '{method_name[4:]}' from CLI.")
                del self._command_owners[method_name]
            self._plugin_commands.pop(plugin_name, None)

            # Remove the plugin from the dictionary of loaded plugins
            del self.plugin_instances[plugin_name]

            # Log a message
            self.logger.info(f"Unloaded plugin '{plugin_name}'.")

        else:  # If the plugin was not found, raise an error
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

    def reload_plugin(self, plugin_name: str):
        """Reload a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be reloaded.
        """
        self.logger.info(f"Reloading plugin '{plugin_name}'.")
        self.unload_plugin(plugin_name)  # Unload the plugin
        self.load_plugin(plugin_name)  # Load the plugin again
        self.logger.info(f"Reloaded plugin '{plugin_name}'.")

    def disable_plugin(self, plugin_name: str):
        """Disable a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be disabled.
        """
        self.logger.info(f"Disabling plugin '{plugin_name}'.")
        # Check if the plugin is already disabled
        if plugin_name in self.disabled_plugins:
            raise PluginDisabledError(f"Plugin '{plugin_name}' is already disabled.")

        self.disabled_plugins.add(plugin_name)
        self.disabled_plugins.save()  # Save the updated set of disabled plugins to the file
        if (
            plugin_name in self.plugin_instances
        ):  # If the plugin is currently loaded, unload it
            self.unload_plugin(plugin_name)
        self.logger.info(f"Disabled plugin '{plugin_name}'.")

    def enable_plugin(self, plugin_name: str):
        """Enable a plugin by its name.
        Args:
            plugin_name (str): The name of the plugin to be enabled.
        """
        self.logger.info(f"Enabling plugin '{plugin_name}'.")
        # Check if the plugin is not disabled
        if plugin_name not in self.disabled_plugins:
            raise PluginNotFoundError(f"Plugin '{plugin_name}' is not disabled.")

        self.disabled_plugins.remove(plugin_name)
        self.disabled_plugins.save()  # Save the updated set of disabled plugins to the file
        (  # Load the plugin if the configuration option is enabled
            self.load_plugin(plugin_name)
            if self.master.config["plugin"]["load_on_enable"]
            else None
        )
        self.logger.info(f"Enabled plugin '{plugin_name}'.")

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
                # Skip disabled plugins and already loaded plugins
                if plugin_name in self.disabled_plugins:  # Skip disabled plugins
                    self.logger.info(f"Plugin '{plugin_name}' is disabled. Skipping...")
                    continue
                if plugin_name in self.plugin_instances:  # Skip already loaded plugins
                    self.logger.info(
                        f"Plugin '{plugin_name}' is already loaded. Skipping..."
                    )
                    continue
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
        for plugin_name in list(self.plugin_instances.keys()):
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
        for plugin_name in list(self.plugin_instances.keys()):
            self.reload_plugin(plugin_name)  # Reload the plugin
            reloaded_count += 1

        self.logger.info(f"Reloaded {reloaded_count} plugins.")
        return reloaded_count
