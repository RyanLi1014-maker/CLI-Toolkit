"""Plugin Manager for the CLI-Toolkit application."""

# Import libraries
import importlib.util
from logging import getLogger
from pathlib import Path

from rich.console import Console

# Import modules
from api import BasePlugin
from src.exception import (
    PluginDisabledError,
    PluginLoadedError,
    PluginNotDisabledError,
    PluginNotFoundError,
)
from src.util.config import SetConfig
from src.util.project_root import PROJECT_ROOT

# Set up the base logger
logger = getLogger("CLI-Toolkit")


class PluginManager:
    """Manager class for handling plugins in the CLI-Toolkit application."""

    def __init__(self, master, plugin_dir: Path = Path("plugin")) -> None:
        """Initialize the plugin manager.

        Args:
            master: A reference to the main application.
                Can be used by plugins to interact with the application.
            plugin_dir (Path, optional): The directory where plugins are stored.
                Defaults to "plugin".

        """
        # Set up the attributes
        self.master = master  # Reference to the main application
        self.logger = logger.getChild("PluginManager")  # Logger
        self.plugin_instances: dict[  # Dictionary to store loaded plugins
            str, BasePlugin
        ] = {}

        # Set up the core commands and plugin commands
        self._core_commands: set[str] = {  # Set of core commands
            method_name
            for method_name in dir(master)
            if method_name.startswith("cmd_")
            and callable(getattr(master, method_name, None))
        }
        self._plugin_commands: dict[  # Dictionary to store plugin commands
            str, set[str]
        ] = {}
        self._command_owners: dict[  # Dictionary to store the owner of each command
            str, str
        ] = {}

        # Initialize the plugin directory
        self.plugin_dir = PROJECT_ROOT / plugin_dir  # Path to the plugin directory
        self.plugin_dir.mkdir(  # Check if the plugin directory exists
            parents=True, exist_ok=True
        )

        # Initialize the set of disabled plugins using a SetConfig instance
        self.disabled_plugins = SetConfig(  # Set of disabled plugins
            Path("CLI-Toolkit/disabled_plugins.json")
        )
        # Check if any disabled plugins don't exist
        # Create a temporary set to avoid modifying the original during iteration
        temp_disabled_plugins = self.disabled_plugins.copy()
        for plugin_name in temp_disabled_plugins:
            (  # Disable plugins that are in the disabled list but don't exist
                self.disabled_plugins.remove(plugin_name)
                if self.plugin_dir / f"{plugin_name}.py"
                not in self.plugin_dir.iterdir()
                else None
            )
        (  # Save the updated set of disabled plugins
            self.disabled_plugins.save()
            if temp_disabled_plugins != self.disabled_plugins
            else None
        )

    def load_plugin(self, plugin_name: str, loaded_ok: bool = False):
        """Load a new plugin.

        Args:
            plugin_name (str): The name of a plugin to be loaded.
            loaded_ok (bool, optional): Whether it's okay for the plugin
                to already be loaded. Defaults to True.

        """
        self.logger.info(f"Loading plugin '{plugin_name}'.")

        # Check before loading
        if plugin_name in self.disabled_plugins:  # Check if the plugin is disabled
            raise PluginDisabledError(f"Plugin '{plugin_name}' is disabled.")
        if (  # Check if the plugin is already loaded
            plugin_name in self.plugin_instances
        ):
            self.logger.warning(f"Plugin '{plugin_name}' is already loaded.")
            if not loaded_ok:
                raise PluginLoadedError(f"Plugin '{plugin_name}' is already loaded.")
        if (  # Check if the plugin name is valid
            ".." in plugin_name or "/" in plugin_name or "\\" in plugin_name
        ):
            raise ValueError(f"Invalid plugin name: {plugin_name}")
        self.plugin_dir.mkdir(  # Check if the plugin directory exists
            parents=True, exist_ok=True
        )

        # Get the path to the plugin file
        plugin_path = self.plugin_dir / f"{plugin_name}.py"

        # Load the plugin
        if plugin_path.exists():  # Check if the plugin file exists
            # Create a module spec
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not (spec and spec.loader):  # Check if the module spec is invalid
                raise ValueError(
                    f"Plugin '{plugin_name}' has an invalid module specification. "
                    "This may indicate a corrupted or malformed plugin file."
                )

            # Load the module
            module = importlib.util.module_from_spec(spec)  # Load the module
            spec.loader.exec_module(module)  # Execute the module to import the plugin
            if not hasattr(module, "Plugin"):  # Check if the plugin class exists
                raise AttributeError(
                    f"Plugin '{plugin_name}' does not define a 'Plugin' class. "
                    "Each plugin must export a class named 'Plugin' "
                    "that inherits from BasePlugin."
                )
            if not issubclass(  # Check if the plugin class is a subclass of BasePlugin
                module.Plugin, BasePlugin
            ):
                raise TypeError(
                    f"Plugin '{plugin_name}' does not inherit from BasePlugin. "
                    "The 'Plugin' class must be a subclass of api.BasePlugin."
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
                        f"Plugin '{plugin_name}' command '{method_name[4:]}' "
                        "conflicts with a built-in command."
                    )
                if method_name in self._command_owners:
                    raise ValueError(
                        f"Plugin '{plugin_name}' command '{method_name[4:]}' "
                        "conflicts with command from plugin "
                        f"'{self._command_owners[method_name]}'."
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

            # Log a message and return True
            self.logger.info(f"Loaded plugin '{plugin_name}'.")

        else:  # If the plugin file does not exist, raise an error
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

    def unload_plugin(self, plugin_name: str) -> None:
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

    def reload_plugin(self, plugin_name: str) -> None:
        """Reload a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be reloaded.

        """
        self.logger.info(f"Reloading plugin '{plugin_name}'.")
        self.unload_plugin(plugin_name)  # Unload the plugin
        self.load_plugin(plugin_name)  # Load the plugin again
        self.logger.info(f"Reloaded plugin '{plugin_name}'.")

    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be disabled.

        """
        self.logger.info(f"Disabling plugin '{plugin_name}'.")

        # Check if the plugin is already disabled
        if plugin_name in self.disabled_plugins:
            raise PluginDisabledError(f"Plugin '{plugin_name}' is already disabled.")

        if self.plugin_dir / f"{plugin_name}.py" not in self.plugin_dir.iterdir():
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

        # Add the plugin to the set of disabled plugins to disable it
        self.disabled_plugins.add(plugin_name)
        self.disabled_plugins.save()
        if (  # If the plugin is currently loaded, unload it
            plugin_name in self.plugin_instances
        ):
            self.unload_plugin(plugin_name)
        self.logger.info(f"Disabled plugin '{plugin_name}'.")

    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be enabled.

        """
        self.logger.info(f"Enabling plugin '{plugin_name}'.")

        # Check if the plugin is not disabled
        if plugin_name not in self.disabled_plugins:
            raise PluginNotDisabledError(
                f"Plugin '{plugin_name}' is not disabled; enable only applies "
                "to plugins in the disabled list."
            )

        # Remove the plugin from the set of disabled plugins to enable it
        self.disabled_plugins.remove(plugin_name)
        self.disabled_plugins.save()  # Save the updated set of disabled plugins

        # Check if the plugin file exists before loading
        if self.plugin_dir / f"{plugin_name}.py" not in self.plugin_dir.iterdir():
            raise PluginNotFoundError(
                f"Plugin '{plugin_name}' not found while loading. "
                "But it was removed from the disabled list. "
                "So it may have been deleted since the last time plugins were loaded."
            )

        # Load the plugin if the configuration specifies to load on enable
        if self.master.config["plugin"]["load_on_enable"]:
            self.load_plugin(plugin_name)

        self.logger.info(f"Enabled plugin '{plugin_name}'.")

    def load_all_plugins(self, console: Console | None = None) -> int:
        """Load all plugins in the plugin directory.

        Args:
            console (Console | None, optional): A Rich Console instance for
                printing warning messages. If None, no messages will be printed.
                Defaults to None.

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
                except Exception as e:  # If any other exception occurs, log an error
                    self.logger.error(f"Failed to load plugin '{plugin_name}': {e}")
                    console.print(
                        f"[red]Failed to load plugin '{plugin_name}': {e}[/red]"
                    ) if console else None
                else:  # If the plugin was loaded successfully, log an info
                    loaded_count += 1

        self.logger.info(f"Loaded {loaded_count} plugins.")
        return loaded_count

    def unload_all_plugins(self) -> int:
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

    def reload_all_plugins(self) -> int:
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
