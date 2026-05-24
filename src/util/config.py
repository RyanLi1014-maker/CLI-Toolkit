"""Configuration utilities."""

import json  # json file handling
import logging  # Logging module
from pathlib import Path  # file path handling

from src.util.project_root import PROJECT_ROOT  # Get the project root directory

# Set up logging
logger = logging.getLogger("Config")

CONFIG_DIRECTORY = PROJECT_ROOT / "config"


def _validate_nested_value(
    loaded_val, default_val, config_file_name: str, logger_obj, path=""
):
    """Recursively validate nested values.

    This is a shared utility function to avoid code duplication across config classes.

    Args:
        loaded_val: The value from the loaded configuration.
        default_val: The corresponding default value.
        config_file_name: Name of the configuration file for logging.
        logger_obj: Logger instance to use for warnings.
        path: The current path in the configuration (for error messages).

    Returns:
        The validated value (either loaded or default if invalid).

    """
    # Check type match (exact type, not isinstance, to prevent
    # bool (subclass of int) from passing int validation)
    if type(loaded_val) is not type(default_val):
        logger_obj.warning(
            "File '%s' value at %s has type %s, but expected %s. Using default value.",
            config_file_name,
            path or "root",
            type(loaded_val).__name__,
            type(default_val).__name__,
        )
        return default_val

    # Recursively validate nested structures
    if isinstance(loaded_val, dict) and isinstance(default_val, dict):
        # Validate dictionary keys and values
        result = {}
        for key in default_val:
            if key not in loaded_val:
                logger_obj.warning(
                    "File '%s' missing key '%s' at %s. Using default value.",
                    config_file_name,
                    key,
                    path or "root",
                )
                result[key] = default_val[key]
            else:
                child_path = f"{path}.{key}" if path else key
                result[key] = _validate_nested_value(
                    loaded_val[key],
                    default_val[key],
                    config_file_name,
                    logger_obj,
                    child_path,
                )
        return result

    elif isinstance(loaded_val, list) and isinstance(default_val, list):
        # Validate list items
        result = []
        min_len = min(len(loaded_val), len(default_val))
        for i in range(min_len):
            child_path = f"{path}[{i}]" if path else f"[{i}]"
            result.append(
                _validate_nested_value(
                    loaded_val[i],
                    default_val[i],
                    config_file_name,
                    logger_obj,
                    child_path,
                )
            )
        return result

    return loaded_val


class ListConfig(list):
    """Configuration class for handling application configuration."""

    def __init__(
        self,
        config_path: Path,
        default_config: list | None = None,
        auto_load: bool = True,
        validate_structure: bool = False,
    ) -> None:
        """Initialize the configuration.

        Args:
            config_path (Path): The path to the configuration file.
            default_config (list): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration
                from the file upon initialization.
                If False, the default configuration will be used while initializing.
                Defaults to True.
            validate_structure (bool): Whether to validate that the loaded
                configuration matches the structure, number of items, and value
                types in the default configuration. If False, any valid list
                will be accepted. Defaults to False.

        """
        # Initialize the list and set up logging
        super().__init__()
        self.logger = logger.getChild(
            self.__class__.__name__ + "('" + str(config_path) + "')"
        )

        # Set the configuration file path
        self.config_file_path = CONFIG_DIRECTORY / config_path
        self.config_file_path.parent.mkdir(  # Check if the config directory exists
            parents=True, exist_ok=True
        )
        # Set the default configuration
        self.default = list(default_config) if default_config is not None else []
        # Store the validation flag
        self.validate_structure = validate_structure

        # Load the configuration from the file if auto_load is True
        self.load() if auto_load else self.extend(self.default)

        # Log the initialization of the configuration
        self.logger.info(
            "Configuration initialized with file: '%s'", self.config_file_path
        )
        self.logger.debug("Default configuration values: %s", self.default)

    def load(self) -> None:
        """Load the configuration from the file."""
        if self.config_file_path.exists():  # Check if the configuration file exists
            with self.config_file_path.open("r", encoding="utf-8") as f:
                # Try to load the content of the file as json
                try:
                    content = json.load(f)

                # If the content is not valid json, return the default configuration
                except json.JSONDecodeError:
                    self.logger.warning(
                        "File '%s' is not a valid json file. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    content = self.default

                # Load the configuration from the file if it's a list
                if isinstance(content, list):
                    validated_content = []

                    # Validate each item and build validated content
                    min_len = min(len(content), len(self.default))
                    for i in range(min_len):
                        validated_item = _validate_nested_value(
                            content[i],
                            self.default[i],
                            self.config_file_path.name,
                            self.logger,
                            f"[{i}]",
                        )
                        validated_content.append(validated_item)

                    # Add remaining default items if content is shorter
                    if len(content) < len(self.default):
                        validated_content.extend(self.default[len(content) :])

                    # Check structure validation if enabled
                    if self.validate_structure and len(content) != len(self.default):
                        self.logger.warning(
                            "File '%s' has %d items, but default has %d items. "
                            "Using validated values for matching items.",
                            self.config_file_path.name,
                            len(content),
                            len(self.default),
                        )

                    self.clear()
                    self.extend(validated_content)
                    self.save()
                    self.logger.info(
                        "Configuration loaded successfully from file: '%s'",
                        self.config_file_path,
                    )
                    self.logger.debug(
                        "Loaded configuration values: %s", validated_content
                    )

                else:  # If the content is not a list, return the default configuration
                    self.logger.warning(
                        "File '%s' does not contain a list. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    self.clear()  # Clear the current configuration
                    self.extend(self.default)
                    self.save()  # Save the default configuration to the file

        else:  # Return the default configuration if the file does not exist
            self.logger.warning(
                "File '%s' does not exist. "
                "Returning default configuration and saving it to the file.",
                self.config_file_path.name,
            )
            self.extend(self.default)
            self.save()  # Save the default configuration to the file

    def save(self) -> None:
        """Save the configuration to the file."""
        self.logger.info("Saving configuration to file: '%s'", self.config_file_path)

        # Check if the configuration directory exists
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the configuration to the file
        with self.config_file_path.open("w", encoding="utf-8") as f:
            json.dump(list(self), f, indent=4)

        self.logger.info(
            "Configuration saved successfully to file: '%s'", self.config_file_path
        )


class DictConfig(dict):
    """Configuration class for handling application configuration."""

    def __init__(
        self,
        config_path: Path,
        default_config: dict | None = None,
        auto_load: bool = True,
        validate_structure: bool = False,
    ) -> None:
        """Initialize the configuration.

        Args:
            config_path (Path): The path to the configuration file.
            default_config (dict): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration
                from the file upon initialization.
                If False, the default configuration will be used while initializing.
                Defaults to True.
            validate_structure (bool): Whether to validate that the loaded
                configuration matches the structure, keys, and value types of
                the default configuration. If False, any valid dictionary will
                be accepted. Defaults to False.

        """
        # Initialize the dictionary and set up logging
        super().__init__()
        self.logger = logger.getChild(
            self.__class__.__name__ + "('" + str(config_path) + "')"
        )

        # Set the configuration file path
        self.config_file_path = CONFIG_DIRECTORY / config_path
        self.config_file_path.parent.mkdir(  # Check if the config directory exists
            parents=True, exist_ok=True
        )
        # Set the default configuration
        self.default = dict(default_config) if default_config is not None else {}
        # Store the validation flag
        self.validate_structure = validate_structure

        # Load the configuration from the file if auto_load is True
        self.load() if auto_load else self.update(self.default)

        # Log the initialization of the configuration
        self.logger.info(
            "Configuration initialized with file: '%s'", self.config_file_path
        )
        self.logger.debug("Default configuration values: %s", self.default)

    def load(self) -> None:
        """Load the configuration from the file."""
        self.logger.info("Loading configuration from file: '%s'", self.config_file_path)
        if self.config_file_path.exists():  # Check if the configuration file exists
            with self.config_file_path.open("r", encoding="utf-8") as f:
                # Try to load the content of the file as json
                try:
                    content = json.load(f)

                # If the content is not valid json, return the default configuration
                except json.JSONDecodeError:
                    self.logger.warning(
                        "File '%s' is not a valid json file. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    content = self.default

                # Load the configuration from the file if it's a dictionary
                if isinstance(content, dict):
                    validated_content = {}

                    # Validate each key and build validated content
                    for key in self.default:
                        if key in content:
                            validated_content[key] = _validate_nested_value(
                                content[key],
                                self.default[key],
                                self.config_file_path.name,
                                self.logger,
                                key,
                            )
                        else:
                            self.logger.warning(
                                "File '%s' missing key '%s'. Using default value.",
                                self.config_file_path.name,
                                key,
                            )
                            validated_content[key] = self.default[key]

                    # Add extra keys from loaded content
                    # if structure validation is disabled
                    if not self.validate_structure:
                        for key in content:
                            if key not in validated_content:
                                validated_content[key] = content[key]

                    # Check structure validation if enabled
                    if self.validate_structure and set(content.keys()) != set(
                        self.default.keys()
                    ):
                        self.logger.warning(
                            "File '%s' has keys %s, but default has keys %s. "
                            "Using validated values for matching keys.",
                            self.config_file_path.name,
                            set(content.keys()),
                            set(self.default.keys()),
                        )

                    self.clear()
                    self.update(validated_content)
                    self.save()
                    self.logger.info(
                        "Configuration loaded successfully from file: '%s'",
                        self.config_file_path,
                    )
                    self.logger.debug(
                        "Loaded configuration values: %s", validated_content
                    )

                # If the content is not a dictionary, return the default configuration
                else:
                    self.logger.warning(
                        "File '%s' does not contain a dictionary. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    self.clear()  # Clear the current configuration
                    self.update(self.default)
                    self.save()  # Save the default configuration to the file
        else:  # Return the default configuration if the file does not exist
            self.logger.warning(
                "File '%s' does not exist. "
                "Returning default configuration and saving it to the file.",
                self.config_file_path.name,
            )
            self.update(  # Update the configuration with the default values
                self.default
            )
            self.save()  # Save the default configuration to the file

    def save(self) -> None:
        """Save the configuration to the file."""
        self.logger.info("Saving configuration to file: '%s'", self.config_file_path)

        # Check if the configuration directory exists
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the configuration to the file
        with self.config_file_path.open("w", encoding="utf-8") as f:
            json.dump(self, f, indent=4)

        self.logger.info(
            "Configuration saved successfully to file: '%s'", self.config_file_path
        )


class SetConfig(set):
    """Configuration class for handling application configuration."""

    def __init__(
        self,
        config_path: Path,
        default_config: set | None = None,
        auto_load: bool = True,
        validate_structure: bool = False,
    ) -> None:
        """Initialize the configuration.

        Args:
            config_path (Path): The path to the configuration file.
            default_config (set): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration
                from the file upon initialization.
                If False, the default configuration will be used while initializing.
                Defaults to True.
            validate_structure (bool): Whether to validate that the loaded
                configuration matches the structure, items, and value types of
                the default configuration. If False, any valid list will be
                converted to a set. Defaults to False.

        """
        # Initialize the set and set up logging
        super().__init__()
        self.logger = logger.getChild(
            self.__class__.__name__ + "('" + str(config_path) + "')"
        )

        # Set the configuration file path
        self.config_file_path = CONFIG_DIRECTORY / config_path
        self.config_file_path.parent.mkdir(  # Check if the config directory exists
            parents=True, exist_ok=True
        )
        # Set the default configuration
        self.default = set(default_config) if default_config is not None else set()
        # Store the validation flag
        self.validate_structure = validate_structure

        # Load the configuration from the file if auto_load is True
        self.load() if auto_load else self.update(self.default)

        # Log the initialization of the configuration
        self.logger.info(
            "Configuration initialized with file: '%s'", self.config_file_path
        )
        self.logger.debug("Default configuration values: %s", self.default)

    def load(self) -> None:
        """Load the configuration from the file."""
        self.logger.info("Loading configuration from file: '%s'", self.config_file_path)
        if self.config_file_path.exists():  # Check if the configuration file exists
            with self.config_file_path.open("r", encoding="utf-8") as f:
                # Try to load the content of the file as json
                try:
                    content = json.load(f)

                # If the content is not valid json, return the default configuration
                except json.JSONDecodeError:
                    self.logger.warning(
                        "File '%s' is not a valid json file. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    content = list(self.default)

                # Load the configuration from the file if it's a list
                if isinstance(content, list):
                    validated_items = set()

                    # Validate each item and build validated set
                    for loaded_item in content:
                        # Find a corresponding default item of same value
                        matched = False
                        for default_item in self.default:
                            if loaded_item == default_item:
                                validated_item = _validate_nested_value(
                                    loaded_item,
                                    default_item,
                                    self.config_file_path.name,
                                    self.logger,
                                    str(loaded_item),
                                )
                                validated_items.add(validated_item)
                                matched = True
                                break

                        # If no matching default item found, use loaded item as-is
                        # (if structure validation disabled)
                        if not matched and not self.validate_structure:
                            validated_items.add(loaded_item)

                    # Add missing default items
                    for default_item in self.default:
                        if default_item not in validated_items:
                            validated_items.add(default_item)

                    # Check structure validation if enabled
                    if self.validate_structure and validated_items != self.default:
                        self.logger.warning(
                            "File '%s' has %d unique items, but default has %d "
                            "unique items. Using validated values.",
                            self.config_file_path.name,
                            len(validated_items),
                            len(self.default),
                        )

                    self.clear()
                    self.update(validated_items)
                    self.save()
                    self.logger.info(
                        "Configuration loaded successfully from file: '%s'",
                        self.config_file_path,
                    )
                    self.logger.debug(
                        "Loaded configuration values: %s", validated_items
                    )

                # If the content is not a list, return the default configuration
                else:
                    self.logger.warning(
                        "File '%s' does not contain a list. "
                        "Returning default configuration.",
                        self.config_file_path.name,
                    )
                    self.clear()  # Clear the current configuration
                    self.update(self.default)
                    self.save()  # Save the default configuration to the file
        else:  # Return the default configuration if the file does not exist
            self.logger.warning(
                "File '%s' does not exist. "
                "Returning default configuration and saving it to the file.",
                self.config_file_path.name,
            )
            self.update(self.default)
            self.save()  # Save the default configuration to the file

    def save(self) -> None:
        """Save the configuration to the file."""
        self.logger.info("Saving configuration to file: '%s'", self.config_file_path)

        # Check if the configuration directory exists
        self.config_file_path.parent.mkdir(parents=True, exist_ok=True)

        # Save the configuration to the file
        with self.config_file_path.open("w", encoding="utf-8") as f:
            json.dump(sorted(self), f, indent=4)

        self.logger.info(
            "Configuration saved successfully to file: '%s'", self.config_file_path
        )
