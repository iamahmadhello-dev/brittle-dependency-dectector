import ast
import os

def extract_imports(file_path, project_root):
    """
    Extract all imports from a Python file.
    Returns a list of module names that are imported.
    
    Handles:
    - Direct imports: import module
    - From imports: from package import name
    - Relative imports: from . import module
    """
    imports = []

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # Process: import module, import module as alias
                for alias in node.names:
                    imports.append(alias.name)
            
            elif isinstance(node, ast.ImportFrom):
                # Process: from module import name, from . import name
                
                # Relative import: from . import X or from .. import X
                if node.level > 0:
                    # For relative imports, get the module being imported from
                    if node.module:
                        imports.append(node.module)
                    # Also track the imported names as they might be submodules
                    # from . import config → config is a module we import from current package
                    for alias in node.names:
                        if alias.name != "*":  # Skip wildcard imports
                            imports.append(alias.name)
                
                # Regular import: from module import name
                elif node.module:
                    imports.append(node.module)
                    # Also add individual imports in case they're modules
                    for alias in node.names:
                        if alias.name != "*":
                            imports.append(node.module + "." + alias.name)
    
    except Exception:
        # Silently skip files with syntax errors or encoding issues
        # Common in test files, tool continues analyzing other files
        pass

    return imports