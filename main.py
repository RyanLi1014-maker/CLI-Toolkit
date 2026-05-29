"""Main entry point for the CLI-Toolkit application."""

# Import libraries
import argparse
import logging
from sys import path as sys_path

# Import the CLI-Toolkit application
from src.app import CLIToolkitApp
from src.util.project_root import PROJECT_ROOT

# Setup the argument parser
arg_parser = argparse.ArgumentParser(description="CLI-Toolkit")

# Add the arguments
arg_parser.add_argument(
    "-v",
    "--verbose",
    action="store_true",
    help="Log the verbose output while running the application",
)

# Parse the arguments
args = arg_parser.parse_args()

# Setup the package path
(PROJECT_ROOT / "package").mkdir(exist_ok=True, parents=True)
sys_path.append(str(PROJECT_ROOT / "package"))

# Setup logging
logging_directory = PROJECT_ROOT / "log"
logging_directory.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.DEBUG if args.verbose else logging.INFO,
    format="%(asctime)s | %(name)-25s | %(levelname)-8s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    filename=logging_directory / "CLI-Toolkit.log",
    filemode="w",
    encoding="utf-8",
)

if __name__ == "__main__":
    app = CLIToolkitApp()
    app.mainloop()
