from backend.core.db import config_col

class ConfigManager:
    """Manages application configuration and user preferences in MongoDB"""
    
    def __init__(self, config_file=None):
        # We accept config_file param to avoid breaking legacy init calls
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from MongoDB"""
        try:
            cfg = config_col.find_one({'_id': 'user_preferences'})
            if cfg:
                cfg.pop('_id', None)
                return {**self.get_default_config(), **cfg}
        except Exception as e:
            print(f"Error loading config from MongoDB: {e}")
        
        return self.get_default_config()
    
    def save_config(self):
        """Save configuration to MongoDB"""
        try:
            # We copy config to avoid modifying in-place _id insertion
            data = self.config.copy()
            config_col.replace_one({'_id': 'user_preferences'}, data, upsert=True)
        except Exception as e:
            print(f"Error saving config to MongoDB: {e}")
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'quality': 85,
            'output_format': 'webp',
            'maintain_aspect': True,
            'preserve_exif': False,
            'max_workers': 4,
            'use_cache': True,
            'theme': 'dark',
            'language': 'fa',
            'smart_format': True
        }
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
    
    def update(self, updates: dict):
        """Update multiple configuration values"""
        self.config.update(updates)
        self.save_config()
