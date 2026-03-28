"""Configuration utilities."""

import json  # json file handling
from pathlib import Path  # file path handling

from src.util.message import *  # Message module


class Config(dict):
    """Configuration class for handling application configuration."""

    def __init__(self, config_path: Path, default_config: dict = {}):
        """Initialize the configuration.
        Args:
            config_path (Path): The path to the configuration file.
            default_config (dict): The default configuration values.
        """
        super().__init__()  # Initialize the dictionary
        self.confg_file_path = Path("config") / config_path
        # Check if the config directory exists
        if not self.confg_file_path.parent.exists():
            show_warning("Config", "Config directory does not exist. Creating...")
            self.confg_file_path.parent.mkdir()
        self.default = default_config

    def load(self):
        """Load the configuration from the file."""
        if self.confg_file_path.exists():  # Check if the configuration file exists
            with open(self.confg_file_path, "r") as f:
                self.update(json.load(f))  # Load the configuration from the file
        else:  # If the configuration file does not exist, return the default configuration
            self.update(
                self.default
            )  # Update the configuration with the default values
            self.save()  # Save the default configuration to the file

    def save(self):
        """Save the configuration to the file."""
        # Check if the configuration directory exists
        if not self.confg_file_path.parent.exists():
            show_warning("Config", "Config directory does not exist. Creating...")
            self.confg_file_path.parent.mkdir()
        with open(self.confg_file_path, "w") as f:
            json.dump(self, f, indent=4)
