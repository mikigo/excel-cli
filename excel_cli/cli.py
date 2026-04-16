import argparse
import sys
from pathlib import Path

from .app import ExcelCliApp
from .storage import load_data, save_data


def main():
    parser = argparse.ArgumentParser(
        prog="excel-cli",
        description="CLI spreadsheet editor with formula support and Excel export"
    )
    parser.add_argument(
        "file",
        type=str,
        help="Path to Python file containing table data"
    )
    parser.add_argument(
        "--export",
        "-e",
        type=str,
        help="Export to Excel file and exit"
    )
    
    args = parser.parse_args()
    file_path = Path(args.file)
    
    if not file_path.exists():
        file_path.parent.mkdir(parents=True, exist_ok=True)
        save_data(file_path, {"headers": [], "rows": []})
    
    data = load_data(file_path)
    
    if args.export:
        from .export import export_to_excel
        export_to_excel(data, Path(args.export))
        print(f"Exported to {args.export}")
        return 0
    
    app = ExcelCliApp(data=data, file_path=file_path)
    app.run()
    return 0


if __name__ == "__main__":
    sys.exit(main())