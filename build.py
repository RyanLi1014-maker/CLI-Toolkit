"""Build script for the CLI Toolkit.

This script can use PyInstaller to create a executable for the CLI Toolkit.
And it can include all of the stdlibs in the final executable.
"""

from subprocess import run
from sys import stdlib_module_names


def build():
    """Build the CLI Toolkit executable using PyInstaller."""
    stdlib_list = list(stdlib_module_names)
    hidden_imports = ["--hidden-import=" + lib for lib in stdlib_list]
    run(
        [
            "pyinstaller",
            "--name",
            "CLI-Toolkit",
            *hidden_imports,
            "--collect-all=rich",
            "--noconfirm",
            "main.py",
        ],
        check=True,
    )


if __name__ == "__main__":
    build()
