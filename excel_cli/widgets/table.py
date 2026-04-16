from typing import Any, Callable, Dict

from textual.containers import Horizontal
from textual.message import Message
from textual.widgets import Label, Static


class TableWidget(Static):
    DEFAULT_CSS = """
    TableWidget {
        height: auto;
        padding: 1;
    }
    
    .table-header {
        background: $primary;
        padding: 0 1;
        height: 1;
    }
    
    .table-header Label {
        color: white;
        text-style: bold;
        width: 20;
        min-width: 10;
        max-width: 40;
    }
    
    .table-row {
        height: 1;
        background: $surface;
    }
    
    .table-row:even {
        background: $panel;
    }
    
    .table-cell {
        width: 20;
        min-width: 10;
        max-width: 40;
        padding: 0 1;
    }
    
    .table-cell:focus {
        background: $accent;
    }
    
    .row-number {
        width: 4;
        min-width: 4;
        max-width: 4;
        background: $panel;
        color: $text-muted;
        text-align: right;
        padding: 0 1;
    }
    
    .selected-cell {
        background: $accent;
        color: white;
    }
    """
    
    class Modified(Message):
        pass
    
    def __init__(
        self,
        data: Dict[str, Any],
        formulas: Dict[str, Callable],
        custom_functions: Dict[str, Callable],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.data = data
        self.formulas = formulas
        self.custom_functions = custom_functions
        self.selected_row = 0
        self.selected_col = 0
        self._editing = False
        self._edit_buffer = ""
    
    def compose(self):
        headers = self.data.get("headers", [])
        rows = self.data.get("rows", [])
        
        with Horizontal(classes="table-header"):
            yield Label("", classes="row-number")
            for col_idx, header in enumerate(headers):
                yield Label(str(header) if header else "", classes="table-cell")
        
        for row_idx, row in enumerate(rows):
            with Horizontal(classes="table-row"):
                yield Label(str(row_idx + 1), classes="row-number")
                for col_idx, cell in enumerate(row):
                    display_value = self._get_display_value(cell)
                    yield Label(
                        str(display_value) if display_value is not None else "",
                        classes="table-cell",
                        id=f"cell-{row_idx}-{col_idx}",
                    )
    
    def _get_display_value(self, value: Any) -> Any:
        from ..formula import evaluate_formula
        
        if isinstance(value, str) and value.startswith("="):
            return evaluate_formula(value, self.data, self.formulas, self.custom_functions)
        return value
    
    def get_data(self) -> Dict[str, Any]:
        return self.data
    
    def add_row(self) -> None:
        headers = self.data.get("headers", [])
        rows = self.data.get("rows", [])
        new_row = [""] * len(headers)
        rows.append(new_row)
        self.data["rows"] = rows
        self._refresh_table()
        self.post_message(self.Modified())
    
    def add_column(self) -> None:
        headers = self.data.get("headers", [])
        rows = self.data.get("rows", [])
        
        col_name = f"列{len(headers) + 1}"
        headers.append(col_name)
        self.data["headers"] = headers
        
        for row in rows:
            row.append("")
        self.data["rows"] = rows
        
        self._refresh_table()
        self.post_message(self.Modified())
    
    def insert_formula(self) -> None:
        if self._editing:
            return
        
        rows = self.data.get("rows", [])
        if self.selected_row >= len(rows):
            return
        
        row = rows[self.selected_row]
        if self.selected_col >= len(row):
            return
        
        current = row[self.selected_col]
        if not isinstance(current, str) or not current.startswith("="):
            current = ""
        
        self._edit_buffer = str(current) if current else ""
        self._editing = True
        self._show_edit_input()
    
    def _show_edit_input(self) -> None:
        cell_id = f"cell-{self.selected_row}-{self.selected_col}"
        try:
            cell = self.query_one(f"#{cell_id}", Label)
            cell.add_class("selected-cell")
        except Exception:
            pass
    
    def _refresh_table(self) -> None:
        self.remove_children()
        for child in self.compose():
            self.mount(child)
    
    def on_key(self, event) -> None:
        key = event.key
        
        if self._editing:
            if key == "escape":
                self._editing = False
                self._refresh_table()
            elif key == "enter":
                self._editing = False
                rows = self.data.get("rows", [])
                if self.selected_row < len(rows):
                    row = rows[self.selected_row]
                    while len(row) <= self.selected_col:
                        row.append("")
                    row[self.selected_col] = self._edit_buffer
                    self.data["rows"] = rows
                    self.post_message(self.Modified())
                self._refresh_table()
            else:
                if key == "backspace":
                    self._edit_buffer = self._edit_buffer[:-1]
                elif len(key) == 1:
                    self._edit_buffer += key
            event.stop()
            return
        
        rows = self.data.get("rows", [])
        headers = self.data.get("headers", [])
        
        if key == "up":
            self.selected_row = max(0, self.selected_row - 1)
        elif key == "down":
            self.selected_row = min(len(rows) - 1, self.selected_row + 1)
        elif key == "left":
            self.selected_col = max(0, self.selected_col - 1)
        elif key == "right":
            self.selected_col = min(len(headers) - 1, self.selected_col + 1)
        elif key == "enter":
            self._edit_buffer = ""
            self._editing = True
            rows = self.data.get("rows", [])
            if self.selected_row < len(rows):
                row = rows[self.selected_row]
                if self.selected_col < len(row):
                    self._edit_buffer = str(row[self.selected_col]) if row[self.selected_col] else ""
        else:
            return
        
        self._refresh_table()
        event.stop()