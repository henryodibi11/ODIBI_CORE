"""
Proposed fix for AzureAdapter container handling inconsistency

PROBLEM:
- Container can be set in __init__ but is ignored
- _parse_path always expects "container/path" format

SOLUTION:
- If self.container is set, use it as default
- If path contains container, override default
- Support both modes seamlessly
"""

def _parse_path(self, path: str) -> tuple:
    """
    Parse Azure path into container and file path.
    
    Supports two modes:
    1. Default container (set in __init__): path = "folder/file.parquet"
    2. Container in path: path = "container/folder/file.parquet"
    
    Args:
        path: Path like "folder/file.parquet" or "container/folder/file.parquet"
    
    Returns:
        tuple: (container_name, file_path)
    """
    # Remove leading slash if present
    path = path.lstrip("/")
    
    # Check if path contains a slash (might have container)
    if "/" in path:
        parts = path.split("/", 1)
        first_part = parts[0]
        remaining_path = parts[1] if len(parts) > 1 else ""
        
        # Heuristic: If self.container is set and first_part looks like a folder
        # (e.g., starts with lowercase, contains underscores/dashes),
        # treat entire path as file_path within default container
        
        # For now, simple logic:
        # If self.container is set AND path doesn't start with known container name,
        # assume path is file_path within default container
        if self.container and first_part != self.container:
            # Could be a folder path within the default container
            # OR could be a different container
            
            # Simple approach: Check if first_part is a known container
            # For safety, assume it's a different container if it looks like one
            # (no dots, no spaces, short name)
            if len(first_part) < 30 and "." not in first_part and " " not in first_part:
                # Likely a container name
                return first_part, remaining_path
            else:
                # Likely a folder path
                return self.container, path
        else:
            # No default container, or path explicitly specifies container
            return first_part, remaining_path
    else:
        # No slash - could be just container name or just filename
        if self.container:
            # Treat as filename in default container
            return self.container, path
        else:
            # No default container, treat as container name only
            return path, ""


# CLEANER ALTERNATIVE: Be explicit about modes
# ================================================

def _parse_path_v2(self, path: str) -> tuple:
    """
    Parse Azure path into container and file path.
    
    Rules:
    1. If path starts with "container@", extract container explicitly:
       "mycontainer@folder/file.parquet" → ("mycontainer", "folder/file.parquet")
    
    2. If self.container is set and path doesn't have "@", use default:
       "folder/file.parquet" → (self.container, "folder/file.parquet")
    
    3. If no self.container and no "@", first part is container:
       "container/folder/file.parquet" → ("container", "folder/file.parquet")
    
    Args:
        path: Path in one of the formats above
    
    Returns:
        tuple: (container_name, file_path)
    
    Raises:
        ValueError: If container cannot be determined
    """
    # Check for explicit container syntax: "container@path"
    if "@" in path:
        container, file_path = path.split("@", 1)
        return container, file_path
    
    # Remove leading slash
    path = path.lstrip("/")
    
    # If default container is set, use it
    if self.container:
        return self.container, path
    
    # Otherwise, first part of path is container
    if "/" in path:
        parts = path.split("/", 1)
        return parts[0], parts[1]
    else:
        # Just container name, no file path
        return path, ""


# SIMPLEST SOLUTION: Make it explicit in docs and add helper
# ===========================================================

def _parse_path_simple(self, path: str) -> tuple:
    """
    Parse Azure path into container and file path.
    
    BEHAVIOR:
    - If self.container is set: path is treated as file_path within that container
    - If self.container is None: path must be "container/file_path" format
    
    Args:
        path: "folder/file.parquet" (if container set) or "container/folder/file.parquet"
    
    Returns:
        tuple: (container_name, file_path)
    
    Raises:
        ValueError: If container cannot be determined
    """
    path = path.lstrip("/")
    
    # If default container is set, entire path is file_path
    if self.container:
        return self.container, path
    
    # Otherwise, split path into container and file_path
    if "/" not in path:
        # Just container name
        return path, ""
    
    parts = path.split("/", 1)
    return parts[0], parts[1]


# USAGE EXAMPLES
# ==============

# Example 1: With default container
azure = CloudAdapter.create("azure", account_name="...", container="bronze")
azure.read("data/customers.parquet")  # ← Uses "bronze" container
azure.write(df, "data/output.parquet")  # ← Uses "bronze" container

# Example 2: Without default container (multi-container)
azure = CloudAdapter.create("azure", account_name="...")
azure.read("bronze/data/customers.parquet")  # ← "bronze" from path
azure.write(df, "silver/data/output.parquet")  # ← "silver" from path

# Example 3: Override default container (with @ syntax)
azure = CloudAdapter.create("azure", account_name="...", container="bronze")
azure.read("data/file.parquet")  # ← Uses "bronze" (default)
azure.write(df, "silver@data/output.parquet")  # ← Override to "silver"
