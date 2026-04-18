"""Configuration utilities."""

import json  # json file handling
from pathlib import Path  # file path handling
import logging  # Logging module


class Config(dict):
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
                try:
                    content = json.load(f)
                except json.JSONDecodeError:
                    self.logger.warning(
                        f"File '{self.config_file_path.name}' is not a valid json file. Returning default configuration."
                    )
                    content = self.default
                self.update(content)  # Load the configuration from the file
        else:  # If the configuration file does not exist, return the default configuration
            self.logger.warning(
                f"File '{self.config_file_path.name}' does not exist. Returning default configuration and saving it to the file."
            )
            self.update(
                self.default
            )  # Update the configuration with the default values
            self.save()  # Save the default configuration to the file

    def save(self):
        """Save the configuration to the file."""
        # Check if the configuration directory exists
        if not self.config_file_path.parent.exists():
            self.logger.warning("Config directory does not exist. Creating...")
            self.config_file_path.parent.mkdir(parents=True)
        with open(self.config_file_path, "w", encoding="utf-8") as f:
            json.dump(self, f, indent=4)

    def __getitem__(self, key):
        if key in self:  # Check in the configuration
            return super().__getitem__(key)
        elif key in self.default:  # Check in the default configuration
            return self.default[key]
        else:  # If the key does not exist in the configuration or the default configuration, raise an error
            raise KeyError(f"Key '{key}' does not exist in the configuration.")
