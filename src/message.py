"""Functions for displaying informational, warning, and error messages in the terminal with colored output."""
from colorama import Fore, Style # Import colorama for colored output in the terminal

def show_info(category: str = "\b", *content):
    """Show an informational message with a category label.
    Args:
        category (str): The category label for the informational message.
        content (str): The informational message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT +Fore.LIGHTBLUE_EX + f"[INFO/{category}]" + Style.RESET_ALL,
        Fore.BLUE + content[0] + Fore.RESET,
        *content[1:] if len(content) > 1 else ""
    )

def show_success(category: str = "\b", *content):
    """Show a success message with a category label.

    Args:
        category (str): The category label for the message. Defaults to "\b".
        content (str): The success message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT +Fore.LIGHTGREEN_EX + f"[SUCCESS/{category}]" + Style.RESET_ALL,
        Fore.GREEN + content[0] + Fore.RESET,
        *content[1:] if len(content) > 1 else ""
    )

def show_warning(category: str = "\b", *content):
    """Show a warning message with a category label.
    Args:
        category (str): The category label for the warning message.
        content (str): The warning message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTYELLOW_EX + f"[WARNING/{category}]" + Style.RESET_ALL,
        Fore.YELLOW + content[0] + Fore.RESET,
        *content[1:] if len(content) > 1 else ""
    )

def show_error(category: str = "\b", *content):
    """Show an error message with a category label.
    Args:
        category (str): The category label for the error message.
        content (str): The error message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTRED_EX + f"[ERROR/{category}]" + Style.RESET_ALL,
        Fore.RED + content[0] + Fore.RESET,
        *content[1:] if len(content) > 1 else ""
    )
