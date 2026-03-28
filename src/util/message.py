"""Functions for displaying informational, warning, and error messages in the terminal with colored output."""

from colorama import Fore, Style  # Import colorama for colored output in the terminal


def show_info(category: str, *content: str):
    """Show an informational message with a category label.
    Args:
        category (str): The category label for the informational message.
        content (str): The informational message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTBLUE_EX + f"[INFO/{category}]" + Style.RESET_ALL,
        Fore.BLUE + content[0] + Style.RESET_ALL,
        *content[1:] if len(content) > 1 else "",
    )


def show_success(category: str, *content: str):
    """Show a success message with a category label.

    Args:
        category (str): The category label for the success message.
        content (str): The success message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTGREEN_EX + f"[SUCCESS/{category}]" + Style.RESET_ALL,
        Fore.GREEN + content[0] + Style.RESET_ALL,
        *content[1:] if len(content) > 1 else "",
    )


def show_warning(category: str, *content: str):
    """Show a warning message with a category label.
    Args:
        category (str): The category label for the warning message.
        content (str): The warning message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTYELLOW_EX + f"[WARNING/{category}]" + Style.RESET_ALL,
        Fore.YELLOW + content[0] + Style.RESET_ALL,
        *content[1:] if len(content) > 1 else "",
    )


def show_error(category: str, *content: str):
    """Show an error message with a category label.
    Args:
        category (str): The category label for the error message.
        content (str): The error message to display. The first element is the main message, and the rest are additional details.
    """
    print(
        Style.BRIGHT + Fore.LIGHTRED_EX + f"[ERROR/{category}]" + Style.RESET_ALL,
        Fore.RED + content[0] + Style.RESET_ALL,
        *content[1:] if len(content) > 1 else "",
    )


class ProgressBar:
    """A progress bar in the command line interface."""

    def __init__(
        self,
        category: str,
        total: int,
        describe: str = "",
        decimals: int = 1,
        length: int = 50,
        completed_fill: str = "#",
        uncompleted_fill: str = "-",
    ):
        """Initialize the progress bar.

        Args:
            category (str): Category of the progress bar.
            total (int): Total number of steps.
            describe (str, optional): Description of the progress bar. Defaults to "".
            decimals (int, optional): Number of decimals in percent complete. Defaults to 1.
            length (int, optional): Character length of bar. Defaults to 50.
            completed_fill (str, optional): Bar fill character. Defaults to "#".
            uncompleted_fill (str, optional): Uncompleted bar fill character. Defaults to "-".
        """
        self.category = category  # Category of the progress bar
        self.total = total  # Total number of steps
        self.completed = 0  # Number of steps completed, printing as the `fill` argument
        self.describe = describe  # Description of the progress bar
        self.decimals = decimals  # Number of decimals in percent complete
        self.length = length  # Character length of bar
        self.completed_fill = completed_fill  # Completed progress bar character
        self.uncompleted_fill = uncompleted_fill  # Uncompleted progress bar character
        self.update(0)

    def update(self, complete: int = 1):
        """Update the progress bar.

        Args:
            completed (int, optional): Number of steps completed. Defaults to 1.
        """
        self.completed += complete  # Increment the number of steps completed
        # Check if the number of steps completed is greater than the total number of steps
        if self.completed >= self.total:
            self.complete()
        else:  # If the number of steps completed is less than the total number of steps
            # Calculate and format the percent complete
            percent = (self.completed / self.total) * 100
            percent_str = f"{percent:.{self.decimals}f}"
            # Calculate the length of the completed and uncompleted bars
            completed_bar_length = int(self.length * percent / 100)
            uncompleted_bar_length = self.length - completed_bar_length
            # Create the progress bar
            bar = (
                Fore.LIGHTGREEN_EX
                + self.completed_fill * completed_bar_length
                + Style.RESET_ALL
                + Style.DIM
                + Fore.LIGHTGREEN_EX
                + self.uncompleted_fill * uncompleted_bar_length
                + Style.RESET_ALL
            )
            bar_str = (
                Style.BRIGHT
                + Fore.LIGHTGREEN_EX
                + f"[PROG/{self.category}] "
                + Style.RESET_ALL  # Progress bar header (Category of the progress bar)
                + Fore.GREEN
                + self.describe  # Progress bar prefix text
                + Style.RESET_ALL
                + f" [{bar}] "  # Progress bar
                + f"{percent_str}%"  # Percent complete
            )
            print(bar_str, end="\r", flush=True)  # Print the progress bar

    def complete(self):
        """Complete and close the progress bar."""
        bar = Fore.LIGHTGREEN_EX + self.completed_fill * self.length + Style.RESET_ALL
        bar_str = (
            Style.BRIGHT
            + Fore.LIGHTGREEN_EX
            + f"[PROG/{self.category}] "
            + Style.RESET_ALL  # Progress bar header (Category of the progress bar)
            + Fore.GREEN
            + self.describe  # Progress bar prefix text
            + Style.RESET_ALL
            + f" [{bar}] "  # Progress bar
            + Fore.LIGHTGREEN_EX
            + f"Completed!"  # Percent complete
            + Style.RESET_ALL
        )
        print(bar_str)
        del self
