"""Command-line interface"""
import shlex # Shell-like syntax parsing
import string # String manipulation utilities
from colorama import Fore # Import colorama for colored output in the terminal

from message import * # Message module

class CLI:
    """Command-line interface class."""
    def __init__(self, prompt: str = "", intro: str = ""):
        """Initialize the CLI interface.
        Args:
            prompt (str): The prompt to display for user input.
            intro (str): The introduction message to display when the application starts.
        """
        self.prompt = prompt # Prompt for user input
        self.intro = intro # Introduction message displayed when the application starts

    def cmd_exit(self, _):
        """Exit the application.
        Equivalent to Ctrl+C, this command exits the application with code 0.
        Usage:
            exit: Exit the application with code 0.
        Options:
            None
        """
        show_info(
            "CLI",
            "Exiting the application."
        )
        print("Goodbye!")
        exit(0) # Exit the application with code 0 on exit command

    def cmd_help(self, args: list):
        """Show help information for commands.
        If a specific command is provided, show detailed help for that command.
        Otherwise, show a list of available commands.
        Usage:
            help: Show command list.
            help <command>: Show detailed descriptions for [command].
        Options:
            command: The specific command to show detailed help for.
        """
        if args: # If a specific command is provided, show detailed help for that command
            cmd_name = args[0] # Get the command name from the arguments
            method_attr = getattr(self, f"cmd_{cmd_name}", None) # Get the method attribute for the command
            if callable(method_attr): # If the method exists and is callable, show its docstring as detailed help
                if method_attr.__doc__: # If the method has a docstring, provide a default message
                    print(
                        Fore.BLUE + f"Detailed description of {cmd_name}:" + Fore.RESET
                    )
                    lines = method_attr.__doc__.splitlines() # Split the docstring into lines
                    indented_lines = ["    " + line for line in lines] # Indent each line for better readability
                    indented_doc = "\n".join(indented_lines) # Join the indented lines back into a single string
                    print(indented_doc)
                else: # If the method has no docstring, provide a default message
                    print(
                        "Command",
                        Fore.BLUE + cmd_name + Fore.RESET,
                        "has no description available."
                    )
            else:
                self.show_unknown_cmd(cmd_name)
        else: # If no specific command is provided, show a list of available commands
            print(Fore.GREEN + "Available commands:" + Fore.RESET)
            for method_name in dir(self):
                if not method_name.startswith("cmd_"):
                    continue
                method_attr = getattr(self, method_name, None)
                if callable(method_attr):
                    if method_attr.__doc__: # If the method has a docstring, provide a default message
                        print( # Print the command name without the "cmd_" prefix and the first line of the docstring as a brief description
                            Fore.BLUE + f"    {method_name[4:]}:" + Fore.RESET,
                            method_attr.__doc__.splitlines()[0]
                        )
                    else: # If the method has no docstring, provide a default message
                        print(
                            Fore.BLUE + f"    {method_name[4:]}:" + Fore.RESET,
                            "No description available."
                        )
            print("To get detailed help for a specific command, type 'help [command]'.")

    def show_unknown_cmd(self, input_cmd: str = ""):
        """Show an error message for unknown/blank commands.
        Args:
            input_cmd (str): The input command that was not recognized.
        """
        # Remove unprintable characters like shortcut keys from the input command
        input_cmd = "".join([char for char in input_cmd if char in string.printable])
        if input_cmd: # If the input command is not blank, show an error message for unknown command
            show_error(
                "CLI",
                f"'{input_cmd}' is not a recognized command.",
                "Please enter an existing command. Type 'help' for a list of commands."
            )
        else: # If the input command is blank, show an error message for blank command
            show_error(
                "CLI",
                "No command entered.",
                "Please enter an existing command. Type 'help' for a list of commands."
            )

    def _dispatch(self, input_cmd: str):
        """Dispatch the command to the appropriate handler.
        Args:
            input_cmd (str): The raw input command entered by the user.
        """
        try:
            parsed_input = shlex.split(input_cmd) # Parse the command using shell-like syntax
        except ValueError as e: # Handle parsing errors
            show_error(
                "CLI",
                f"Error parsing command: {e}.",
                "Please check your command syntax and try again."
            )
            return
        if not parsed_input: # Ignore blank commands (commands with only spaces)
            return
        cmd = parsed_input[0] if parsed_input else "" # Get the command name
        args = parsed_input[1:] if len(parsed_input) > 1 else [] # Get the command arguments
        method = getattr(self, f"cmd_{cmd}", None) # Get the method corresponding to the command
        if callable(method): # If the method exists and is callable, call it with the arguments
            method(args)
        else: # If the command is not recognized, call the default handler
            self.show_unknown_cmd(cmd)

    def mainloop(self):
        """Start the command loop."""
        print(self.intro) # Print the introduction message in yellow color
        while True: # Infinite loop to continuously prompt for user input and dispatch commands
            try:
                command = input( # Get user input
                    Fore.LIGHTMAGENTA_EX + self.prompt + Fore.YELLOW
                )
                print(Fore.RESET, end="") # Reset color after the prompt
                self._dispatch(command) # Dispatch the command
            except (KeyboardInterrupt, EOFError): # Handle Ctrl+C and Ctrl+D gracefully
                print() # Print a newline for better formatting after Ctrl+C or Ctrl+D
                show_warning(
                    "CLI",
                    "Received interrupt signal.",
                    "Exiting the application."
                )
                print("Goodbye!")
                exit(0) # Exit the application with code 0 on Ctrl+C

if __name__ == "__main__": # Test the CLI application
    show_info("Test", "This is an informational message.", "Description of the informational message.")
    show_warning("Test", "This is a warning message.", "Description of the warning message.")
    show_error("Test", "This is an error message.", "Description of the error message.")
    def infinite_loop(_):
        """A test task that runs an infinite loop, printing a message while running."""
        while True:
            print("Running test task...", end="\r")
    cli = CLI(
        prompt="CLI-Test> ", # Prompt for user input
        intro=( # Introduction message displayed when the application starts
            "Welcome to the CLI Test! Type 'help' to list commands.\n"
            "Type 'exit' to exit the application."
        )
    )
    setattr(cli, "cmd_infinite_loop", infinite_loop) # Add a test task method to the app instance
    cli.mainloop()