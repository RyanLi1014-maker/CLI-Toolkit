"""Main entry point for the CLI-Toolkit application."""

# Import libraries
import logging
from sys import path as sys_path

# Import the CLI-Toolkit application
from src.app import CLIToolkitApp
from src.util.project_root import PROJECT_ROOT

# Setup the package path
(PROJECT_ROOT / "package").mkdir(exist_ok=True, parents=True)
sys_path.append(str(PROJECT_ROOT / "package"))

# Setup logging
logging_directory = PROJECT_ROOT / "log"
logging_directory.mkdir(parents=True, exist_ok=True)
logging.basicConfig(  # Initialize the logger
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s][%(name)s] "
    "(%(filename)s:%(lineno)d) - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=logging_directory / "CLI-Toolkit.log",
    filemode="w",
    encoding="utf-8",
)

if __name__ == "__main__":
    app = CLIToolkitApp()
    app.mainloop()
