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
# 注意：Excel 单元格索引从 1 开始
# 第1行数据对应 A1, B1, C1... (row_idx=0)
# 第2行数据对应 A2, B2, C2... (row_idx=1)

data = {
    "headers": ["Name", "Age", "City"],
    "rows": [
        ["Alice", 25, "New York"],    # 第1行 (A1-C1)
        ["Bob", 30, "London"],        # 第2行 (A2-C2)
        ["Total", "=SUM(B1:B2)", ""], # 第3行 (A3-C3)
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