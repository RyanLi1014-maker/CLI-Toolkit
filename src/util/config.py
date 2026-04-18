"""Configuration utilities."""

import json  # json file handling
from pathlib import Path  # file path handling
import logging  # Logging module


class ListConfig(list):
    def __init__(
        self, config_path: Path, default_config: list = [], auto_load: bool = True
    ):
        """Initialize the configuration.
        Args:
            config_path (Path): The path to the configuration file.
            default_config (list): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration from the file upon initialization. If False, the default configuration will be used while initializing. Defaults to True.
        """

        # Initialize the list and set up logging
        super().__init__()
        self.logger = logging.getLogger("Config")
        self.config_file_path = Path("config") / config_path

        # Check if the config directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        self.default = default_config

        # Load the configuration from the file if auto_load is True, otherwise update the configuration with the default values
        self.load() if auto_load else self.extend(default_config)

    def load(self):
        """Load the configuration from the file."""
        if self.config_file_path.exists():  # Check if the configuration file exists
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                # Try to load the content of the file as json, if it fails, log a warning and return the default configuration
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"File '{self.config_file_path.name}' is not a valid json file. Returning default configuration."
                    )
                    content = self.default
                # Load the configuration from the file if it's a list, otherwise load an empty list
                if isinstance(content, list):
                    self.extend(content)
                else:
                    self.logger.warning(  # Log a warning if the content of the file is not a list and return the default configuration
                        f"File '{self.config_file_path.name}' does not contain a list. Returning default configuration."
                    )
                    self.clear()  # Clear the current configuration before loading the default configuration
                    self.extend(self.default)
                    self.save()  # Save the default configuration to the file
        else:  # If the configuration file does not exist, return the default configuration
            self.logger.warning(
                f"File '{self.config_file_path.name}' does not exist. Returning default configuration and saving it to the file."
            )
            self.extend(  # Update the configuration with the default values
                self.default
            )
            self.save()  # Save the default configuration to the file

    def save(self):
        """Save the configuration to the file."""
        # Check if the configuration directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(self, f, indent=4)


class DictConfig(dict):
    """Configuration class for handling application configuration."""

    def __init__(
        self,
        config_path: Path,
        default_config: dict = {},
        auto_load: bool = True,
    ):
        """Initialize the configuration.
        Args:
            config_path (Path): The path to the configuration file.
            default_config (dict): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration from the file upon initialization. If False, the default configuration will be used while initializing. Defaults to True.
        """

        # Initialize the dictionary and set up logging
        super().__init__()
        self.logger = logging.getLogger("Config")
        self.config_file_path = Path("config") / config_path

        # Check if the config directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        self.default = default_config

        # Load the configuration from the file if auto_load is True, otherwise update the configuration with the default values
        self.load() if auto_load else self.update(default_config)

    def load(self):
        """Load the configuration from the file."""
        if self.config_file_path.exists():  # Check if the configuration file exists
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                # Try to load the content of the file as json, if it fails, log a warning and return the default configuration
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"File '{self.config_file_path.name}' is not a valid json file. Returning default configuration."
                    )
                    content = self.default
                # Load the configuration from the file if it's a dictionary, otherwise load an empty dictionary
                if isinstance(content, dict):
                    self.update(content)
                else:
                    self.logger.warning(  # Log a warning if the content of the file is not a dictionary and return the default configuration
                        f"File '{self.config_file_path.name}' does not contain a dictionary. Returning default configuration."
                    )
                    self.clear()  # Clear the current configuration before loading the default configuration
                    self.update(self.default)
                    self.save()  # Save the default configuration to the file
        else:  # If the configuration file does not exist, return the default configuration
            self.logger.warning(
                f"File '{self.config_file_path.name}' does not exist. Returning default configuration and saving it to the file."
            )
            self.update(  # Update the configuration with the default values
                self.default
            )
            self.save()  # Save the default configuration to the file

    def save(self):
        """Save the configuration to the file."""
        # Check if the configuration directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(self, f, indent=4)


class SetConfig(set):
    def __init__(
        self, config_path: Path, default_config: set = set(), auto_load: bool = True
    ):
        """Initialize the configuration.
        Args:
            config_path (Path): The path to the configuration file.
            default_config (set): The default configuration values.
            auto_load (bool): Whether to automatically load the configuration from the file upon initialization. If False, the default configuration will be used while initializing. Defaults to True.
        """

        # Initialize the set and set up logging
        super().__init__()
        self.logger = logging.getLogger("Config")
        self.config_file_path = Path("config") / config_path

        # Check if the config directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        self.default = default_config

        # Load the configuration from the file if auto_load is True, otherwise update the configuration with the default values
        self.load() if auto_load else self.update(default_config)

    def load(self):
        """Load the configuration from the file."""
        if self.config_file_path.exists():  # Check if the configuration file exists
            with open(self.config_file_path, "r", encoding="utf-8") as f:
                # Try to load the content of the file as json, if it fails, log a warning and return the default configuration
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"File '{self.config_file_path.name}' is not a valid json file. Returning default configuration."
                    )
                    content = list(self.default)
                # Load the configuration from the file if it's a list, otherwise load an empty set
                if isinstance(content, list):
                    self.update(content)
                else:
                    self.logger.warning(
                        f"File '{self.config_file_path.name}' does not contain a list. Returning default configuration."
                    )
                    self.clear()  # Clear the current configuration before loading the default configuration
                    self.update(self.default)
                    self.save()  # Save the default configuration to the file
        else:  # If the configuration file does not exist, return the default configuration
            self.logger.warning(
                f"File '{self.config_file_path.name}' does not exist. Returning default configuration and saving it to the file."
            )
            self.update(  # Update the configuration with the default values
                list(self.default) if isinstance(self.default, set) else []
            )
            self.save()  # Save the default configuration to the file

    def save(self):
        """Save the configuration to the file."""
        # Check if the configuration directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(sorted(list(self)), f, indent=4)
