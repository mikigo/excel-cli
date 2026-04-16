from pathlib import Path
from typing import Any, Dict

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widgets import Footer, Header

from .custom import load_custom_functions, load_formulas
from .export import export_to_excel
from .storage import load_data, save_data
from .widgets.table import TableWidget


class ExcelCliApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    
    .header-bar {
        height: 3;
        background: $primary;
        padding: 0 2;
        align: center middle;
    }
    
    .header-bar Label {
        color: white;
        text-style: bold;
    }
    
    .status-bar {
        height: 1;
        background: $panel;
        padding: 0 2;
    }
    
    .status-bar Label {
        color: $text;
    }
    
    .cell-input {
        width: 1fr;
        margin: 0 1;
    }
    
    #table-container {
        height: 1fr;
        overflow: auto;
    }
    
    Button {
        margin: 0 1;
    }
    """
    
    BINDINGS = [
        Binding("ctrl+s", "save", "保存"),
        Binding("ctrl+e", "export", "导出Excel"),
        Binding("ctrl+r", "refresh", "刷新"),
        Binding("ctrl+n", "new_row", "新增行"),
        Binding("ctrl+d", "new_col", "新增列"),
        Binding("ctrl+f", "formula", "插入公式"),
        Binding("q", "quit", "退出"),
    ]
    
    def __init__(self, data: Dict[str, Any], file_path: Path, **kwargs):
        super().__init__(**kwargs)
        self.data = data
        self.file_path = file_path
        self.formulas = load_formulas(file_path)
        self.custom_functions = load_custom_functions(file_path)
        self._modified = False
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            TableWidget(
                data=self.data,
                formulas=self.formulas,
                custom_functions=self.custom_functions,
                id="table",
            ),
            id="table-container",
        )
        yield Footer()
    
    def on_mount(self) -> None:
        self.title = f"excel-cli - {self.file_path.name}"
    
    def action_save(self) -> None:
        table = self.query_one("#table", TableWidget)
        self.data = table.get_data()
        save_data(self.file_path, self.data)
        self._modified = False
        self.notify("已保存", title="保存成功")
    
    def action_export(self) -> None:
        from pathlib import Path
        
        output_path = self.file_path.with_suffix(".xlsx")
        table = self.query_one("#table", TableWidget)
        data = table.get_data()
        export_to_excel(data, output_path)
        self.notify(f"已导出到 {output_path}", title="导出成功")
    
    def action_refresh(self) -> None:
        self.formulas = load_formulas(self.file_path)
        self.custom_functions = load_custom_functions(self.file_path)
        table = self.query_one("#table", TableWidget)
        table.formulas = self.formulas
        table.custom_functions = self.custom_functions
        table.refresh()
        self.notify("已刷新公式和自定义函数", title="刷新成功")
    
    def action_new_row(self) -> None:
        table = self.query_one("#table", TableWidget)
        table.add_row()
        self._modified = True
    
    def action_new_col(self) -> None:
        table = self.query_one("#table", TableWidget)
        table.add_column()
        self._modified = True
    
    def action_formula(self) -> None:
        table = self.query_one("#table", TableWidget)
        table.insert_formula()
    
    def on_table_widget_modified(self, event: TableWidget.Modified) -> None:
        self._modified = True