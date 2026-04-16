from typing import Any, Callable, Dict, List


def load_custom_functions(file_path) -> Dict[str, Callable]:
    import importlib.util
    
    custom_functions = {}
    
    try:
        spec = importlib.util.spec_from_file_location("user_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "custom_functions"):
                custom_functions.update(module.custom_functions)
    except Exception:
        pass
    
    return custom_functions


def load_formulas(file_path) -> Dict[str, Callable]:
    import importlib.util
    
    formulas = {}
    
    try:
        spec = importlib.util.spec_from_file_location("user_module", file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            if hasattr(module, "formulas"):
                formulas.update(module.formulas)
    except Exception:
        pass
    
    return formulas


def register_custom_function(
    custom_functions: Dict[str, Callable],
    name: str,
    func: Callable,
) -> None:
    custom_functions[name] = func


def unregister_custom_function(
    custom_functions: Dict[str, Callable],
    name: str,
) -> None:
    if name in custom_functions:
        del custom_functions[name]


def get_available_functions(custom_functions: Dict[str, Callable]) -> List[str]:
    return list(custom_functions.keys())