# CLI-Toolkit

<div align="center">

**A compact and powerful command-line toolkit with an extensible plugin system**

[![Python Version](https://img.shields.io/badge/python-≥3.14-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Package Manager](https://img.shields.io/badge/package%20manager-uv-orange.svg)](https://github.com/astral-sh/uv)

</div>

---

## 📖 Overview

CLI-Toolkit is a flexible, modular command-line interface application designed to bring order to your scripts and utilities. Instead of scattering code across multiple files in a chaotic directory structure, CLI-Toolkit provides a clean architecture with an intuitive plugin system that makes organizing and accessing your tools effortless.

### ✨ Why CLI-Toolkit?

- **Eliminate Chaos**: Say goodbye to disorganized script collections
- **Intuitive Interface**: Beautiful colored output and user-friendly commands
- **Extensible Design**: Add functionality through simple plugins with minimal code
- **Modular Architecture**: Clean separation between core functionality and extensions

---

## 🚀 Features

- **🎨 Rich Terminal Output**: Colored, formatted console output for enhanced readability
- **⌨️ Interactive CLI**: User-friendly command loop with help system
- **🔌 Dynamic Plugin System**: Load, unload, and manage plugins at runtime
- **📦 Modular Architecture**: Clean separation of concerns between core and plugins
- **⚙️ Configuration Management**: Built-in support for plugin configuration storage
- **📝 Logging Integration**: Comprehensive logging for debugging and monitoring
- **✨ Magic Variables**: Resolve `${cwd}` and other placeholders in command arguments
- **🐚 Shell Integration**: Run external commands with the built-in `run` command
- **🛡️ Type Safety**: Modern Python with type hints and static analysis

---

## 📋 Prerequisites

Before installing CLI-Toolkit, ensure you have:

- **Python ≥ 3.14** installed on your system
- **[uv](https://github.com/astral-sh/uv)** package manager installed

Install `uv` by following the [official installation guide](https://github.com/astral-sh/uv).

---

## 🛠️ Installation

### Executable Version (Recommended)

The easiest way to get started is by downloading the executable for your platform from the [Releases](https://github.com/RyanLi1014-maker/CLI-Toolkit/releases).

1. Download the executable for your OS.
2. Place it in a convenient folder.
3. Run the downloaded executable.

On first launch, CLI-Toolkit initializes itself and creates runtime support directories under `_internal`.

- The executable version stores generated runtime data in `_internal/`
- Plugin folder and runtime folders are created there automatically
- You can inspect `_internal/plugin/` to add or manage plugins manually

Example:

```bash
# Windows
CLI-Toolkit.exe

# macOS / Linux (if built for the platform)
./CLI-Toolkit
```

> If you are using the executable version, open the generated `_internal` folder to find runtime directories such as `plugin/`, `config/`, and other support folders.

### Source Code Version

If you prefer to run CLI-Toolkit from source, or if you want to inspect and customize the code, follow these steps:

1. Download the source code from [Releases](https://github.com/RyanLi1014-maker/CLI-Toolkit/releases) or clone the repository:

   ```bash
   git clone https://github.com/RyanLi1014-maker/CLI-Toolkit.git
   ```

2. Navigate to the project directory:

   ```bash
   cd CLI-Toolkit
   ```

3. Install dependencies and set up the environment using `uv`:

   ```bash
   uv sync
   ```

4. Run CLI-Toolkit from source:

   ```bash
   uv run main.py
   ```

The source version keeps plugin files and configuration folders next to the project root, making it easier to develop and customize CLI-Toolkit.

---

## 🎯 Quick Start

### Running the Application

If you are using the executable version, simply run the downloaded executable. Otherwise, cd into the project directory and start CLI-Toolkit with:

```bash
uv run main.py
```

You'll see the welcome screen:

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

────────────────────────────────────────────────────────────────────────────────────────────────
Welcome to CLI-Toolkit! Type `help` for a list of available commands.
CLI-Toolkit>
```

### Basic Commands

Once inside the CLI:

- **List all commands**:

  ```
  CLI-Toolkit> help
  ```

- **Get detailed help for a specific command**:

  ```
  CLI-Toolkit> help <command_name>
  ```

- **Check version information**:

  ```
  CLI-Toolkit> version
  ```

- **Print text or magic variables**:

  ```
  CLI-Toolkit> echo hello world
  CLI-Toolkit> echo ${cwd}
  ```

- **Run a shell command**:

  ```
  CLI-Toolkit> run echo hello
  ```

- **Manage plugins** (load, unload, reload, enable, disable):

  ```
  CLI-Toolkit> plugin load my_plugin
  ```

- **View or change configuration**:

  ```
  CLI-Toolkit> config
  ```

- **Create command aliases**:

  ```
  CLI-Toolkit> alias create ll run ls -la
  ```

- **Clear the screen**:

  ```
  CLI-Toolkit> clear
  ```

- **Exit the application**:

  ```
  CLI-Toolkit> exit
  ```

  Or press **Ctrl+C** twice within 2 seconds. A single **Ctrl+C** cancels the current command and returns to the prompt.

### Magic Variables

CLI-Toolkit supports **magic variables** in command arguments. These are placeholders written as `${variable_name}` that are automatically resolved to dynamic values before the command executes.

Currently supported magic variables:

- **`${cwd}`**: Resolves to the absolute path of the current working directory. Useful for passing the working directory to plugin commands or built-in commands that accept paths.

Any unrecognized magic variable (e.g., `${unknown}`) is passed through as the variable name itself.

Example:

```
CLI-Toolkit> echo ${cwd} ${unknown}
```

The output would be:

```
D:\Data\Projects\CLI-Toolkit
unknown
```

---

## 🔌 Plugin System

The heart of CLI-Toolkit is its powerful yet simple plugin system. Plugins extend functionality without modifying core code.

### Installing Plugins

1. **Run the application to create the plugin directory** (automatically created on first run)
2. **Place your plugin file** in the `plugin/` directory:

   ```
   plugin/
   └── my_plugin.py
   ```

   If you are using the executable version, this directory is created under `_internal/plugin/`.

3. **Load the plugin** from within CLI-Toolkit:

   ```
   CLI-Toolkit> plugin load my_plugin
   ```

   For plugins with spaces in their name:

   ```
   CLI-Toolkit> plugin load "my plugin"
   ```

4. **View available commands**:
   ```
   CLI-Toolkit> help
   ```

Your plugin commands are now available alongside built-in commands!

### Developing Plugins

Creating a plugin is straightforward. Drop a Python file in the `plugin/` directory with a class that inherits from `BasePlugin` and methods starting with `cmd_`:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """My awesome plugin."""

    def cmd_hello(self, args):
        """Say hello."""
        self.console.print("Hello from my plugin!", style="bold green")
```

That's it! Each `cmd_<name>` method automatically becomes a `<name>` command.

#### Key Plugin Features

- **Rich Console Output**: Use `self.console.print()` for styled messages
- **Logging**: Access plugin-specific logger via `self.logger`
- **Configuration**: Save/load settings with `DictConfig`
- **Version Tracking**: Register plugin versions with the `VERSION` attribute
- **App Integration**: Access the main application through `self.master`

For comprehensive plugin development guidance, see [Plugin Development Documentation](doc/plugin_development_guide.md).

---

## 📦 Manual Package Installation

Some plugins may require external Python packages that are not included in the main project dependencies. You can manually download these packages from PyPI and place them in the `package/` directory for your plugins to import.

> **For executable users**: The `package/` directory is located inside the `_internal` folder (e.g., `_internal/package/`). When following the instructions below, replace all references to the `package/` directory with `_internal/package/` — or `cd` into `_internal` first so that `./package` resolves correctly.

### Why Use the `package/` Directory?

- **Plugin Isolation**: Keep plugin-specific dependencies separate from core dependencies
- **Customizable**: Choose which packages to download and even create your own for your plugin
- **Executable Support**: Allows you to download packages for CLI-Toolkit Executable

### Method 1: Using `uv` (recommended)

You can download packages using `uv`:

1. **Install `uv`**: Go to the `uv` [repository](https://github.com/astral-sh/uv) and follow the installation instructions.
2. **Run CLI-Toolkit**: Run CLI-Toolkit firstly to create the `package/` directory.
3. **Go to the project directory**: `cd` into the CLI-Toolkit directory.
4. **Download Packages**: Run the following command in the terminal:

   ```bash
   # Download a package to the package directory
   uv pip install <package_name> --target ./package

   # Example: Download the 'requests' package
   uv pip install requests --target ./package
   ```

   **For multiple packages:**

   ```bash
   uv pip install package1 package2 package3 --target ./package
   ```

### Method 2: Using PyPI Website

You can also download packages directly from [PyPI](https://pypi.org/):

1. **Visit PyPI**: Go to [PyPI](https://pypi.org/) and search for the package you want

2. **Download the wheel or source file**:
   - Look for the "Download files" section
   - Choose the appropriate file for your platform:
     - `.whl` files (wheels) are preferred for faster installation
     - `.tar.gz` files are source distributions

3. **Install the package**:
   - For `.whl` files, run following command in the terminal:
     ```bash
     uv pip install your_package.whl --target ./package
     ```
   - For `.tar.gz` files, unzip the file and place the whole folder in the `package/` directory.

### Using Packages in Plugins

Once packages are in the `package/` directory, they will be automatically available for import in your plugins:

```python
from api import BasePlugin
import requests  # This works if requests is in package/ directory


class Plugin(BasePlugin):
    """Plugin that uses external packages."""

    def cmd_fetch(self, args):
        """Fetch data using requests library."""
        response = requests.get("https://api.example.com")
        self.console.print(f"Status: {response.status_code}", style="green")
```

### Important Notes

⚠️ **Platform Compatibility**: Ensure downloaded packages match your operating system and Python version. Wheels built for Linux won't work on Windows, and vice versa.

⚠️ **Version Conflicts**: Be careful about version conflicts between packages in the `package/` directory and those installed via `uv sync`.

⚠️ **Priority**: Packages that are already included in the project dependencies such as `rich` will be given priority for import.

💡 **Best Practice**: Document any external packages your plugin requires in the plugin's docstring or comments so users know what to install.

### Checking Installed Packages

To see what's currently in your package directory (for the executable version, run this inside `_internal`):

```bash
ls package/      # On Linux/Mac
dir package\     # On Windows
```

### Removing Packages

If you need to remove a package from the `package/` directory (for the executable version, `_internal/package/`):

**Using command line:**

```bash
# Remove a specific package file
rm package/<package_filename>          # On Linux/Mac
del package\<package_filename>         # On Windows

# Example: Remove requests package
rm package/requests-2.31.0-py3-none-any.whl    # On Linux/Mac
del package\requests-2.31.0-py3-none-any.whl   # On Windows
```

**Using file explorer:**

- Navigate to the `package/` directory (for the executable version, open `_internal/package/`)
- Select the package file(s) you want to remove
- Delete them using your system's standard delete operation

⚠️ **Caution**: Before removing a package, ensure that no active plugins depend on it. Removing a required package may cause plugin errors.

💡 **Tip**: If you're unsure which plugins use a package, check the plugin source code for import statements or refer to the plugin documentation.

---

## 🧪 Development

### Code Quality

CLI-Toolkit uses [Ruff](https://github.com/astral-sh/ruff) for linting and code quality. The project enforces:

- **ARG**: Unused argument detection
- **B**: Bugbear checks
- **C4**: Comprehension rules
- **D**: Docstring conventions
- **E/F**: PEP8 errors and warnings
- **G**: Logging format strings
- **I**: Import sorting
- **LOG**: Logging best practices
- **PTH**: Pathlib usage
- **SIM**: Simplify code
- **UP**: Pyupgrade rules
- **W**: PEP8 warnings

### Dependencies

Core runtime dependencies (defined in `pyproject.toml`):

| Package                                    | Purpose                                       |
| ------------------------------------------ | --------------------------------------------- |
| [rich](https://github.com/Textualize/rich) | Terminal formatting and plugin console output |

### Adding Dependencies

Edit `pyproject.toml` and run:

```bash
uv sync
```

---

## 📚 Documentation

- **[Plugin Development Guide](doc/plugin_development_guide.md)**: Complete tutorial for creating plugins
- **[Source Code](src/)**: Well-documented source with type hints

---

## 🔄 Version Information

- **Stable releases**: Check the [main branch](https://github.com/RyanLi1014-maker/CLI-Toolkit/tree/main)
- **Latest changes**: Check the [develop branch](https://github.com/RyanLi1014-maker/CLI-Toolkit/tree/develop)
- **Current version**: See `pyproject.toml` or use the `version` command

---

## 🤝 Contributing

Contributions are welcome! Whether it's:

- 🐛 Bug reports
- 💡 Feature requests
- 📝 Documentation improvements
- 🔧 Code contributions

Please feel free to open issues or submit pull requests.

---

## 📄 License

This project is licensed under the **MIT License**. See the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **[rich](https://github.com/Textualize/rich)**: Beautiful terminal formatting
- **[uv](https://github.com/astral-sh/uv)**: Fast Python package installer and resolver

---

<div align="center">

**Made with ❤️ by [RyanLi1014-maker](https://github.com/RyanLi1014-maker)**

</div>
