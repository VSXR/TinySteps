"""
Data utility functions for TinySteps management commands
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class ConfigManager:
    """Manages configuration settings for TinySteps management commands"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """Load configuration from the config file."""
        if not self.config_file:
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            self.config_file = base_dir / "config" / "settings.json"
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                logger.warning(f"Config file not found: {self.config_file}")
        except Exception as e:
            logger.error(f"Failed to load config: {str(e)}")
    
    def get(self, key, default=None):
        """Get a configuration value by key."""
        return self.config.get(key, default)
    
    def get_path(self, path_key):
        """Get a file path from configuration."""
        path = self.get(path_key)
        if path:
            if not os.path.isabs(path):
                base_dir = Path(self.config_file).parent.parent
                return os.path.join(base_dir, path)
            return path
        return None

# File and directory utilities
def ensure_directory_exists(directory_path):
    """Create directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        logger.info(f"Created directory: {directory_path}")
        return True
    return False

def get_abs_path(relative_path):
    """Convert a relative path to an absolute path based on the project root."""
    base_dir = Path(__file__).resolve().parent.parent.parent.parent
    return os.path.join(base_dir, relative_path)

def get_json_directory(data_type, config_manager=None):
    """Get the directory for a specific type of JSON data."""
    if config_manager is None:
        config_manager = ConfigManager()
    path_key = f"paths.{data_type}_dir"
    relative_path = config_manager.get(path_key)
    
    if not relative_path:
        logger.warning(f"No path defined for {data_type}_dir in settings")
        # Fallback to default structure
        relative_path = os.path.join("data", "tinySteps_jsons", data_type)
    
    abs_path = get_abs_path(relative_path)
    ensure_directory_exists(abs_path)
    return abs_path

# JSON data utilities
def load_json_data(file_path, default_data=None):
    """Load JSON data from a file."""
    try:
        if not os.path.exists(file_path):
            if default_data is not None:
                save_json_data(default_data, file_path)
                logger.info(f"Created default file: {os.path.basename(file_path)}")
            else:
                return default_data if default_data is not None else {}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON from {file_path}: {str(e)}")
        return default_data if default_data is not None else {}

def save_json_data(data, file_path, pretty=True):
    """Save data to a JSON file."""
    try:
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if pretty:
                json.dump(data, f, indent=2, ensure_ascii=False)
            else:
                json.dump(data, f, ensure_ascii=False)
        logger.info(f"Saved JSON data to {file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON to {file_path}: {str(e)}")
        return False

def get_json_files_in_directory(directory, extension=".json"):
    """Get all JSON files in a directory."""
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return []
    
    return [f for f in os.listdir(directory) 
            if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)]

def load_all_json_in_directory(directory):
    """Load all JSON files in a directory into a dictionary."""
    result = {}
    
    if not os.path.exists(directory):
        logger.warning(f"Directory not found: {directory}")
        return result
    
    for filename in get_json_files_in_directory(directory):
        file_path = os.path.join(directory, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                key = os.path.splitext(filename)[0]  # Remove extension
                result[key] = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load {filename}: {str(e)}")
    
    return result

# Project structure utilities
def setup_json_directory(dir_type, files_dict=None):
    """
    Set up a JSON directory with default files if needed.
    
    Args:
        dir_type: Type of directory (e.g., 'babies', 'guides')
        files_dict: Dictionary mapping filenames to default content
    
    Returns:
        Dictionary containing loaded data from all files
    """
    json_dir = get_json_directory(dir_type)
    result = {}
    
    if files_dict:
        for filename, default_data in files_dict.items():
            file_path = os.path.join(json_dir, filename)
            result[os.path.splitext(filename)[0]] = load_json_data(file_path, default_data)
    else:
        # Just load existing files
        result = load_all_json_in_directory(json_dir)
    
    return result