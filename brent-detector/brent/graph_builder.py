import networkx as nx
import os

def build_dependency_graph(file_paths, parser_func, project_root):
    """
    Build a directed dependency graph from Python files in a project.
    
    Args:
        file_paths: List of absolute file paths to analyze
        parser_func: Function to extract imports from a file
        project_root: Root directory of the project
    
    Returns:
        A NetworkX DiGraph representing module dependencies
    """
    graph = nx.DiGraph()

    # Map file paths to module names
    file_to_module = {}
    internal_modules = set()

    for file_path in file_paths:
        # Get relative path and convert to module name
        rel_path = os.path.relpath(file_path, project_root)
        module_name = os.path.splitext(rel_path)[0].replace(os.sep, ".")
        
        file_to_module[file_path] = module_name
        internal_modules.add(module_name)

    # Add all modules as nodes
    for module_name in internal_modules:
        graph.add_node(module_name)

    # Build edges based on imports
    for file_path in file_paths:
        source_module = file_to_module[file_path]
        imports = parser_func(file_path, project_root)

        for imp in imports:
            # Find matching internal modules for this import
            matching_modules = _find_matching_modules(imp, internal_modules)
            
            for target_module in matching_modules:
                # Add edge: source depends on target
                graph.add_edge(source_module, target_module)

    return graph


def _find_matching_modules(import_name, internal_modules):
    """
    Find internal modules that match an import statement.
    
    Handles multiple matching strategies:
    1. Exact match
    2. Suffix match (import may not have package prefix)
    3. Submodule match
    4. Parent module match
    
    Args:
        import_name: Name of the import (e.g., 'os', 'django.db', 'myapp.models')
        internal_modules: Set of module names in the project
    
    Returns:
        List of matching internal module names
    """
    matches = []
    
    for module in internal_modules:
        # Strategy 1: Exact match
        if module == import_name:
            matches.append(module)
            continue
        
        # Strategy 2: Submodule match (e.g., importing 'app' matches 'app.models')
        if module.startswith(import_name + "."):
            matches.append(module)
            continue
        
        # Strategy 3: Parent module match (e.g., importing 'app.models' when module is 'app')
        if import_name.startswith(module + "."):
            matches.append(module)
            continue
        
        # Strategy 4: Suffix matching for imports that don't include full path
        # E.g., module is 'src.flask.config' and import is 'flask.config'
        # Split by dots and check if the suffix matches
        module_parts = module.split(".")
        import_parts = import_name.split(".")
        
        # If import is shorter, check if module ends with import
        if len(import_parts) < len(module_parts):
            module_suffix = ".".join(module_parts[-len(import_parts):])
            if module_suffix == import_name:
                matches.append(module)
                continue
        
        # Check if the last N parts of module match import
        if len(module_parts) >= len(import_parts):
            # Try matching from different starting positions
            for start_idx in range(len(module_parts) - len(import_parts) + 1):
                module_section = ".".join(module_parts[start_idx:])
                if module_section == import_name:
                    matches.append(module)
                    break
    
    # Remove duplicates while preserving list type
    return list(set(matches))