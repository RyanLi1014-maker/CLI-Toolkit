# CLI-Toolkit

Have you ever written a large amount of code and placed it all in one folder, feeling chaotic and not knowing what each part is used for?

CLI-Toolkit is a flexible and customizable command-line interface (CLI) application, featuring built-in command handling, colored output, and intuitive user interaction.

More importantly, it inherits an [easy-to-develop plugin system](doc/Plugin%20development.md), where by adding just a few lines of code to your script, you can organize them neatly and conveniently call each function!

## Features

- Clean, modular CLI architecture
- Colored terminal output for better user experience
- `help` command based on smart docstring recognition
- Shell-like command parsing (supports quotes and special characters)
- A very easy-to-develop plugin system

# Usage

## Installation

1.  From [python.org](https://www.python.org/) install Python3.14 or above
2.  Add Python scripts directory to PATH environment variable
3.  Download an arbitrary release from [Releases](https://github.com/RyanLi1014-maker/CLI-Toolkit/releases)
4.  cd to the project directory and run the following command to install the requirements:
    ```bash
    pip install -r requirements.txt
    ```

## Running

1. cd to the project directory
2. Start the application:
   ```bash
   python main.py
   ```
3. You'll see the CLI-Toolkit logo and welcome message:

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

   [INFO/Plugin] Plugin manager initialized.
   [SUCCESS/Plugin] All plugins loaded successfully.

   Welcome to the CLI-Toolkit! Type 'help' to list commands.
   Type 'exit' to exit the application.
   CLI-Toolkit>
   ```

4. Interact with the application:
   - List all commands:
     ```
     CLI-Toolkit> help
     ```
   - Get detailed help for a command:
     ```
     CLI-Toolkit> help <command_name>
     ```
   - Exit the application:
     ```
     CLI-Toolkit> exit
     ```

## Plugin installation

1. Run the application first to create the `plugin` directory if it doesn't exist.
2. Copy your plugin file (e.g., `my_plugin.py`) to the `plugin` directory.
3. Load the plugin in the CLI-Toolkit:
   ```
   CLI-Toolkit> plg load my_plugin
   ```
   If there is any space in the plugin name, you need to use quotes to wrap the plugin name.
   ```
   CLI-Toolkit> plg load "my plugin"
   ```
4. Use help to see the commands provided by the plugin:
   ```
   CLI-Toolkit> help
   ```

After loading the plugin, you can use the plugin's commands as you would use any other command in the CLI-Toolkit.

If you want to develop your own plugin, please refer to [Plugin development](doc/Plugin%20development.md).

# Contributing

If you want to contribute to this project, please follow these steps:

1. From [git-scm.com](http://git-scm.com) install Git
2. From [python.org](https://www.python.org/) install Python3.14 or above
3. Fork the repository.
4. Clone the repository and ckeckout to the develop branch.

   ```bash
   git clone https://github.com/RyanLi1014-maker/CLI-Toolkit.git  # Clone the repository
   cd CLI-Toolkit  # cd to the project directory
   git checkout develop  # Checkout to the develop branch
   pip install -r requirements.txt  # Install the required packages

   ```

5. Create a new branch for your changes.
   ```
   git checkout -b feature-my_feature
   ```
6. Create a pull request to the [develop](https://github.com/RyanLi1014-maker/CLI-Toolkit/tree/develop) branch.
7. Wait for your pull request to be merged. If your pull request is accepted, the changes will be included in the next release.

To see the latest stable version, please checkout to the [main](https://github.com/RyanLi1014-maker/CLI-Toolkit/tree/main) branch.

To see the latest changes, please checkout to the [develop](https://github.com/RyanLi1014-maker/CLI-Toolkit/tree/develop) branch.

# License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
