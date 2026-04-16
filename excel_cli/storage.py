import ast
import re
from pathlib import Path
from typing import Any, Dict, Optional


def load_data(file_path: Path) -> Dict[str, Any]:
    if not file_path.exists():
        return {"headers": [], "rows": []}
    
    content = file_path.read_text(encoding="utf-8")
    tree = ast.parse(content)
    
    result: Dict[str, Any] = {
        "headers": [],
        "rows": [],
        "formulas": {},
        "custom_functions": {},
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "data":
                        result["data"] = _extract_dict(node.value)
                    elif target.id == "formulas":
                        result["formulas"] = _extract_dict(node.value)
                    elif target.id == "custom_functions":
                        result["custom_functions"] = _extract_dict(node.value)
    
    if "data" in result:
        result["headers"] = result["data"].get("headers", [])
        result["rows"] = result["data"].get("rows", [])
        del result["data"]
    
    return result


def _extract_dict(node: ast.AST) -> dict:
    if not isinstance(node, ast.Dict):
        return {}
    
    result = {}
    for key, value in zip(node.keys, node.values):
        if key is None:
            continue
        key_str = _extract_value(key)
        if key_str is not None:
            result[key_str] = _extract_value(value)
    return result


def _extract_value(node: ast.AST) -> Any:
    if isinstance(node, ast.Constant):
        return node.value
    elif isinstance(node, ast.List):
        return [_extract_value(elt) for elt in node.elts]
    elif isinstance(node, ast.Dict):
        return _extract_dict(node)
    elif isinstance(node, ast.Call):
        func_name = _get_func_name(node.func)
        if func_name:
            return f"={func_name}({_format_args(node.args)})"
    return None


def _get_func_name(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_get_func_name(node.value)}.{node.attr}"
    return None


def _format_args(args: list) -> str:
    parts = []
    for arg in args:
        if isinstance(arg, ast.Constant):
            parts.append(str(arg.value))
        elif isinstance(arg, ast.List):
            parts.append(f"[{', '.join(str(_extract_value(e)) for e in arg.elts)}]")
        elif isinstance(arg, ast.Call):
            parts.append(_extract_value(arg))
    return ", ".join(parts)


def save_data(file_path: Path, data: Dict[str, Any]) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    lines = [
        '# -*- coding: utf-8 -*-',
        '# This file is managed by excel-cli',
        '',
        'data = {',
        f'    "headers": {_format_value(data.get("headers", []))},',
        '    "rows": [',
    ]
    
    for row in data.get("rows", []):
        lines.append(f'        {_format_value(row)},')
    
    lines.extend([
        '    ],',
        '}',
        '',
    ])
    
    if data.get("formulas"):
        lines.extend([
            'formulas = {',
        ])
        for name, func in data["formulas"].items():
            lines.append(f'    "{name}": {func},')
        lines.extend([
            '}',
            '',
        ])
    
    if data.get("custom_functions"):
        lines.extend([
            'custom_functions = {',
        ])
        for name, func in data["custom_functions"].items():
            lines.append(f'    "{name}": {func},')
        lines.extend([
            '}',
            '',
        ])
    
    file_path.write_text("\n".join(lines), encoding="utf-8")


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        return repr(value)
    elif isinstance(value, list):
        return "[" + ", ".join(_format_value(v) for v in value) + "]"
    elif isinstance(value, dict):
        return "{" + ", ".join(f"{_format_value(k)}: {_format_value(v)}" for k, v in value.items()) + "}"
    else:
        return repr(value)