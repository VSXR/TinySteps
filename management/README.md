# TinySteps Management System

This system provides tools and commands for managing the TinySteps application.

## Structure

```
management/
├── __init__.py                  # Package initialization
├── run_command.py               # Command runner script
├── commands/                    # Command modules
│   ├── content/                 # Content generation commands
│   │   ├── generate_babies_list.py
│   │   ├── generate_forum_discussions.py
│   │   ├── generate_guides_discussions.py
│   │   └── refresh_articles.py
│   ├── notifications/           # Notification commands
│   │   └── send_reminders.py
│   ├── translations/            # Translation commands
│   │   ├── auto_translate.py
│   │   ├── init_translations.py
│   │   └── translation_workflow.py
│   └── utils/                   # Shared utilities
│       ├── data_helpers.py      # Data management helpers
│       └── settings.py          # Configuration settings
```

## Running Commands

Use the `run_command.py` script to execute management commands:

```bash
# List all available commands
python management/run_command.py --list

# Run a specific command
python management/run_command.py content.generate_babies_list --username=admin --count=5

# Run a notification command
python management/run_command.py notifications.send_reminders
```

## Available Commands

### Content Commands

- `content.generate_babies_list`: Generate random babies for testing

  - Options: `--username`, `--count`, `--clear`

- `content.generate_forum_discussions`: Generate forum discussions

  - Options: `--count`, `--comments`

- `content.generate_guides_discussions`: Add comments to guides

  - Options: `--max_comments`, `--all`

- `content.refresh_articles`: Update news articles from external APIs

### Notification Commands

- `notifications.send_reminders`: Send reminders for calendar events

### Translation Commands

- `translations.auto_translate`: Automatically translate content
- `translations.init_translations`: Initialize translation system
- `translations.translation_workflow`: Manage translation workflow

## Extending the System

To add a new command:

1. Create a new Python file in the appropriate directory under `commands/`
2. Implement a Django management command or a standalone command with a `main()` function
3. Your command will be automatically detected by the command runner

## Configuration

Settings are managed through the `settings.py` utility. Access configuration values:

```python
from management.config.settings import settings

# Get a configuration value
api_key = settings.get('api.key')
data_dir = settings.get('paths.data_dir')
```
