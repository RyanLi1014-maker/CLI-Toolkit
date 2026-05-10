"""Unit tests for config.py."""

# Import libraries
import json
import logging

# Import pytest for testing
import pytest

# Import the config classes and functions to test
from src.util.config import DictConfig, ListConfig, SetConfig, _validate_nested_value


@pytest.fixture
def temp_config_dir(tmp_path):
    """Fixture to provide a temporary config directory."""
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    return config_dir


class TestValidateNestedValue:
    """Tests for the _validate_nested_value function."""

    def test_type_match(self, caplog):
        """Test when types match."""
        with caplog.at_level(logging.WARNING):
            result = _validate_nested_value(42, 0, "test.json", logging.getLogger())
        assert result == 42
        assert not caplog.records

    def test_type_mismatch(self, caplog):
        """Test when types don't match."""
        logger = logging.getLogger()
        with caplog.at_level(logging.WARNING):
            result = _validate_nested_value("string", 0, "test.json", logger)
        assert result == 0
        assert "has type str, but expected int" in caplog.text

    def test_dict_missing_key(self, caplog):
        """Test dict with missing key."""
        loaded = {"a": 1}
        default = {"a": 1, "b": 2}
        logger = logging.getLogger()
        with caplog.at_level(logging.WARNING):
            result = _validate_nested_value(loaded, default, "test.json", logger)
        assert result == default
        assert "missing key 'b'" in caplog.text

    def test_dict_nested(self, caplog):
        """Test nested dict validation."""
        loaded = {"a": {"x": 10}}
        default = {"a": {"x": 0, "y": 20}}
        logger = logging.getLogger()
        with caplog.at_level(logging.WARNING):
            result = _validate_nested_value(loaded, default, "test.json", logger)
        expected = {"a": {"x": 10, "y": 20}}
        assert result == expected
        assert "missing key 'y'" in caplog.text

    def test_list_validation(self, caplog):
        """Test list validation."""
        loaded = [1, "wrong"]
        default = [0, 0]
        logger = logging.getLogger()
        with caplog.at_level(logging.WARNING):
            result = _validate_nested_value(loaded, default, "test.json", logger)
        assert result == [1, 0]  # second item type mismatch, use default
        assert "has type str, but expected int" in caplog.text


class TestListConfig:
    """Tests for the ListConfig class."""

    def test_init_auto_load_false(self, temp_config_dir):
        """Test initialization without auto load."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        config = ListConfig(config_path, default, auto_load=False)
        assert list(config) == default
        assert not config_path.exists()

    def test_init_auto_load_true_no_file(self, temp_config_dir, caplog):
        """Test initialization with auto load but no file exists."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        with caplog.at_level(logging.WARNING):
            config = ListConfig(config_path, default, auto_load=True)
        assert list(config) == default
        assert config_path.exists()
        assert "does not exist" in caplog.text

    def test_load_valid_json(self, temp_config_dir):
        """Test loading valid JSON."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        loaded_data = [4, 5, 6]
        config_path.write_text(json.dumps(loaded_data))
        config = ListConfig(config_path, default, auto_load=True)
        assert list(config) == loaded_data

    def test_load_invalid_json(self, temp_config_dir, caplog):
        """Test loading invalid JSON."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        config_path.write_text("invalid json")
        with caplog.at_level(logging.WARNING):
            config = ListConfig(config_path, default, auto_load=True)
        assert list(config) == default
        assert "not a valid json file" in caplog.text

    def test_load_non_list(self, temp_config_dir, caplog):
        """Test loading non-list JSON."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        config_path.write_text(json.dumps({"key": "value"}))
        with caplog.at_level(logging.WARNING):
            config = ListConfig(config_path, default, auto_load=True)
        assert list(config) == default
        assert "does not contain a list" in caplog.text

    def test_save(self, temp_config_dir):
        """Test saving configuration."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        config = ListConfig(config_path, default, auto_load=False)
        config.save()
        assert config_path.exists()
        with config_path.open() as f:
            saved = json.load(f)
        assert saved == default

    def test_validate_structure_enabled(self, temp_config_dir, caplog):
        """Test validation with structure enabled."""
        config_path = temp_config_dir / "list_config.json"
        default = [1, 2, 3]
        loaded_data = [4, 5]  # shorter
        config_path.write_text(json.dumps(loaded_data))
        with caplog.at_level(logging.WARNING):
            config = ListConfig(config_path, default, validate_structure=True)
        assert list(config) == [4, 5, 3]  # extended with default
        assert "has 2 items, but default has 3" in caplog.text


class TestDictConfig:
    """Tests for the DictConfig class."""

    def test_init_auto_load_false(self, temp_config_dir):
        """Test initialization without auto load."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1, "b": 2}
        config = DictConfig(config_path, default, auto_load=False)
        assert dict(config) == default
        assert not config_path.exists()

    def test_load_valid_json(self, temp_config_dir):
        """Test loading valid JSON."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1, "b": 2}
        loaded_data = {"a": 10, "b": 20}
        config_path.write_text(json.dumps(loaded_data))
        config = DictConfig(config_path, default, auto_load=True)
        assert dict(config) == loaded_data

    def test_load_missing_key(self, temp_config_dir, caplog):
        """Test loading with missing key."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1, "b": 2}
        loaded_data = {"a": 10}
        config_path.write_text(json.dumps(loaded_data))
        with caplog.at_level(logging.WARNING):
            config = DictConfig(config_path, default, auto_load=True)
        assert dict(config) == {"a": 10, "b": 2}
        assert "missing key 'b'" in caplog.text

    def test_load_extra_key_no_validation(self, temp_config_dir):
        """Test loading with extra key when validation disabled."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1}
        loaded_data = {"a": 10, "b": 20}
        config_path.write_text(json.dumps(loaded_data))
        config = DictConfig(config_path, default, validate_structure=False)
        assert dict(config) == loaded_data

    def test_validate_structure_enabled(self, temp_config_dir, caplog):
        """Test validation with structure enabled."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1, "b": 2}
        loaded_data = {"a": 10, "c": 30}
        config_path.write_text(json.dumps(loaded_data))
        with caplog.at_level(logging.WARNING):
            config = DictConfig(config_path, default, validate_structure=True)
        assert dict(config) == {"a": 10, "b": 2}
        assert "has keys" in caplog.text and "but default has keys" in caplog.text

    def test_save(self, temp_config_dir):
        """Test saving configuration."""
        config_path = temp_config_dir / "dict_config.json"
        default = {"a": 1, "b": 2}
        config = DictConfig(config_path, default, auto_load=False)
        config.save()
        assert config_path.exists()
        with config_path.open() as f:
            saved = json.load(f)
        assert saved == default


class TestSetConfig:
    """Tests for the SetConfig class."""

    def test_init_auto_load_false(self, temp_config_dir):
        """Test initialization without auto load."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        config = SetConfig(config_path, default, auto_load=False)
        assert set(config) == default
        assert not config_path.exists()

    def test_load_valid_json(self, temp_config_dir):
        """Test loading valid JSON."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        loaded_data = [4, 5, 6]
        config_path.write_text(json.dumps(loaded_data))
        config = SetConfig(config_path, default, auto_load=True)
        assert set(config) == {1, 2, 3, 4, 5, 6}

    def test_load_invalid_json(self, temp_config_dir, caplog):
        """Test loading invalid JSON."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        config_path.write_text("invalid json")
        with caplog.at_level(logging.WARNING):
            config = SetConfig(config_path, default, auto_load=True)
        assert set(config) == default
        assert "not a valid json file" in caplog.text

    def test_load_non_list(self, temp_config_dir, caplog):
        """Test loading non-list JSON."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        config_path.write_text(json.dumps({"key": "value"}))
        with caplog.at_level(logging.WARNING):
            config = SetConfig(config_path, default, auto_load=True)
        assert set(config) == default
        assert "does not contain a list" in caplog.text

    def test_save(self, temp_config_dir):
        """Test saving configuration."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        config = SetConfig(config_path, default, auto_load=False)
        config.save()
        assert config_path.exists()
        with config_path.open() as f:
            saved = json.load(f)
        assert set(saved) == default

    def test_validate_structure_enabled(self, temp_config_dir):
        """Test validation with structure enabled."""
        config_path = temp_config_dir / "set_config.json"
        default = {1, 2, 3}
        loaded_data = [1, 4]  # 4 not in default
        config_path.write_text(json.dumps(loaded_data))
        config = SetConfig(config_path, default, validate_structure=True)
        assert set(config) == {1, 2, 3}  # only matched and defaults
