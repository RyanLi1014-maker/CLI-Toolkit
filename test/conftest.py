"""Test configuration for pytest."""

from pathlib import Path
from sys import path as sys_path

sys_path[0] = str(Path(__file__).parent.parent)
