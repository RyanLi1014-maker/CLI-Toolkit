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
- **🔌 Dynamic Plugin System**: Load, unload, and manage plugins at runtime
- **📦 Modular Architecture**: Clean separation of concerns between core and plugins
- **⚙️ Configuration Management**: Built-in support for plugin configuration storage
- **📝 Logging Integration**: Comprehensive logging for debugging and monitoring
- **💬 Interactive CLI**: User-friendly command prompt with help system
- **🛡️ Type Safety**: Modern Python with type hints and static analysis

---

## 📋 Prerequisites

Before installing CLI-Toolkit, ensure you have:

- **Python ≥ 3.14** installed on your system
- **[uv](https://github.com/astral-sh/uv)** package manager installed

Install `uv` by following the [official installation guide](https://github.com/astral-sh/uv).

---

## 🛠️ Installation

1. **Download the source code** from [Releases](https://github.com/RyanLi1014-maker/CLI-Toolkit/releases):
   - Download the latest release archive (e.g., `CLI-Toolkit-v0.3.0.zip`)
   - Extract it to your desired location

2. **Navigate to the project directory**:

   ```bash
   cd CLI-Toolkit
   ```

3. **Install dependencies and set up the environment** using `uv`:
   ```bash
   uv sync
   ```

That's it! CLI-Toolkit is now ready to use.

---

## 🎯 Quick Start

### Running the Application

Start CLI-Toolkit with:

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

- **Exit the application**:
  ```
  CLI-Toolkit> exit
  ```

---

## 🔌 Plugin System

The heart of CLI-Toolkit is its powerful yet simple plugin system. Plugins extend functionality without modifying core code.

### Installing Plugins

1. **Create the plugin directory** (automatically created on first run):

   ```bash
   uv run main.py  # Run once to initialize
   ```

2. **Place your plugin file** in the `plugin/` directory:

   ```
   plugin/
   └── my_plugin.py
   ```

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

Creating a plugin is straightforward. Create a Python file in the `plugin/` directory:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """My awesome plugin."""

    VERSION = (1, 0, 0)  # Optional version number

    def cmd_hello(self, args):
        """Say hello."""
        self.console.print("Hello from my plugin!", style="bold green")

        if args:
            self.console.print(f"Arguments received: {args}")
```

That's it! The method `cmd_hello` automatically becomes the `hello` command.

#### Key Plugin Features

- **Rich Console Output**: Use `self.console.print()` for styled messages
- **Logging**: Access plugin-specific logger via `self.logger`
- **Configuration**: Save/load settings with `DictConfig`
- **Version Tracking**: Register plugin versions with the `VERSION` attribute
- **App Integration**: Access the main application through `self.master`

For comprehensive plugin development guidance, see [Plugin Development Documentation](doc/Plugin%20development.md).

---

## 🧪 Development

### Code Quality

CLI-Toolkit uses [Ruff](https://github.com/astral-sh/ruff) for linting and code quality. The project enforces:

- **B**: Bugbear checks
- **C4**: Comprehension rules
- **D**: Docstring conventions
- **E/F**: PEP8 errors and warnings
- **I**: Import sorting
- **PTH**: Pathlib usage
- **SIM**: Simplify code
- **UP**: Pyupgrade rules
- **W**: PEP8 warnings

### Adding Dependencies

Edit `pyproject.toml` and run:

```bash
uv sync
```

---

## 📚 Documentation

- **[Plugin Development Guide](doc/Plugin%20development.md)**: Complete tutorial for creating plugins
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
