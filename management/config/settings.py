"""
Settings management module for TinySteps
"""
import os
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

class Settings:
    """Settings manager for TinySteps management commands
    
    This class provides a centralized way to access configuration settings
    stored in the settings.json file.
    """
    _instance = None
    
    def __new__(cls):
        """Implement singleton pattern for settings"""
        if cls._instance is None:
            cls._instance = super(Settings, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize settings if not already initialized"""
        if not getattr(self, "_initialized", False):
            self._load_settings()
            self._initialized = True
    
    def _load_settings(self):
        """Load settings from settings.json file"""
        self.settings = {}
        self.settings_file = Path(__file__).parent / "settings.json"
        
        # Default settings (fallback)
        self.default_settings = {
            "paths": {
                "data_dir": "data/tinySteps_jsons",
                "babies_dir": "data/tinySteps_jsons/babies",
                "guides_dir": "data/tinySteps_jsons/guides",
                "forum_dir": "data/tinySteps_jsons/forum"
            },
            "translations": {
                "default_language": "en",
                "supported_languages": ["en", "es"],
                "auto_translate": True
            },
            "notifications": {
                "send_email": True,
                "days_in_advance": 1
            },
            "content_generation": {
                "default_comment_count": 5,
                "default_baby_count": 5,
                "default_forum_count": 15
            }
        }
        
        # Try to load settings from file
        try:
            if self.settings_file.exists():
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    self.settings = loaded_settings
                    logger.info(f"Settings loaded from {self.settings_file}")
            else:
                logger.warning(f"Settings file not found at {self.settings_file}")
                self.settings = self.default_settings.copy()
        except Exception as e:
            logger.error(f"Error loading settings: {e}")
            self.settings = self.default_settings.copy()
    
    def get(self, key_path, default=None):
        """Get setting value using dot notation path
        
        Args:
            key_path (str): Path to setting using dot notation (e.g., 'paths.data_dir')
            default: Default value to return if setting not found
            
        Returns:
            Setting value or default if not found
        """
        if not key_path:
            return default
            
        parts = key_path.split('.')
        current = self.settings
        
        try:
            for part in parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            # If not found in main settings, try default settings
            try:
                current = self.default_settings
                for part in parts:
                    current = current[part]
                return current
            except (KeyError, TypeError):
                return default
    
    def set(self, key_path, value):
        """Set a setting value using dot notation path
        
        Args:
            key_path (str): Path to setting using dot notation (e.g., 'paths.data_dir')
            value: Value to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not key_path:
            return False
            
        parts = key_path.split('.')
        current = self.settings
        
        # Navigate to the appropriate nested dictionary
        for part in parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Set the value
        current[parts[-1]] = value
        return True
    
    def save(self):
        """Save current settings to file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            logger.info(f"Settings saved to {self.settings_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
            return False
    
    def get_path(self, path_key, create=True):
        """Get absolute path for a settings path and optionally create the directory
        
        Args:
            path_key (str): Path key in settings (e.g., 'paths.data_dir')
            create (bool): Whether to create the directory if it doesn't exist
            
        Returns:
            str: Absolute path or None if not found
        """
        rel_path = self.get(path_key)
        if not rel_path:
            return None
            
        base_dir = Path(__file__).resolve().parent.parent.parent
        abs_path = os.path.join(base_dir, rel_path)
        
        if create and not os.path.exists(abs_path):
            try:
                os.makedirs(abs_path)
                logger.info(f"Created directory: {abs_path}")
            except Exception as e:
                logger.error(f"Error creating directory {abs_path}: {e}")
        
        return abs_path
    
    def reset_to_defaults(self):
        """Reset settings to default values
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.settings = self.default_settings.copy()
            return self.save()
        except Exception as e:
            logger.error(f"Error resetting settings: {e}")
            return False

settings = Settings()

# Function to access settings from other modules
def get_settings():
    """Get the settings instance
    
    Returns:
        Settings: Singleton settings instance
    """
    return settings