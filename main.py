"""Main entry point for the CLI-Tookit application."""
from src.app import CLI_Toolkit_App # Import the CLI_Toolkit_App class from the app module

if __name__ == "__main__":
    app = CLI_Toolkit_App()
    app.mainloop()