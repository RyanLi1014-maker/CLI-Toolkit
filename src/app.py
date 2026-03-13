"""CLI-Tookit Application"""
import cli # Command-line interface module

class CLI_Toolkit_App(cli.CLI):
    """Command-line interface class."""
    def __init__(self):
        """Initialize the CLI-Tookit application."""
        super().__init__()
        self.prompt = "CLI-Toolkit> " # Prompt for user input
        self.intro = ( # Introduction message displayed when the application starts
            "Welcome to the CLI Toolkit! Type 'help' to list commands.\n"
            "Type 'exit' to exit the application."
        )

if __name__ == "__main__": # Test the CLI-Tookit Application
    app = CLI_Toolkit_App()
    app.mainloop()