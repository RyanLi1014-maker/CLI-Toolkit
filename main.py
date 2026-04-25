"""Main entry point for the CLI-Toolkit application."""

# Set the path to the src directory
import sys

sys.path[0] = "./src"

# Import the CLI-Toolkit application
from app import CLI_Toolkit_App  # noqa: E402

if __name__ == "__main__":
    app = CLI_Toolkit_App()
    app.mainloop()
