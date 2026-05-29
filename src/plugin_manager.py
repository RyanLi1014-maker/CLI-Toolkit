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

logger = getLogger("clit.plugin_manager")


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
        self.master = master
        self.plugin_instances: dict[str, BasePlugin] = {}

        # Collect core commands and set up tracking structures for plugin commands
        self._core_commands: set[str] = {
            method_name
            for method_name in dir(master)
            if method_name.startswith("cmd_")
            and callable(getattr(master, method_name, None))
        }
        self._plugin_commands: dict[str, set[str]] = {}
        self._command_owners: dict[str, str] = {}

        self.plugin_dir = PROJECT_ROOT / plugin_dir
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        # Initialize the set of disabled plugins
        self.disabled_plugins = SetConfig(Path("CLI-Toolkit/disabled_plugins.json"))

        # Remove plugins from the disabled list if their file no longer exists.
        # Iterate on a copy to avoid modifying the set during iteration.
        temp_disabled_plugins = self.disabled_plugins.copy()
        temp_plugin_dir_iter = self.plugin_dir.iterdir()
        for plugin_name in temp_disabled_plugins:
            (
                self.disabled_plugins.remove(plugin_name)
                if self.plugin_dir / f"{plugin_name}.py" not in temp_plugin_dir_iter
                else None
            )
        (
            self.disabled_plugins.save()
            if temp_disabled_plugins != self.disabled_plugins
            else None
        )
        del temp_disabled_plugins
        del temp_plugin_dir_iter

    def load_plugin(self, plugin_name: str, loaded_ok: bool = False):
        """Load a new plugin.

        Args:
            plugin_name (str): The name of a plugin to be loaded.
            loaded_ok (bool, optional): Whether it's okay for the plugin
                to already be loaded. Defaults to False.

        """
        logger.info("Loading plugin '%s'.", plugin_name)

        # Pre-load validation checks
        if plugin_name in self.disabled_plugins:
            raise PluginDisabledError(f"Plugin '{plugin_name}' is disabled.")
        if plugin_name in self.plugin_instances:
            logger.warning("Plugin '%s' is already loaded.", plugin_name)
            if not loaded_ok:
                raise PluginLoadedError(f"Plugin '{plugin_name}' is already loaded.")
        if ".." in plugin_name or "/" in plugin_name or "\\" in plugin_name:
            raise ValueError(f"Invalid plugin name: {plugin_name}")
        self.plugin_dir.mkdir(parents=True, exist_ok=True)

        plugin_path = self.plugin_dir / f"{plugin_name}.py"

        if plugin_path.exists():
            spec = importlib.util.spec_from_file_location(plugin_name, plugin_path)
            if not (spec and spec.loader):
                raise ValueError(
                    f"Plugin '{plugin_name}' has an invalid module specification. "
                    "This may indicate a corrupted or malformed plugin file."
                )

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if not hasattr(module, "Plugin"):
                raise AttributeError(
                    f"Plugin '{plugin_name}' does not define a 'Plugin' class. "
                    "Each plugin must export a class named 'Plugin' "
                    "that inherits from BasePlugin."
                )
            if not issubclass(module.Plugin, BasePlugin):
                raise TypeError(
                    f"Plugin '{plugin_name}' does not inherit from BasePlugin. "
                    "The 'Plugin' class must be a subclass of api.BasePlugin."
                )

            plugin_instance: BasePlugin = module.Plugin(self.master)
            logger.debug("Plugin instance: %s", plugin_instance)

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

            # Inject validated plugin commands into the main application
            registered_commands: set[str] = set()
            for method_name, method_attr in plugin_methods.items():
                setattr(self.master, method_name, method_attr)
                self._command_owners[method_name] = plugin_name
                registered_commands.add(method_name)
                logger.debug("Added command '%s' to CLI.", method_name[4:])
            self.plugin_instances[plugin_name] = plugin_instance
            self._plugin_commands[plugin_name] = registered_commands

            logger.info("Loaded plugin '%s'.", plugin_name)

        else:
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

    def unload_plugin(self, plugin_name: str) -> None:
        """Unload a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be unloaded.

        """
        logger.info("Unloading plugin '%s'.", plugin_name)

        if plugin_name in self.plugin_instances:
            plugin_instance = self.plugin_instances[plugin_name]
            logger.debug("Plugin instance: %s", plugin_instance)

            # Remove only commands previously registered by this plugin
            for method_name in self._plugin_commands.get(plugin_name, set()):
                if self._command_owners.get(method_name) != plugin_name:
                    continue
                if hasattr(self.master, method_name):
                    delattr(self.master, method_name)
                    logger.debug("Removed command '%s' from CLI.", method_name[4:])
                del self._command_owners[method_name]
            self._plugin_commands.pop(plugin_name, None)

            del self.plugin_instances[plugin_name]
            logger.info("Unloaded plugin '%s'.", plugin_name)

        else:
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

    def reload_plugin(self, plugin_name: str) -> None:
        """Reload a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be reloaded.

        """
        logger.info("Reloading plugin '%s'.", plugin_name)
        self.unload_plugin(plugin_name)
        self.load_plugin(plugin_name)
        logger.info("Reloaded plugin '%s'.", plugin_name)

    def disable_plugin(self, plugin_name: str) -> None:
        """Disable a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be disabled.

        """
        logger.info("Disabling plugin '%s'.", plugin_name)

        if plugin_name in self.disabled_plugins:
            raise PluginDisabledError(f"Plugin '{plugin_name}' is already disabled.")

        if self.plugin_dir / f"{plugin_name}.py" not in self.plugin_dir.iterdir():
            raise PluginNotFoundError(f"Plugin '{plugin_name}' not found.")

        self.disabled_plugins.add(plugin_name)
        self.disabled_plugins.save()
        if plugin_name in self.plugin_instances:
            self.unload_plugin(plugin_name)
        logger.info("Disabled plugin '%s'.", plugin_name)

    def enable_plugin(self, plugin_name: str) -> None:
        """Enable a plugin by its name.

        Args:
            plugin_name (str): The name of the plugin to be enabled.

        """
        logger.info("Enabling plugin '%s'.", plugin_name)

        if plugin_name not in self.disabled_plugins:
            raise PluginNotDisabledError(
                f"Plugin '{plugin_name}' is not disabled; enable only applies "
                "to plugins in the disabled list."
            )

        self.disabled_plugins.remove(plugin_name)
        self.disabled_plugins.save()

        if self.plugin_dir / f"{plugin_name}.py" not in self.plugin_dir.iterdir():
            raise PluginNotFoundError(
                f"Plugin '{plugin_name}' not found while loading. "
                "But it was removed from the disabled list. "
                "So it may have been deleted since the last time plugins were loaded."
            )

        if self.master.config["plugin"]["load_on_enable"]:
            self.load_plugin(plugin_name)

        logger.info("Enabled plugin '%s'.", plugin_name)

    def load_all_plugins(self, console: Console | None = None) -> int:
        """Load all plugins in the plugin directory.

        Args:
            console (Console | None, optional): A Rich Console instance for
                printing warning messages. If None, no messages will be printed.
                Defaults to None.

        Returns:
            int: The number of plugins loaded.

        """
        logger.info("Loading all plugins.")

        loaded_count = 0

        for file in self.plugin_dir.iterdir():
            if file.is_file() and file.suffix == ".py":
                plugin_name = file.stem

                # Skip disabled or already loaded plugins
                if plugin_name in self.disabled_plugins:
                    logger.info("Plugin '%s' is disabled. Skipping...", plugin_name)
                    continue
                if plugin_name in self.plugin_instances:
                    logger.info(
                        "Plugin '%s' is already loaded. Skipping...", plugin_name
                    )
                    continue

                try:
                    self.load_plugin(plugin_name)
                except Exception as e:
                    logger.error("Failed to load plugin '%s': %s", plugin_name, e)
                    console.print(
                        "[bold red]Failed to load plugin "
                        f"'{plugin_name}': {e}[/bold red]"
                    ) if console else None
                else:
                    loaded_count += 1

        logger.info("Loaded %d plugins.", loaded_count)
        return loaded_count

    def unload_all_plugins(self) -> int:
        """Unload all plugins.

        Returns:
            int: The number of plugins unloaded.

        """
        logger.info("Unloading all plugins.")

        unloaded_count = 0

        for plugin_name in list(self.plugin_instances.keys()):
            self.unload_plugin(plugin_name)
            unloaded_count += 1

        logger.info("Unloaded %d plugins.", unloaded_count)
        return unloaded_count

    def reload_all_plugins(self) -> int:
        """Reload all plugins.

        Returns:
            int: The number of plugins reloaded.

        """
        logger.info("Reloading all plugins.")

        reloaded_count = 0

        for plugin_name in list(self.plugin_instances.keys()):
            self.reload_plugin(plugin_name)
            reloaded_count += 1

        logger.info("Reloaded %d plugins.", reloaded_count)
        return reloaded_count
