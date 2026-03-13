"""Command-line interface"""
import shlex # Shell-like syntax parsing
from colorama import Fore, Style # Import colorama for colored output in the terminal

class CLI:
    """Command-line interface class."""
    def __init__(self):
        """Initialize the CLI interface."""
        self.prompt = "" # Prompt for user input
        self.intro = "" # Introduction message displayed when the application starts
    
    def cmd_exit(self, *_):
        """Exit the application."""
        print("Goodbye!")
        exit(0)
    
    def cmd_help(self, cmd: str = ""):
        """Show help information for commands.
        If a specific command is provided, show detailed help for that command.
        Otherwise, show a list of available commands.
        """
        if cmd: # If a specific command is provided, show detailed help for that command
            method_name = f"cmd_{cmd}"
            method_attr = getattr(self, method_name, None)
            if callable(method_attr) and method_attr != self.cmd_default:
                if method_attr.__doc__: # If the method has no docstring, provide a default message
                    print(
                        Fore.BLUE + f"Detailed description of {cmd}:" + Fore.RESET
                    )
                    lines = method_attr.__doc__.splitlines() # Split the docstring into lines
                    indented_lines = ["  " + line for line in lines] # Indent each line for better readability
                    indented_doc = "\n".join(indented_lines) # Join the indented lines back into a single string
                    print(indented_doc)
                else: # If the method has no docstring, provide a default message
                    print(
                        Fore.BLUE + f"Detailed description of {cmd}:" + Fore.RESET,
                        "No description available."
                    )
            else:
                self.cmd_default(cmd)
        else: # If no specific command is provided, show a list of available commands
            print(Fore.BLUE + "Available commands:" + Fore.RESET)
            for method_name in dir(self):
                if not method_name.startswith("cmd_"):
                    continue
                method_attr = getattr(self, method_name, None)
                if callable(method_attr) and method_attr != self.cmd_default:
                    if method_attr.__doc__: # If the method has no docstring, provide a default message
                        print(
                            Fore.BLUE + f"  {method_name[4:]}:" + Fore.RESET,
                            method_attr.__doc__.splitlines()[0]
                        )
                    else: # If the method has no docstring, provide a default message
                        print(
                            Fore.BLUE + f"  {method_name[4:]}:" + Fore.RESET,
                            "No description available."
                        )

    def cmd_default(self, cmd: str):
        """Handle unrecognized commands."""
        print( # Print an error message in red color for unrecognized commands
            Style.BRIGHT + Fore.LIGHTRED_EX + "[Error]" + Style.RESET_ALL,
            Fore.RED + f"Unknown command: {cmd}." + Fore.RESET,
            "Type 'help' for a list of commands."
        )

    def _dispatch(self, input_cmd: str):
        """Dispatch the command to the appropriate handler."""
        input_cmd = input_cmd.strip() # Remove leading/trailing whitespace
        if not input_cmd: # Ignore empty commands
            return
        parsed_cmd = shlex.split(input_cmd) # Parse the command using shell-like syntax
        cmd = parsed_cmd[0] if parsed_cmd else "" # Get the command name
        args = parsed_cmd[1:] if len(parsed_cmd) > 1 else [] # Get the command arguments
        method = getattr(self, f"cmd_{cmd}", None) # Get the method corresponding to the command
        if callable(method): # If the method exists and is callable, call it with the arguments
            method(*args)
        else: # If the command is not recognized, call the default handler
            self.cmd_default(input_cmd)

    def mainloop(self):
        """Start the command loop."""
        print(Fore.CYAN + self.intro + Fore.RESET) # Print the introduction message in yellow color
        while True: # Infinite loop to continuously prompt for user input and dispatch commands
            try:
                command = input( # Get user input
                    Fore.LIGHTMAGENTA_EX + self.prompt + Fore.YELLOW
                )
                print(Fore.RESET, end="") # Reset color after the prompt
                self._dispatch(command) # Dispatch the command
            except (KeyboardInterrupt, EOFError): # Handle Ctrl+C and Ctrl+D gracefully
                print(Fore.RESET + "\nGoodbye!")
                break

if __name__ == "__main__": # Test the CLI application
    cli = CLI()
    cli.intro = (
        "Welcome to the CLI Test! Type 'help' to list commands.\n"
        "Type 'exit' to exit the application."
    )
    cli.prompt = "CLI-Test> "
    cli.mainloop()