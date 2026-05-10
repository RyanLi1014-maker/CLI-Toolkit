"""Unit tests for app.py."""

# Import libraries
import contextlib
import json
import tomllib
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

# Import the app class to test
from src.app import CLIToolkitApp
from src.exception import PluginDisabledError


class TestCLIToolkitApp:
    """Unit tests for CLIToolkitApp class."""

    def test_app_initialization(self):
        """Test that the app initializes correctly."""
        app = CLIToolkitApp()

        # Check that the app has the expected attributes
        assert hasattr(app, "VERSION")  # Check that the app has a VERSION attribute
        assert hasattr(app, "console")
        assert hasattr(app, "logger")
        assert hasattr(app, "config")
        assert hasattr(app, "plugin_manager")
        assert hasattr(app, "aliases")
        # Check that the VERSION attribute matches the version in pyproject.toml
        with Path("pyproject.toml").open("rb") as f:
            pyproject_data = tomllib.load(f)
        expected_version = tuple(
            int(num) for num in pyproject_data["project"]["version"].split(".")
        )
        assert expected_version == app.VERSION

        # Check that the config is loaded correctly from file
        with Path("config/CLI-Toolkit/config.json").open("r") as f:
            config_data = json.load(f)
        assert app.config == config_data

    def test_built_in_commands(self):
        """Test that the app has the expected built-in commands."""
        app = CLIToolkitApp()

        # Check that the app has the expected built-in commands
        assert hasattr(app, "cmd_alias") and callable(app.cmd_alias)
        assert hasattr(app, "cmd_clear") and callable(app.cmd_clear)
        assert hasattr(app, "cmd_config") and callable(app.cmd_config)
        assert hasattr(app, "cmd_exit") and callable(app.cmd_exit)
        assert hasattr(app, "cmd_help") and callable(app.cmd_help)
        assert hasattr(app, "cmd_plugin") and callable(app.cmd_plugin)
        assert hasattr(app, "cmd_version") and callable(app.cmd_version)

    def test_cmd_alias(self):
        """Test the cmd_alias command."""
        app = CLIToolkitApp()
        current_aliases = app.aliases.copy()  # Save current aliases to restore later
        app.aliases.clear()  # Clear any existing aliases for testing
        app.aliases.save()  # Save the restored aliases to file

        # Test creating a new alias
        app.cmd_alias(["create", "a", "b"])
        # Check that the alias was created correctly
        assert "a" in app.aliases and app.aliases["a"] == "b"

        # Test creating an alias for an alias
        app.cmd_alias(["create", "c", "a"])
        # Should not allow aliasing an alias
        assert "c" not in app.aliases

        # Test creating an alias using a command that already exists as an alias name
        app.cmd_alias(["create", "b", "c"])
        # Should not allow aliasing to an existing alias name
        assert "c" not in app.aliases

        # Test deleting an alias
        app.cmd_alias(["delete", "a"])
        # Check that the alias was deleted correctly
        assert "a" not in app.aliases

        # Test the simplified sub-command
        app.cmd_alias(["c", "d", "e"])
        assert "d" in app.aliases and app.aliases["d"] == "e"

        # Test the simplified sub-command for deletion
        app.cmd_alias(["d", "d"])
        assert "d" not in app.aliases

        # Test listing aliases
        app.cmd_alias([])  # Should print the list of aliases without error

        # Restore original aliases after testing
        app.aliases.clear()
        app.aliases.update(current_aliases)
        app.aliases.save()  # Save the restored aliases to file

    def test_cmd_clear(self):
        """Test the cmd_clear command."""
        app = CLIToolkitApp()

        # Test that the cmd_clear method can be called without error
        app.cmd_clear([])

    def test_cmd_config(self, monkeypatch):
        """Test the cmd_config command."""
        app = CLIToolkitApp()
        original_config = deepcopy(app.config)

        def set_confirm(confirmed: bool) -> None:
            mock_confirm = MagicMock()
            mock_confirm.return_value.ask.return_value = confirmed
            monkeypatch.setattr("src.app.Confirm", mock_confirm)

        # Test listing all configuration values
        app.cmd_config([])  # Should print config without error

        # Test setting a configuration value
        app.cmd_config(["set", "plugin", "load_on_start", "false"])
        assert app.config["plugin"]["load_on_start"] is False

        # Test the simplified set sub-command
        app.cmd_config(["s", "plugin", "load_on_enable", "false"])
        assert app.config["plugin"]["load_on_enable"] is False

        # Test reset a configuration value (restores default when confirmed)
        set_confirm(True)
        app.cmd_config(["reset", "plugin", "load_on_start"])
        assert (
            app.config["plugin"]["load_on_start"]
            == app.config.default["plugin"]["load_on_start"]
        )

        # Test the simplified reset sub-command
        app.config["plugin"]["load_on_enable"] = False
        set_confirm(True)
        app.cmd_config(["rs", "plugin", "load_on_enable"])
        assert (
            app.config["plugin"]["load_on_enable"]
            == app.config.default["plugin"]["load_on_enable"]
        )

        # Test reset aborted when user declines confirmation
        app.config["plugin"]["load_on_start"] = False
        set_confirm(False)
        app.cmd_config(["reset", "plugin", "load_on_start"])
        assert app.config["plugin"]["load_on_start"] is False

        # Test reset_all
        app.config["plugin"]["load_on_start"] = not app.config.default["plugin"][
            "load_on_start"
        ]
        app.config.save()
        set_confirm(True)
        app.cmd_config(["reset_all"])
        assert (
            app.config["plugin"]["load_on_start"]
            == app.config.default["plugin"]["load_on_start"]
        )

        # Test the simplified reset_all sub-command
        app.config["plugin"]["load_on_enable"] = not app.config.default["plugin"][
            "load_on_enable"
        ]
        app.config.save()
        set_confirm(True)
        app.cmd_config(["rsa"])
        assert (
            app.config["plugin"]["load_on_enable"]
            == app.config.default["plugin"]["load_on_enable"]
        )

        # Test reset_all aborted when user declines confirmation
        app.config["plugin"]["load_on_start"] = True
        app.config.save()
        set_confirm(False)
        app.cmd_config(["reset_all"])
        assert app.config["plugin"]["load_on_start"] is True

        # Test reload from file
        app.config["plugin"]["load_on_start"] = False
        app.config.save()
        app.config["plugin"]["load_on_start"] = True  # Change in memory only
        app.cmd_config(["reload"])
        assert app.config["plugin"]["load_on_start"] is False

        # Test the simplified reload sub-command
        app.config["plugin"]["load_on_start"] = True
        app.config.save()
        app.config["plugin"]["load_on_start"] = False  # Change in memory only
        app.cmd_config(["rl"])
        assert app.config["plugin"]["load_on_start"] is True

        # Test invalid category/key (should not change config)
        before = app.config["plugin"]["load_on_start"]
        app.cmd_config(["set", "nonexistent", "key", "value"])
        app.cmd_config(["set", "plugin", "nonexistent", "value"])
        assert app.config["plugin"]["load_on_start"] == before

        # Test unknown sub-command
        app.cmd_config(["unknown"])  # Should print error without raising

        # Restore original config after testing
        app.config.clear()
        app.config.update(original_config)
        app.config.save()

    def test_cmd_exit(self):
        """Test the cmd_exit command."""
        app = CLIToolkitApp()

        # Test that the cmd_exit method can be called without error
        with contextlib.suppress(SystemExit):
            app.cmd_exit([])

    def test_cmd_help(self):
        """Test the cmd_help command."""
        app = CLIToolkitApp()

        # Test showing help for a specific command
        app.cmd_help(["alias"])  # Should print detailed help message without error

        # Test listing all commands
        app.cmd_help([])  # Should print the list of commands without error

    def test_cmd_plugin(self, tmp_path):
        """Test the cmd_plugin command."""
        app = CLIToolkitApp()
        # Unload all plugins to ensure a clean state for testing
        app.plugin_manager.unload_all_plugins()
        # Set plugin directory to a temporary path for testing
        app.plugin_manager.plugin_dir = tmp_path
        (tmp_path / "test_plugin.py").write_text(
            """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_test_command(self, _):
        pass
"""
        )

        # Test loading/unloading/reloading a specific plugin
        app.cmd_plugin(["load", "test_plugin"])
        app.cmd_plugin(["reload", "test_plugin"])
        app.cmd_plugin(["unload", "test_plugin"])
        # Test the simplified sub-commands
        app.cmd_plugin(["l", "test_plugin"])
        app.cmd_plugin(["r", "test_plugin"])
        app.cmd_plugin(["u", "test_plugin"])

        # Set config before disable/enable testing
        original_config = deepcopy(app.config)
        app.config["plugin"]["load_on_enable"] = True
        app.config.save()

        # Test disabling a specific plugin
        app.cmd_plugin(["disable", "test_plugin"])
        assert "test_plugin" in app.plugin_manager.disabled_plugins
        assert "test_plugin" not in app.plugin_manager.plugin_instances
        with contextlib.suppress(PluginDisabledError):
            app.plugin_manager.load_plugin("test_plugin")  # Should raise error
        assert "test_plugin" not in app.plugin_manager.plugin_instances

        # Test enabling a specific plugin
        app.cmd_plugin(["enable", "test_plugin"])
        assert "test_plugin" not in app.plugin_manager.disabled_plugins
        # Should load successfully if load_on_enable is True
        assert "test_plugin" in app.plugin_manager.plugin_instances

        # Test the simplified sub-commands for disabling
        app.cmd_plugin(["dis", "test_plugin"])
        assert "test_plugin" in app.plugin_manager.disabled_plugins
        assert "test_plugin" not in app.plugin_manager.plugin_instances
        with contextlib.suppress(PluginDisabledError):
            app.plugin_manager.load_plugin("test_plugin")  # Should raise error
        assert "test_plugin" not in app.plugin_manager.plugin_instances

        # Test the simplified sub-commands for enabling
        app.cmd_plugin(["en", "test_plugin"])
        assert "test_plugin" not in app.plugin_manager.disabled_plugins
        assert "test_plugin" in app.plugin_manager.plugin_instances

        # Restore config after disable/enable testing
        app.config.clear()
        app.config.update(original_config)
        app.config.save()

        # Test showing help for a specific plugin command
        app.cmd_plugin(["help", "alias"])  # Should print help message without error
        app.cmd_plugin(["h", "alias"])  # Should print help message without error
        app.cmd_plugin(["help", "nonexistent"])  # Should print error message

        # Test listing all plugins
        app.cmd_plugin([])  # Should print plugins list without error

    def test_cmd_version(self):
        """Test the cmd_version command."""
        app = CLIToolkitApp()

        # Test that the cmd_version method can be called without error
        app.cmd_version([])  # Should print the version information without error

    def test_mainloop(self, monkeypatch):
        """Test mainloop dispatches commands."""
        app = CLIToolkitApp()
        dispatched: list[str] = []
        monkeypatch.setattr(app, "_dispatch", lambda cmd: dispatched.append(cmd))

        mock_input_calls = 0

        def mock_input(_=""):
            nonlocal mock_input_calls
            mock_input_calls += 1
            if mock_input_calls == 1:
                return "help"
            raise EOFError()

        monkeypatch.setattr("builtins.input", mock_input)

        with contextlib.suppress(SystemExit):
            app.mainloop()

        assert dispatched == ["help"]

    def test_mainloop_keyboard_interrupt(self, monkeypatch):
        """Test mainloop exits gracefully on Ctrl+C."""
        app = CLIToolkitApp()
        dispatched: list[str] = []
        monkeypatch.setattr(app, "_dispatch", lambda cmd: dispatched.append(cmd))

        def mock_input(_=""):
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", mock_input)

        with contextlib.suppress(SystemExit):
            app.mainloop()

        assert dispatched == []
