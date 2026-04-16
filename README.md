# excel-cli

CLI spreadsheet editor with formula support and Excel export.

## Usage

```bash
# Edit existing table file
excel-cli path/to/data.py

# Create new table file
excel-cli new_table.py

# Export to Excel and exit
excel-cli path/to/data.py --export output.xlsx
```

## Features

- Interactive TUI for editing tables
- Formula support: SUM, AVG, COUNT, MIN, MAX
- Cell references (e.g., A1, B2:C5)
- Custom Python functions
- Excel export (.xlsx)

## Data File Format

```python
# data.py
data = {
    "headers": ["Name", "Age", "City"],
    "rows": [
        ["Alice", 25, "New York"],
        ["Bob", 30, "London"],
        ["Total", "=SUM(B2:B3)", ""]
    ]
}

# Optional: custom formulas
formulas = {
    "SUM": lambda cells: sum(cells),
}

# Optional: custom functions
def get_current_time():
    import datetime
    return datetime.datetime.now().strftime("%Y-%m-%d")

custom_functions = {
    "current_time": get_current_time,
}
```

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Arrow keys | Navigate cells |
| Enter | Edit cell |
| Escape | Exit edit mode |
| Ctrl+S | Save |
| Ctrl+E | Export to Excel |
| Ctrl+N | Add new row |
| Ctrl+D | Add new column |
| Ctrl+F | Insert formula |
| Ctrl+R | Refresh formulas |
| q | Quit |

## Installation

```bash
pip install excel-cli
```

## Dependencies

- textual >= 0.47.0
- openpyxl >= 3.1.0