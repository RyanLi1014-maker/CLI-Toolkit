"""Main entry point for the CLI-Tookit application."""
from sys import path # Import the sys module to manipulate the system path for module imports
path[0] = "./src" # Set the first entry in the system path to the src directory for module imports

from app import CLI_Toolkit_App # Import the CLI_Toolkit_App class from the app module

if __name__ == "__main__":
    app = CLI_Toolkit_App()
    app.mainloop()