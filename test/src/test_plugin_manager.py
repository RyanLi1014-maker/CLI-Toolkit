"""Unit tests for plugin_manager.py."""

import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from src.exception import (
    PluginDisabledError,
    PluginLoadedError,
    PluginNotDisabledError,
    PluginNotFoundError,
)
from src.plugin_manager import PluginManager


@pytest.fixture
def mock_master():
    """Fixture to create a mock master application."""
    master = MagicMock()
    master.VERSION = (1, 0, 0)
    master.console = MagicMock()
    master.config = {"plugin": {"load_on_enable": True}}
    # Add some core commands
    master.cmd_help = MagicMock()
    master.cmd_exit = MagicMock()
    return master


@pytest.fixture
def temp_plugin_dir(tmp_path):
    """Fixture to provide a temporary plugin directory."""
    plugin_dir = tmp_path / "plugin"
    plugin_dir.mkdir()
    return plugin_dir


@pytest.fixture
def temp_config_dir(tmp_path):
    """Fixture to provide a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


def create_fake_plugin(plugin_dir: Path, name: str, plugin_code: str):
    """Create a fake plugin file."""
    plugin_file = plugin_dir / f"{name}.py"
    plugin_file.write_text(plugin_code)


class TestPluginManager:
    """Unit tests for the PluginManager class."""

    def test_init(self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch):
        """Test initialization of PluginManager."""
        # Mock the config path
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)
        assert pm.master == mock_master
        assert pm.plugin_dir == temp_plugin_dir
        assert pm.disabled_plugins == set()
        assert pm.plugin_instances == {}
        assert pm._core_commands == {"cmd_help", "cmd_exit"}
        assert pm._plugin_commands == {}
        assert pm._command_owners == {}

    def test_load_plugin_valid(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test loading a valid plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_test_command(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)

        with caplog.at_level(logging.INFO):
            pm.load_plugin("test_plugin")
        assert "test_plugin" in pm.plugin_instances
        assert "cmd_test_command" in pm._command_owners
        assert pm._command_owners["cmd_test_command"] == "test_plugin"
        assert "Loaded plugin 'test_plugin'" in caplog.text

    def test_load_plugin_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading a disabled plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)
        pm.disabled_plugins.add("test_plugin")

        with pytest.raises(PluginDisabledError):
            pm.load_plugin("test_plugin")

    def test_load_plugin_loaded_ok_true(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test that load_plugin does not raise when loaded_ok is True."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)
        pm.load_plugin("test_plugin")

        with caplog.at_level(logging.WARNING):
            pm.load_plugin("test_plugin", loaded_ok=True)

        assert "is already loaded" in caplog.text

    def test_load_plugin_loaded_ok_false(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test that load_plugin raises when loaded_ok is False.

        It will raise PluginLoadedError and log warning if the plugin is already loaded.
        """
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)
        pm.load_plugin("test_plugin")

        with pytest.raises(PluginLoadedError), caplog.at_level(logging.WARNING):
            pm.load_plugin("test_plugin", loaded_ok=False)

    def test_load_plugin_invalid_name(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading with invalid plugin name."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        with pytest.raises(ValueError, match="Invalid plugin name"):
            pm.load_plugin("../test")

    def test_load_plugin_not_found(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading a non-existent plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        with pytest.raises(PluginNotFoundError):
            pm.load_plugin("nonexistent")

    def test_load_plugin_no_plugin_class(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading plugin without Plugin class."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
# No Plugin class
"""
        create_fake_plugin(temp_plugin_dir, "bad_plugin", plugin_code)

        with pytest.raises(AttributeError, match="does not define a 'Plugin' class"):
            pm.load_plugin("bad_plugin")

    def test_load_plugin_not_subclass(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading plugin not inheriting from BasePlugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
class Plugin:
    pass
"""
        create_fake_plugin(temp_plugin_dir, "bad_plugin", plugin_code)

        with pytest.raises(TypeError, match="does not inherit from BasePlugin"):
            pm.load_plugin("bad_plugin")

    def test_load_plugin_command_conflict_core(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading plugin with command conflicting with core."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_help(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "conflict_plugin", plugin_code)

        with pytest.raises(ValueError, match="conflicts with a built-in command"):
            pm.load_plugin("conflict_plugin")

    def test_load_plugin_command_conflict_plugin(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test loading plugin with command conflicting with another plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Load first plugin
        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_unique(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        pm.load_plugin("plugin1")

        # Load second plugin with conflicting command
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_unique(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)

        with pytest.raises(ValueError, match="conflicts with command from plugin"):
            pm.load_plugin("plugin2")

    def test_unload_plugin_loaded(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test unloading a loaded plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_test(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)
        pm.load_plugin("test_plugin")

        with caplog.at_level(logging.INFO):
            pm.unload_plugin("test_plugin")

        assert "test_plugin" not in pm.plugin_instances
        assert "cmd_test" not in pm._command_owners
        assert "Unloaded plugin 'test_plugin'" in caplog.text

    def test_unload_plugin_not_loaded(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test unloading a not loaded plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        with pytest.raises(PluginNotFoundError):
            pm.unload_plugin("not_loaded")

    def test_reload_plugin(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test reloading a plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_test(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)
        pm.load_plugin("test_plugin")

        with caplog.at_level(logging.INFO):
            pm.reload_plugin("test_plugin")

        assert "test_plugin" in pm.plugin_instances
        assert "Reloaded plugin 'test_plugin'" in caplog.text

    def test_disable_plugin_not_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test disabling a not disabled plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_test_command(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)

        with caplog.at_level(logging.INFO):
            pm.disable_plugin("test_plugin")

        assert "test_plugin" in pm.disabled_plugins
        assert "Disabled plugin 'test_plugin'" in caplog.text

    def test_disable_plugin_already_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test disabling an already disabled plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)
        pm.disabled_plugins.add("test_plugin")

        with pytest.raises(PluginDisabledError):
            pm.disable_plugin("test_plugin")

    def test_disable_plugin_not_found(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test disabling a non-existent plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        with pytest.raises(PluginNotFoundError):
            pm.disable_plugin("nonexistent")

    def test_enable_plugin_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test enabling a disabled plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)
        pm.disabled_plugins.add("test_plugin")

        plugin_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    pass
"""
        create_fake_plugin(temp_plugin_dir, "test_plugin", plugin_code)

        with caplog.at_level(logging.INFO):
            pm.enable_plugin("test_plugin")

        assert "test_plugin" not in pm.disabled_plugins
        assert "test_plugin" in pm.plugin_instances
        assert "Enabled plugin 'test_plugin'" in caplog.text

    def test_enable_plugin_not_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch
    ):
        """Test enabling a not disabled plugin."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        with pytest.raises(PluginNotDisabledError):
            pm.enable_plugin("test_plugin")

    def test_load_all_plugins(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test loading all plugins."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Create multiple plugins
        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd2(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)

        with caplog.at_level(logging.INFO):
            count = pm.load_all_plugins()

        assert count == 2
        assert "plugin1" in pm.plugin_instances
        assert "plugin2" in pm.plugin_instances
        assert "Loaded 2 plugins" in caplog.text

    def test_load_all_plugins_disabled(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test loading all plugins skips disabled plugins."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd2(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)

        # Disable plugin2 before loading all
        pm.disabled_plugins.add("plugin2")

        with caplog.at_level(logging.INFO):
            count = pm.load_all_plugins()

        assert count == 1
        assert "plugin1" in pm.plugin_instances
        assert "plugin2" not in pm.plugin_instances
        assert "Plugin 'plugin2' is disabled. Skipping..." in caplog.text
        assert "Loaded 1 plugins" in caplog.text

    def test_load_all_plugins_loaded(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test loading all plugins skips already loaded plugins and loads the rest."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd2(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)

        # Load plugin1 first
        pm.load_plugin("plugin1")

        with caplog.at_level(logging.INFO):
            count = pm.load_all_plugins()

        assert count == 1
        assert "plugin1" in pm.plugin_instances
        assert "plugin2" in pm.plugin_instances
        assert "Plugin 'plugin1' is already loaded. Skipping..." in caplog.text
        assert "Loaded 1 plugins" in caplog.text

    def test_load_all_plugins_invalid(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test that invalid plugins are reported and skipped when loading all."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Create a bad plugin that will raise when loaded (no Plugin class)
        bad_code = """
# invalid plugin file
"""
        create_fake_plugin(temp_plugin_dir, "bad_plugin", bad_code)

        with caplog.at_level(logging.ERROR):
            count = pm.load_all_plugins()

        assert count == 0
        assert "bad_plugin" not in pm.plugin_instances
        assert "Failed to load plugin 'bad_plugin'" in caplog.text

    def test_load_all_plugins_with_console(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test that `load_all_plugins` prints errors to the provided console."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Create a valid plugin and an invalid plugin
        good_code = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        bad_code = """
# invalid plugin file
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", good_code)
        create_fake_plugin(temp_plugin_dir, "bad_plugin", bad_code)

        console = MagicMock()

        with caplog.at_level(logging.ERROR):
            count = pm.load_all_plugins(console)

        assert count == 1
        assert "plugin1" in pm.plugin_instances
        assert "bad_plugin" not in pm.plugin_instances
        assert console.print.called
        assert "Failed to load plugin 'bad_plugin'" in caplog.text

    def test_unload_all_plugins(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test unloading all plugins."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Load some plugins first
        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd2(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)
        pm.load_all_plugins()

        with caplog.at_level(logging.INFO):
            count = pm.unload_all_plugins()

        assert count == 2
        assert len(pm.plugin_instances) == 0
        assert "Unloaded 2 plugins" in caplog.text

    def test_reload_all_plugins(
        self, mock_master, temp_plugin_dir, temp_config_dir, monkeypatch, caplog
    ):
        """Test reloading all plugins."""
        monkeypatch.chdir(temp_config_dir)
        pm = PluginManager(mock_master, temp_plugin_dir)

        # Load some plugins first
        plugin_code1 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd1(self, _):
        pass
"""
        plugin_code2 = """
from api import BasePlugin

class Plugin(BasePlugin):
    def cmd_cmd2(self, _):
        pass
"""
        create_fake_plugin(temp_plugin_dir, "plugin1", plugin_code1)
        create_fake_plugin(temp_plugin_dir, "plugin2", plugin_code2)
        pm.load_all_plugins()

        with caplog.at_level(logging.INFO):
            count = pm.reload_all_plugins()

        assert count == 2
        assert len(pm.plugin_instances) == 2
        assert "Reloaded 2 plugins" in caplog.text
