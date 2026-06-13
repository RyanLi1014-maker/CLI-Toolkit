"""Unit tests for app.py."""

# Import libraries
import contextlib
import json
import time
import tomllib
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock

import pytest

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
        assert hasattr(app, "cmd_echo") and callable(app.cmd_echo)
        assert hasattr(app, "cmd_exit") and callable(app.cmd_exit)
        assert hasattr(app, "cmd_help") and callable(app.cmd_help)
        assert hasattr(app, "cmd_plugin") and callable(app.cmd_plugin)
        assert hasattr(app, "cmd_run") and callable(app.cmd_run)
        assert hasattr(app, "cmd_version") and callable(app.cmd_version)

    def test_dispatch_magic_variable(self):
        """Test that ${cwd} and other magic variables are resolved in _dispatch."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Test ${cwd} resolves to the current working directory
        app._dispatch("echo ${cwd}")
        assert printed == [str(Path.cwd().resolve())]

        # Test unknown ${...} passes through as the variable name
        printed.clear()
        app._dispatch("echo ${unknown}")
        assert printed == ["unknown"]

        # Test regular arguments are unchanged
        printed.clear()
        app._dispatch("echo hello world")
        assert printed == ["hello\nworld"]

        # Test mixed regular and magic variable arguments
        printed.clear()
        app._dispatch("echo prefix ${cwd} suffix")
        assert printed == [f"prefix\n{Path.cwd().resolve()}\nsuffix"]

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

        # Test invalid argument counts for sub-commands
        app.cmd_alias(["create"])  # Missing required arguments
        app.cmd_alias(["create", "only_one"])
        app.cmd_alias(["create", "a", "b", "extra"])
        app.cmd_alias(["delete"])  # Missing required argument
        app.cmd_alias(["delete", "a", "extra"])

        # Restore original aliases after testing
        app.aliases.clear()
        app.aliases.update(current_aliases)
        app.aliases.save()  # Save the restored aliases to file

    def test_cmd_clear(self):
        """Test the cmd_clear command."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Test that the cmd_clear method can be called without error
        app.cmd_clear([])
        assert not printed

        # Test that extra arguments are rejected
        app.cmd_clear(["extra"])
        assert any("Invalid clear command usage" in message for message in printed)

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

        # Test setting a value of the wrong type (should not change config)
        app.cmd_config(["set", "plugin", "load_on_start", "not_a_boolean"])
        assert app.config["plugin"]["load_on_start"] == before

        # Test unknown sub-command
        app.cmd_config(["unknown"])  # Should print error without raising

        # Test invalid argument counts for sub-commands
        app.cmd_config(["set"])  # Missing required arguments
        app.cmd_config(["set", "plugin", "load_on_start"])  # Too few arguments
        app.cmd_config(["set", "plugin", "load_on_start", "true", "extra"])
        app.cmd_config(["reset", "plugin"])  # Too few arguments
        app.cmd_config(["reset_all", "extra"])
        app.cmd_config(["reload", "extra"])

        # Restore original config after testing
        app.config.clear()
        app.config.update(original_config)
        app.config.save()

    def test_cmd_echo(self):
        """Test the cmd_echo command."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Test echoing no arguments
        app.cmd_echo([])
        assert printed == [""]

        # Test echoing a single argument
        printed.clear()
        app.cmd_echo(["hello"])
        assert printed == ["hello"]

        # Test echoing multiple arguments
        printed.clear()
        app.cmd_echo(["hello", "world"])
        assert printed == ["hello\nworld"]

    def test_cmd_exit(self):
        """Test the cmd_exit command."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Test that the cmd_exit method can be called without error
        with contextlib.suppress(SystemExit):
            app.cmd_exit([])

        # Test that extra arguments are rejected
        app.cmd_exit(["extra"])
        assert any("Invalid exit command usage" in message for message in printed)

    def test_cmd_help(self):
        """Test the cmd_help command."""
        app = CLIToolkitApp()

        # Test showing help for a specific command
        app.cmd_help(["alias"])  # Should print detailed help message without error

        # Test listing all commands
        app.cmd_help([])  # Should print the list of commands without error

        # Test that multiple arguments are rejected
        app.cmd_help(["alias", "extra"])

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

        # Test invalid argument counts for sub-commands
        app.cmd_plugin(["load"])
        app.cmd_plugin(["load", "test_plugin", "extra"])
        app.cmd_plugin(["load_all", "extra"])
        app.cmd_plugin(["reload_all", "extra"])

    def test_cmd_version(self):
        """Test the cmd_version command."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(" ".join(str(arg) for arg in args))

        app.console.print = capture_print

        # Test that the cmd_version method can be called without error
        app.cmd_version([])

        printed.clear()
        app.cmd_version(["extra"])
        assert any("Invalid version command usage" in message for message in printed)

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

    def test_mainloop_single_ctrl_c(self, monkeypatch):
        """Test single Ctrl+C at prompt shows warning without exiting."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print
        app._last_ctrl_c_time = 0.0

        call_count = 0

        def mock_input(_=""):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise KeyboardInterrupt()
            raise EOFError()

        monkeypatch.setattr("builtins.input", mock_input)

        with contextlib.suppress(SystemExit):
            app.mainloop()

        # First press should show the "press again" warning, not exit
        assert any("Press Ctrl+C again" in msg for msg in printed)
        # _last_ctrl_c_time should be updated (no longer 0.0)
        assert app._last_ctrl_c_time > 0.0

    def test_mainloop_double_ctrl_c(self, monkeypatch):
        """Test double Ctrl+C within 2 seconds exits the application."""
        app = CLIToolkitApp()

        call_count = 0

        def mock_input(_=""):
            nonlocal call_count
            call_count += 1
            raise KeyboardInterrupt()

        monkeypatch.setattr("builtins.input", mock_input)
        # Set the last press time so the second interrupt will be within 2s
        app._last_ctrl_c_time = time.time()

        with pytest.raises(SystemExit):
            app.mainloop()

    def test_dispatch_interrupts_command(self):
        """Test KeyboardInterrupt during command execution is caught by _dispatch."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Register a command that raises KeyboardInterrupt
        def _cmd_raises_interrupt(_args):
            raise KeyboardInterrupt()

        app.cmd_raises_interrupt = _cmd_raises_interrupt  # pyright: ignore[reportAttributeAccessIssue]

        # Should not propagate KeyboardInterrupt
        app._dispatch("raises_interrupt")

        # Should print the interruption message
        assert any("Command interrupted" in msg for msg in printed)

    def test_dispatch_interrupts_alias_command(self):
        """Test KeyboardInterrupt during alias command execution is caught."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Register a command that raises KeyboardInterrupt
        def _cmd_raises_interrupt(_args):
            raise KeyboardInterrupt()

        app.cmd_raises_interrupt = _cmd_raises_interrupt  # pyright: ignore[reportAttributeAccessIssue]

        # Create an alias for the interrupt-raising command
        app.aliases["ri"] = "raises_interrupt"

        # Should not propagate KeyboardInterrupt
        app._dispatch("ri")

        # Should print the interruption message
        assert any("Command interrupted" in msg for msg in printed)

    def test_cmd_run(self, monkeypatch):
        """Test the cmd_run command."""
        import subprocess

        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        # Test successful command execution
        mock_run = MagicMock()
        monkeypatch.setattr(subprocess, "run", mock_run)
        app.cmd_run(["echo", "hello"])
        mock_run.assert_called_once_with(["echo", "hello"], shell=True, text=True)
        assert not printed  # No error output on success

        # Test failed command execution
        mock_run.reset_mock()
        mock_run.side_effect = OSError("command not found")
        app.cmd_run(["nonexistent_command"])
        mock_run.assert_called_once_with(["nonexistent_command"], shell=True, text=True)
        assert any("failed" in msg for msg in printed)

    def test_dispatch_no_interrupt_on_normal_command(self):
        """Test normal command execution is unaffected by Ctrl+C handling."""
        app = CLIToolkitApp()
        printed: list[str] = []

        def capture_print(*args, **_kwargs):
            printed.append(str(args[0]) if args else "")

        app.console.print = capture_print

        app._dispatch("echo hello world")
        assert printed == ["hello\nworld"]
