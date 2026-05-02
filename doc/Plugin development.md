# Plugin Development Guide

CLI-Toolkit features a powerful plugin system that allows you to extend functionality with minimal effort. This guide walks you through everything from basic plugin creation to advanced integration patterns.

## Table of Contents

- [Plugin Development Guide](#plugin-development-guide)
  - [Table of Contents](#table-of-contents)
- [Quick Start](#quick-start)
  - [Plugin Structure](#plugin-structure)
  - [Your First Plugin](#your-first-plugin)
- [Core Concepts](#core-concepts)
  - [Command Registration](#command-registration)
    - [Method Naming Rules](#method-naming-rules)
    - [Docstrings as Help Text](#docstrings-as-help-text)
  - [Handling Arguments](#handling-arguments)
  - [Plugin Versioning](#plugin-versioning)
- [Output \& Logging](#output--logging)
  - [Console Output](#console-output)
    - [Basic Styling](#basic-styling)
    - [Common Style Options](#common-style-options)
    - [Advanced Formatting](#advanced-formatting)
  - [Logging System](#logging-system)
    - [Log Levels](#log-levels)
    - [Logger Naming](#logger-naming)
    - [Best Practices](#best-practices)
- [Configuration Management](#configuration-management)
  - [Dictionary Configuration](#dictionary-configuration)
    - [Path Resolution](#path-resolution)
    - [Nested Data Support](#nested-data-support)
    - [Validation Modes](#validation-modes)
  - [List Configuration](#list-configuration)
    - [List Operations](#list-operations)
  - [Set Configuration](#set-configuration)
    - [Set Operations](#set-operations)
  - [Configuration Best Practices](#configuration-best-practices)
    - [Auto-Loading Control](#auto-loading-control)
    - [Error Handling](#error-handling)
- [Advanced Integration](#advanced-integration)
  - [Custom Initialization](#custom-initialization)
  - [Accessing Main Application](#accessing-main-application)
    - [Available Master Attributes](#available-master-attributes)
  - [Plugin Lifecycle](#plugin-lifecycle)
    - [Loading Phase](#loading-phase)
    - [Execution Phase](#execution-phase)
    - [Unloading Phase](#unloading-phase)
    - [Manual Cleanup Example](#manual-cleanup-example)
- [Best Practices](#best-practices-1)
  - [Error Handling](#error-handling-1)
  - [Code Organization](#code-organization)
  - [Documentation Standards](#documentation-standards)
- [Complete Example](#complete-example)
- [Troubleshooting](#troubleshooting)
  - [Common Issues](#common-issues)
    - [Plugin Not Loading](#plugin-not-loading)
    - [Commands Not Recognized](#commands-not-recognized)
    - [Configuration Errors](#configuration-errors)
    - [Import Errors](#import-errors)
  - [Getting Help](#getting-help)

---

# Quick Start

## Plugin Structure

Plugins are Python files placed in the `plugin/` directory at the project root. The filename (without `.py`) becomes your plugin's identifier. If the directory doesn't exist, it will be created automatically when you first run CLI-Toolkit.

**File Location:** `plugin/my_plugin.py`  
**Plugin Name:** `my_plugin`

## Your First Plugin

Every plugin must define a class named `Plugin` that inherits from `BasePlugin`. Command methods start with the prefix `cmd_`:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """A simple example plugin."""

    def cmd_hello(self, _):
        """Say hello to the user."""
        self.console.print("Hello from my plugin!")
```

**Key Points:**

- Import `BasePlugin` from the `api` module
- Class name **must** be `Plugin`
- Command methods **must** start with `cmd_`
- The `_` parameter receives command arguments (ignored here)

To use this command after loading the plugin, type:

```
hello
```

---

# Core Concepts

## Command Registration

Commands are automatically discovered based on method naming conventions. Any method starting with `cmd_` becomes an available command.

### Method Naming Rules

| Method Name     | Command Name | Description           |
| --------------- | ------------ | --------------------- |
| `cmd_greet`     | `greet`      | Simple command        |
| `cmd_add_user`  | `add_user`   | Underscores preserved |
| `cmd_show_info` | `show_info`  | Multi-word commands   |

### Docstrings as Help Text

Method docstrings serve as command descriptions displayed by the help system:

```python
def cmd_calculate(self, args):
    """Perform mathematical calculations on provided numbers."""
    # This docstring appears in help output
    pass
```

## Handling Arguments

All command methods receive an `args` parameter containing a list of strings passed by the user:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Plugin demonstrating argument handling."""

    def cmd_greet(self, args):
        """Greet someone by name. Usage: greet <name>"""
        if not args:
            self.console.print("Please provide a name!", style="red")
            return

        name = args[0]
        self.console.print(f"Hello, {name}!", style="green")

    def cmd_multiply(self, args):
        """Multiply two numbers. Usage: multiply <num1> <num2>"""
        if len(args) < 2:
            self.console.print("Usage: multiply <num1> <num2>", style="yellow")
            return

        try:
            result = float(args[0]) * float(args[1])
            self.console.print(f"Result: {result}")
        except ValueError:
            self.console.print("Both arguments must be numbers!", style="red")
```

**Argument Behavior:**

- `args` is always a list of strings
- Empty list `[]` if no arguments provided
- Arguments separated by spaces
- Quoted strings preserve spaces: `"hello world"` → single argument

## Plugin Versioning

Define a `VERSION` attribute to track your plugin version:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Versioned plugin example."""

    VERSION = (1, 2, 3)  # Semantic versioning: major.minor.patch

    def cmd_status(self, _):
        """Show plugin status."""
        version_str = ".".join(map(str, self.VERSION))
        self.console.print(f"MyPlugin v{version_str}")
```

**Version Format:**

- Tuple of three integers: `(major, minor, patch)`
- Displayed by the `version` command
- Defaults to `(0, 0, 0)` if not specified

**Semantic Versioning Guidelines:**

- **Major**: Breaking changes
- **Minor**: New features (backward compatible)
- **Patch**: Bug fixes only

---

# Output & Logging

## Console Output

CLI-Toolkit uses the Rich library for formatted console output. Access it via `self.console.print()`:

### Basic Styling

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Console styling examples."""

    def cmd_demo(self, _):
        """Demonstrate various output styles."""

        # Simple text
        self.console.print("Plain text message")

        # Colored text
        self.console.print("Error occurred", style="red")
        self.console.print("Success!", style="green")
        self.console.print("Warning", style="yellow")
        self.console.print("Information", style="blue")

        # Combined styles
        self.console.print("Bold red text", style="bold red")
        self.console.print("Italic blue", style="italic blue")
        self.console.print("Underlined green", style="underline green")

        # Inline markup
        self.console.print("This has [bold]bold[/bold] and [red]red[/red] text")
        self.console.print("Nested: [blue]Blue with [bold]bold inside[/bold][/blue]")
```

### Common Style Options

| Style        | Description                                                  | Example              |
| ------------ | ------------------------------------------------------------ | -------------------- |
| Colors       | `red`, `green`, `blue`, `yellow`, `magenta`, `cyan`, `white` | `style="red"`        |
| Modifiers    | `bold`, `italic`, `underline`, `strike`                      | `style="bold"`       |
| Combinations | Space-separated                                              | `style="bold green"` |
| Background   | Prefix with `on_`                                            | `style="on_red"`     |

### Advanced Formatting

```python
def cmd_report(self, _):
    """Display a formatted report."""

    # Tables and structured data
    self.console.print("[bold]System Report[/bold]")
    self.console.print("=" * 40)
    self.console.print(f"{'Component':<20} {'Status':<10}")
    self.console.print("-" * 40)
    self.console.print(f"{'Database':<20} {'OK':<10}", style="green")
    self.console.print(f"{'Cache':<20} {'WARNING':<10}", style="yellow")
    self.console.print(f"{'API':<20} {'ERROR':<10}", style="red")
```

**For complete Rich documentation, visit:** [https://rich.readthedocs.io/](https://rich.readthedocs.io/)

## Logging System

Each plugin gets its own logger instance for debugging and error tracking:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Logging demonstration."""

    def cmd_process(self, _):
        """Process data with logging."""

        # Different log levels
        self.logger.debug("Detailed debug information")
        self.logger.info("General information message")
        self.logger.warning("Something unexpected happened")
        self.logger.error("An error occurred")
        self.logger.critical("Critical failure!")
```

### Log Levels

| Level      | Use Case                      | File Output           |
| ---------- | ----------------------------- | --------------------- |
| `DEBUG`    | Detailed diagnostic info      | Only if debug enabled |
| `INFO`     | General operational messages  | Yes                   |
| `WARNING`  | Unexpected but handled issues | Yes                   |
| `ERROR`    | Error conditions              | Yes                   |
| `CRITICAL` | Severe failures               | Yes                   |

### Logger Naming

Loggers are automatically named after your plugin file:

- Plugin file: `my_plugin.py`
- Logger name: `Plugin.my_plugin`

This makes it easy to filter logs by plugin in log files.

### Best Practices

```python
def cmd_risky_operation(self, args):
    """Example of proper logging usage."""

    if not args:
        self.logger.warning("Operation called without arguments")
        self.console.print("Missing arguments", style="yellow")
        return

    try:
        self.logger.info(f"Processing: {args[0]}")
        # ... perform operation ...
        self.logger.debug("Operation completed successfully")

    except Exception as e:
        self.logger.error(f"Operation failed: {str(e)}", exc_info=True)
        self.console.print(f"Failed: {e}", style="red")
```

**Tips:**

- Use `exc_info=True` to include stack traces in error logs
- Log before critical operations for debugging
- Include context in log messages (variable values, state)
- Don't log sensitive information (passwords, tokens)

---

# Configuration Management

CLI-Toolkit provides three configuration classes for persistent storage. All configs are stored as JSON files in the `config/` directory.

## Dictionary Configuration

Use `DictConfig` for key-value pairs and nested structures:

```python
from pathlib import Path
from api import BasePlugin
from util.config import DictConfig


class Plugin(BasePlugin):
    """Plugin with dictionary configuration."""

    def __init__(self, master):
        """Initialize plugin with configuration."""
        super().__init__(master)
        self.master = master

        # Define configuration with defaults
        self.config = DictConfig(
            config_path=Path("my_plugin.json"),
            default_config={
                "username": "default_user",
                "timeout": 30,
                "features": {
                    "notifications": True,
                    "auto_save": False
                },
                "tags": ["important", "urgent"]
            }
        )

    def cmd_show_settings(self, _):
        """Display current configuration."""
        self.console.print("[bold]Current Settings:[/bold]")
        for key, value in self.config.items():
            self.console.print(f"  {key}: {value}")

    def cmd_set_username(self, args):
        """Set username. Usage: set_username <name>"""
        if not args:
            self.console.print("Usage: set_username <name>", style="yellow")
            return

        self.config["username"] = args[0]
        self.config.save()
        self.console.print(f"Username set to: {args[0]}", style="green")
```

### Path Resolution

The `config_path` parameter automatically prepends `config/`:

```python
Path("my_plugin.json")  # → config/my_plugin.json
```

### Nested Data Support

```python
# Access nested values
notification_enabled = self.config["features"]["notifications"]

# Modify nested values
self.config["features"]["auto_save"] = True
self.config.save()

# Add new keys (if structure validation disabled)
self.config["new_setting"] = "value"
```

### Validation Modes

```python
# Strict validation (recommended for production)
self.config = DictConfig(
    config_path=Path("settings.json"),
    default_config={"key": "value"},
    validate_structure=True  # Reject unknown keys
)

# Flexible validation (development mode)
self.config = DictConfig(
    config_path=Path("settings.json"),
    default_config={"key": "value"},
    validate_structure=False  # Allow extra keys
)
```

**Validation Behavior:**

- **Type checking**: Always enforced
- **Structure validation**: Optional (controlled by `validate_structure`)
- **Invalid values**: Replaced with defaults (partial replacement, not full reset)
- **Missing keys**: Filled with default values
- **Extra keys**: Kept if validation disabled, removed if enabled

## List Configuration

Use `ListConfig` for ordered collections:

```python
from pathlib import Path
from api import BasePlugin
from util.config import ListConfig


class Plugin(BasePlugin):
    """Plugin with list configuration."""

    def __init__(self, master):
        """Initialize with list config."""
        super().__init__(master)
        self.master = master

        self.history = ListConfig(
            config_path=Path("command_history.json"),
            default_config=[
                "initial_command",
                "setup_complete"
            ]
        )

    def cmd_add_history(self, args):
        """Add entry to history. Usage: add_history <entry>"""
        if not args:
            self.console.print("Usage: add_history <entry>", style="yellow")
            return

        self.history.append(args[0])
        self.history.save()
        self.console.print(f"Added: {args[0]}", style="green")

    def cmd_show_history(self, _):
        """Display command history."""
        self.console.print("[bold]History:[/bold]")
        for i, entry in enumerate(self.history, 1):
            self.console.print(f"  {i}. {entry}")
```

### List Operations

```python
# Standard list methods work
self.history.append("new_item")
self.history.extend(["item1", "item2"])
self.history.insert(0, "first_item")
removed = self.history.pop()
```

## Set Configuration

Use `SetConfig` for unique collections:

```python
from pathlib import Path
from api import BasePlugin
from util.config import SetConfig


class Plugin(BasePlugin):
    """Plugin with set configuration."""

    def __init__(self, master):
        """Initialize with set config."""
        super().__init__(master)
        self.master = master

        self.allowed_users = SetConfig(
            config_path=Path("allowed_users.json"),
            default_config={"admin", "moderator"}
        )

    def cmd_add_user(self, args):
        """Add user to allowed list. Usage: add_user <username>"""
        if not args:
            self.console.print("Usage: add_user <username>", style="yellow")
            return

        self.allowed_users.add(args[0])
        self.allowed_users.save()
        self.console.print(f"User added: {args[0]}", style="green")

    def cmd_list_users(self, _):
        """List allowed users."""
        self.console.print("[bold]Allowed Users:[/bold]")
        for user in sorted(self.allowed_users):
            self.console.print(f"  • {user}")
```

### Set Operations

```python
# Standard set methods work
self.allowed_users.add("new_user")
self.allowed_users.update(["user1", "user2"])
self.allowed_users.discard("old_user")
is_member = "admin" in self.allowed_users
```

## Configuration Best Practices

### Auto-Loading Control

```python
# Disable auto-load for custom initialization
self.config = DictConfig(
    config_path=Path("settings.json"),
    default_config={"key": "value"},
    auto_load=False  # Manual control
)

# Load manually when ready
self.config.load()
```

### Error Handling

```python
def cmd_update_config(self, args):
    """Safely update configuration."""
    try:
        if len(args) >= 2:
            key, value = args[0], args[1]
            self.config[key] = value
            self.config.save()
            self.console.print("Configuration updated", style="green")
        else:
            self.console.print("Usage: update_config <key> <value>", style="red")

    except Exception as e:
        self.logger.error(f"Config update failed: {e}")
        self.console.print("Failed to update configuration", style="red")
```

---

# Advanced Integration

## Custom Initialization

Override `__init__` to set up resources when the plugin loads:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Plugin with custom initialization."""

    def __init__(self, master):
        """Initialize plugin resources."""
        super().__init__(master)
        self.master = master

        # Store application reference
        self.app_version = self.APP_VERSION

        # Initialize resources
        self.connection_pool = []
        self.cache = {}

        self.console.print("[green]Plugin initialized successfully[/green]")
        self.logger.info("Plugin loaded and ready")

    def cmd_status(self, _):
        """Show plugin status."""
        self.console.print(f"App Version: {self.app_version}")
        self.console.print(f"Connections: {len(self.connection_pool)}")
        self.console.print(f"Cache Size: {len(self.cache)}")
```

**Initialization Checklist:**

- ✅ Call `super().__init__(master)` first
- ✅ Store `master` reference if needed
- ✅ Initialize instance variables
- ✅ Set up external connections
- ✅ Load configurations
- ✅ Log initialization status

## Accessing Main Application

The `master` parameter provides access to core application components:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Plugin accessing main application."""

    def __init__(self, master):
        """Store application reference."""
        super().__init__(master)
        self.master = master

    def cmd_app_info(self, _):
        """Display application information."""

        # Access application version
        app_version = self.master.VERSION
        self.console.print(f"App Version: {app_version}")

        # Access shared console
        self.console.print("Using shared console")

        # Access application logger
        self.master.logger.info("Plugin requesting app info")

        # Access plugin manager
        plugin_count = len(self.master.plugin_manager.plugins)
        self.console.print(f"Loaded Plugins: {plugin_count}")

        # Access global configuration
        if hasattr(self.master, 'config'):
            self.console.print("Global config available")
```

### Available Master Attributes

| Attribute        | Type          | Description                      |
| ---------------- | ------------- | -------------------------------- |
| `VERSION`        | tuple         | Application version              |
| `console`        | Console       | Rich console instance            |
| `logger`         | Logger        | Application logger               |
| `plugin_manager` | PluginManager | Plugin management                |
| `config`         | dict          | Global configuration (if exists) |

## Plugin Lifecycle

Understanding when plugin code executes:

### Loading Phase

1. Plugin file discovered in `plugin/` directory
2. Module imported dynamically
3. `Plugin` class instantiated with `master` reference
4. `__init__` method called
5. Commands registered automatically

### Execution Phase

- User types command name
- Corresponding `cmd_*` method invoked
- Arguments passed as string list
- Method executes and returns

### Unloading Phase

- Plugin removed from registry
- No automatic cleanup (implement manually if needed)

### Manual Cleanup Example

```python
class Plugin(BasePlugin):
    """Plugin with resource cleanup."""

    def __init__(self, master):
        """Initialize resources."""
        super().__init__(master)
        self.master = master
        self.database_connection = None
        self._connect_to_database()

    def _connect_to_database(self):
        """Establish database connection."""
        try:
            # Simulated connection
            self.database_connection = {"status": "connected"}
            self.logger.info("Database connected")
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")

    def cmd_disconnect(self, _):
        """Manually disconnect from database."""
        if self.database_connection:
            self.database_connection = None
            self.logger.info("Database disconnected")
            self.console.print("Disconnected", style="green")
```

---

# Best Practices

## Error Handling

Always handle potential errors gracefully:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """Robust error handling example."""

    def cmd_safe_operation(self, args):
        """Perform operation with error handling."""

        # Validate input
        if not args:
            self.console.print("No arguments provided", style="yellow")
            self.logger.warning("Command called without arguments")
            return

        try:
            # Attempt operation
            result = self._process_data(args[0])
            self.console.print(f"Success: {result}", style="green")
            self.logger.info(f"Processed: {args[0]}")

        except FileNotFoundError:
            self.console.print("File not found", style="red")
            self.logger.error(f"File missing: {args[0]}")

        except PermissionError:
            self.console.print("Permission denied", style="red")
            self.logger.error(f"Access denied: {args[0]}")

        except Exception as e:
            self.console.print(f"Unexpected error: {e}", style="red")
            self.logger.error(f"Unhandled exception: {e}", exc_info=True)

    def _process_data(self, data):
        """Internal processing logic."""
        # Implementation details
        return f"processed_{data}"
```

**Error Handling Principles:**

- Validate inputs early
- Catch specific exceptions first
- Provide user-friendly messages
- Log detailed error information
- Never expose raw tracebacks to users
- Use `exc_info=True` for debugging

## Code Organization

Structure complex plugins effectively:

```python
from pathlib import Path
from api import BasePlugin
from util.config import DictConfig


class Plugin(BasePlugin):
    """Well-organized plugin example."""

    VERSION = (1, 0, 0)

    def __init__(self, master):
        """Initialize plugin."""
        super().__init__(master)
        self.master = master
        self._load_configuration()

    def _load_configuration(self):
        """Load plugin configuration."""
        self.config = DictConfig(
            config_path=Path("advanced_plugin.json"),
            default_config={
                "max_retries": 3,
                "timeout": 30,
                "output_format": "json"
            }
        )

    # ─── Public Commands ──────────────────────────────

    def cmd_fetch(self, args):
        """Fetch data from source. Usage: fetch <url>"""
        if not args:
            self.console.print("Usage: fetch <url>", style="yellow")
            return

        url = args[0]
        self._execute_fetch(url)

    def cmd_configure(self, args):
        """Update configuration. Usage: configure <key> <value>"""
        if len(args) < 2:
            self.console.print("Usage: configure <key> <value>", style="yellow")
            return

        self._update_config(args[0], args[1])

    # ─── Private Methods ──────────────────────────────

    def _execute_fetch(self, url):
        """Execute data fetch operation."""
        self.logger.info(f"Fetching: {url}")
        # Implementation...

    def _update_config(self, key, value):
        """Update configuration value."""
        if key in self.config:
            self.config[key] = value
            self.config.save()
            self.console.print(f"Updated: {key} = {value}", style="green")
        else:
            self.console.print(f"Unknown setting: {key}", style="red")
```

**Organization Tips:**

- Group related methods together
- Use private methods (prefix `_`) for internal logic
- Separate public commands from helpers
- Keep methods focused and small
- Use descriptive names

## Documentation Standards

Document your plugin thoroughly:

```python
from api import BasePlugin


class Plugin(BasePlugin):
    """DataProcessor Plugin v1.0

    Provides commands for processing and transforming data files.
    Supports CSV, JSON, and XML formats.

    Commands:
        - process: Process a data file
        - convert: Convert between formats
        - validate: Check data integrity
    """

    VERSION = (1, 0, 0)

    def cmd_process(self, args):
        """Process a data file.

        Usage: process <file_path> [options]

        Arguments:
            file_path: Path to the data file
            options: Optional processing flags (--verbose, --strict)

        Examples:
            process data.csv
            process data.json --verbose
        """
        # Implementation...
```

**Documentation Guidelines:**

- Write clear class docstrings
- Document each command with usage examples
- Explain arguments and options
- Include practical examples
- Update docs when changing behavior

---

# Complete Example

Here's a comprehensive plugin combining all concepts:

```python
"""Task Manager Plugin - Manage tasks from the command line."""

from pathlib import Path
from datetime import datetime
from api import BasePlugin
from util.config import DictConfig


class Plugin(BasePlugin):
    """Task Manager Plugin

    A simple task management system with persistence.
    Tasks can be added, listed, completed, and removed.

    Commands:
        - add_task: Add a new task
        - list_tasks: Show all tasks
        - complete: Mark task as done
        - remove: Delete a task
        - stats: Show task statistics
    """

    VERSION = (1, 0, 0)

    def __init__(self, master):
        """Initialize task manager."""
        super().__init__(master)
        self.master = master

        # Load task configuration
        self.tasks_config = DictConfig(
            config_path=Path("tasks.json"),
            default_config={
                "tasks": [],
                "last_updated": None
            }
        )

        self.logger.info("Task Manager Plugin initialized")

    def cmd_add_task(self, args):
        """Add a new task. Usage: add_task <description>"""
        if not args:
            self.console.print("Usage: add_task <description>", style="yellow")
            return

        description = " ".join(args)
        task = {
            "id": len(self.tasks_config["tasks"]) + 1,
            "description": description,
            "created": datetime.now().isoformat(),
            "completed": False
        }

        self.tasks_config["tasks"].append(task)
        self.tasks_config["last_updated"] = datetime.now().isoformat()
        self.tasks_config.save()

        self.console.print(f"✓ Task added: {description}", style="green")
        self.logger.info(f"Task added: {description}")

    def cmd_list_tasks(self, _):
        """List all tasks."""
        tasks = self.tasks_config["tasks"]

        if not tasks:
            self.console.print("No tasks found", style="yellow")
            return

        self.console.print("[bold]Tasks:[/bold]\n")

        for task in tasks:
            status = "✓" if task["completed"] else "○"
            style = "green" if task["completed"] else "white"
            self.console.print(
                f"[{style}]{status} [{task['id']}] {task['description']}[/]"
            )

        self.console.print(f"\nTotal: {len(tasks)} tasks")

    def cmd_complete(self, args):
        """Mark task as completed. Usage: complete <task_id>"""
        if not args:
            self.console.print("Usage: complete <task_id>", style="yellow")
            return

        try:
            task_id = int(args[0])
            tasks = self.tasks_config["tasks"]

            for task in tasks:
                if task["id"] == task_id:
                    task["completed"] = True
                    self.tasks_config["last_updated"] = datetime.now().isoformat()
                    self.tasks_config.save()

                    self.console.print(
                        f"✓ Task {task_id} completed", style="green"
                    )
                    self.logger.info(f"Task {task_id} marked complete")
                    return

            self.console.print(f"Task {task_id} not found", style="red")

        except ValueError:
            self.console.print("Task ID must be a number", style="red")

    def cmd_remove(self, args):
        """Remove a task. Usage: remove <task_id>"""
        if not args:
            self.console.print("Usage: remove <task_id>", style="yellow")
            return

        try:
            task_id = int(args[0])
            tasks = self.tasks_config["tasks"]

            original_count = len(tasks)
            self.tasks_config["tasks"] = [
                t for t in tasks if t["id"] != task_id
            ]

            if len(self.tasks_config["tasks"]) < original_count:
                self.tasks_config["last_updated"] = datetime.now().isoformat()
                self.tasks_config.save()
                self.console.print(f"✓ Task {task_id} removed", style="green")
                self.logger.info(f"Task {task_id} removed")
            else:
                self.console.print(f"Task {task_id} not found", style="red")

        except ValueError:
            self.console.print("Task ID must be a number", style="red")

    def cmd_stats(self, _):
        """Show task statistics."""
        tasks = self.tasks_config["tasks"]

        if not tasks:
            self.console.print("No tasks to analyze", style="yellow")
            return

        total = len(tasks)
        completed = sum(1 for t in tasks if t["completed"])
        pending = total - completed

        self.console.print("[bold]Task Statistics[/bold]\n")
        self.console.print(f"Total:     {total}")
        self.console.print(f"Completed: {completed}", style="green")
        self.console.print(f"Pending:   {pending}", style="yellow")

        if total > 0:
            percentage = (completed / total) * 100
            self.console.print(f"Progress:  {percentage:.1f}%")

        if self.tasks_config["last_updated"]:
            self.console.print(
                f"\nLast Updated: {self.tasks_config['last_updated']}"
            )
```

---

# Troubleshooting

## Common Issues

### Plugin Not Loading

- Check file is in `plugin/` directory
- Verify class is named `Plugin`
- Ensure file has `.py` extension
- Check for syntax errors

### Commands Not Recognized

- Method names must start with `cmd_`
- Restart CLI-Toolkit after adding plugin
- Check method is not private (no leading underscore after `cmd_`)

### Configuration Errors

- Verify JSON syntax in config files
- Check file permissions in `config/` directory
- Review validation settings

### Import Errors

- Use relative imports from project root
- Available modules: `api`, `util.config`
- Don't import from other plugins directly

## Getting Help

- Check application logs in log files
- Use `version` command to verify plugin loaded
- Test with simple commands first
- Review this guide for examples

---

**Happy Plugin Development!** 🚀
