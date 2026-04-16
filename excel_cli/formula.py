import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Set


def parse_cell_ref(ref: str) -> Optional[Tuple[int, int]]:
    match = re.match(r"^([A-Z]+)(\d+)$", ref.upper())
    if not match:
        return None
    col_str, row_str = match.groups()
    col = 0
    for c in col_str:
        col = col * 26 + (ord(c) - ord("A") + 1)
    row = int(row_str)
    return (row - 1, col - 1)


def parse_range(range_str: str) -> List[Tuple[int, int]]:
    if ":" not in range_str:
        cell = parse_cell_ref(range_str)
        return [cell] if cell else []
    
    parts = range_str.split(":")
    if len(parts) != 2:
        return []
    
    start = parse_cell_ref(parts[0])
    end = parse_cell_ref(parts[1])
    if not start or not end:
        return []
    
    cells = []
    for row in range(min(start[0], end[0]), max(start[0], end[0]) + 1):
        for col in range(min(start[1], end[1]), max(start[1], end[1]) + 1):
            cells.append((row, col))
    return cells


def evaluate_formula(
    formula: str,
    data: Dict[str, Any],
    formulas: Dict[str, Callable],
    custom_functions: Dict[str, Callable],
    evaluating: Optional[Set[Tuple[int, int]]] = None,
) -> Any:
    if not formula.startswith("="):
        return formula
    
    if evaluating is None:
        evaluating = set()
    
    expr = formula[1:].strip()
    
    func_match = re.match(r"^([A-Z]+)\((.+)\)$", expr.upper())
    if func_match:
        func_name = func_match.group(1).upper()
        args_str = func_match.group(2)
        return _evaluate_builtin(func_name, args_str, data, formulas, evaluating)
    
    custom_match = re.match(r"^CUSTOM\.(\w+)\((.*)\)$", expr, re.IGNORECASE)
    if custom_match:
        func_name = custom_match.group(1)
        args_str = custom_match.group(2)
        return _evaluate_custom(func_name, args_str, custom_functions)
    
    return formula


def _evaluate_builtin(
    func_name: str,
    args_str: str,
    data: Dict[str, Any],
    formulas: Dict[str, Callable],
    evaluating: Set[Tuple[int, int]],
) -> Any:
    cells = parse_range(args_str)
    if not cells:
        return "#REF!"
    
    headers = data.get("headers", [])
    rows = data.get("rows", [])
    
    values = []
    for row_idx, col_idx in cells:
        if row_idx < 0 or col_idx < 0:
            continue
        if row_idx >= len(rows):
            continue
        row = rows[row_idx]
        if col_idx >= len(row):
            continue
        
        if (row_idx, col_idx) in evaluating:
            continue
        
        evaluating.add((row_idx, col_idx))
        val = row[col_idx]
        if isinstance(val, str) and val.startswith("="):
            val = evaluate_formula(val, data, formulas, {}, evaluating)
        evaluating.discard((row_idx, col_idx))
        
        if isinstance(val, (int, float)):
            values.append(val)
        elif isinstance(val, str) and not val.startswith("#"):
            try:
                values.append(float(val))
            except ValueError:
                pass
    
    if func_name in formulas:
        return formulas[func_name](values)
    
    builtin = {
        "SUM": sum,
        "AVG": lambda v: sum(v) / len(v) if v else 0,
        "COUNT": len,
        "MIN": min,
        "MAX": max,
    }
    
    if func_name in builtin:
        try:
            return builtin[func_name](values)
        except (ValueError, TypeError):
            return "#ERROR!"
    
    return "#NAME?"


def _evaluate_custom(
    func_name: str,
    args_str: str,
    custom_functions: Dict[str, Callable],
) -> Any:
    if func_name not in custom_functions:
        return "#NAME?"
    
    args = []
    if args_str.strip():
        for arg in args_str.split(","):
            arg = arg.strip().strip('"').strip("'")
            args.append(arg)
    
    try:
        func = custom_functions[func_name]
        if args:
            return func(*args)
        return func()
    except Exception as e:
        return f"#ERROR!({e})"


def get_cell_value(
    row_idx: int,
    col_idx: int,
    data: Dict[str, Any],
    formulas: Dict[str, Callable],
    custom_functions: Dict[str, Callable],
) -> Any:
    rows = data.get("rows", [])
    if row_idx < 0 or row_idx >= len(rows):
        return ""
    
    row = rows[row_idx]
    if col_idx < 0 or col_idx >= len(row):
        return ""
    
    value = row[col_idx]
    if isinstance(value, str) and value.startswith("="):
        return evaluate_formula(value, data, formulas, custom_functions)
    return value