"""
Helper functions and utilities.
"""
import os
import json
import hashlib
from typing import Any, Dict, List, Optional, Union
from pathlib import Path
from datetime import datetime

def allowed_file(filename: str, allowed_extensions: set) -> bool:
    """Check if the file has an allowed extension."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def generate_unique_filename(original_filename: str) -> str:
    """Generate a unique filename using a timestamp and hash."""
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    name_hash = hashlib.md5(original_filename.encode()).hexdigest()[:8]
    return f"{timestamp}_{name_hash}{Path(original_filename).suffix}"

def ensure_directory_exists(directory: Union[str, Path]) -> Path:
    """Ensure a directory exists, create it if it doesn't."""
    path = Path(directory)
    path.mkdir(parents=True, exist_ok=True)
    return path

def read_json_file(file_path: Union[str, Path]) -> Any:
    """Read and parse a JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json_file(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """Write data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)

def format_duration(seconds: float) -> str:
    """Format duration in seconds to HH:MM:SS format."""
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def safe_get(dictionary: Dict, *keys, default=None) -> Any:
    """
    Safely get a value from a nested dictionary.
    
    Example:
        value = safe_get(data, 'key1', 'key2', default='default')
    """
    current = dictionary
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key, {})
    
    return current if current != {} else default

def remove_none_values(data: Dict) -> Dict:
    """Remove None values from a dictionary recursively."""
    if not isinstance(data, dict):
        return data
    
    return {
        k: remove_none_values(v) 
        for k, v in data.items() 
        if v is not None
    }