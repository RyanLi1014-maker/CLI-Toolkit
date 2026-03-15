# CLI-Toolkit

A flexible and customizable command-line interface (CLI) application, featuring built-in command handling, colored output, and intuitive user interaction.

## Features

### Currently had

- Clean, modular CLI architecture
- Colored terminal output for better user experience
- `help` command based on smart docstring recognition
- Shell-like command parsing (supports quotes and special characters)

### Todo

- A very easy-to-develop plugin system

# Installation

**_Precautions: The project required Python3.6 or above._**

1. Clone this repository:

   ```
   git clone https://github.com/RyanLi1014-maker/CLI-Toolkit.git
   cd CLI-Toolkit
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Run the Application

Execute the main entry point to start the CLI-Toolkit:

```
python main.py
```

### Basic Commands

| Command | Description                                                             |
| ------- | ----------------------------------------------------------------------- |
| `help`  | Show list of available commands or detailed help for a specific command |
| `exit`  | Exit the application.                                                   |

### Example Workflow

1. Start the application:
   ```
   python main.py
   ```
2. You'll see the CLI-Toolkit logo and welcome message:

   ```
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

   Welcome to the CLI-Toolkit! Type 'help' to list commands.
   Type 'exit' to exit the application.
   CLI-Toolkit>
   ```

3. Interact with the application:
   - List all commands:
     ```
     CLI-Toolkit> help
     ```
   - Get detailed help for a command:
     ```
     CLI-Toolkit> help [command_name]
     ```
   - Exit the application:
     ```
     CLI-Toolkit> exit
     ```

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
