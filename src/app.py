"""CLI-Tookit Application"""
import cli # Command-line interface module

logo = r"""
         ________      ___           ___                                                    
        |\   ____\    |\  \         |\  \                                                   
        \ \  \___|    \ \  \        \ \  \    ____________                                  
         \ \  \        \ \  \        \ \  \  |\____________\                                
          \ \  \____    \ \  \____    \ \  \ \|____________|                                
           \ \_______\   \ \_______\   \ \__\                                               
            \|_______|    \|_______|    \|__|                                               
                                                                                            
 _________    ________      ________      ___           ___  __        ___      _________   
|\___   ___\ |\   __  \    |\   __  \    |\  \         |\  \|\  \     |\  \    |\___   ___\ 
\|___ \  \_| \ \  \|\  \   \ \  \|\  \   \ \  \        \ \  \/  /|_   \ \  \   \|___ \  \_| 
     \ \  \   \ \  \\\  \   \ \  \\\  \   \ \  \        \ \   ___  \   \ \  \       \ \  \  
      \ \  \   \ \  \\\  \   \ \  \\\  \   \ \  \____    \ \  \\ \  \   \ \  \       \ \  \ 
       \ \__\   \ \_______\   \ \_______\   \ \_______\   \ \__\\ \__\   \ \__\       \ \__\
        \|__|    \|_______|    \|_______|    \|_______|    \|__| \|__|    \|__|        \|__|
"""

class CLI_Toolkit_App(cli.CLI):
    """Command-line interface class."""
    def __init__(self):
        """Initialize the CLI-Tookit application."""
        super().__init__()
        self.prompt = "CLI-Toolkit> " # Prompt for user input
        self.intro = ( # Introduction message displayed when the application starts
            logo + "\n"
            "Welcome to the CLI Toolkit! Type 'help' to list commands.\n"
            "Type 'exit' to exit the application."
        )

if __name__ == "__main__": # Test the CLI-Tookit Application
    app = CLI_Toolkit_App()
    app.mainloop()