import json
import yaml
from pathlib import Path
from datetime import datetime

class ConfigManager:
    def __init__(self, data_dir: Path = Path("/app/data")):
        self.data_dir = data_dir
        self.data_dir.mkdir(exist_ok=True)
        self.config_path = self.data_dir / "config.json"
        self.cache_path = self.data_dir / "cached_config.yaml"

    def load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            return {"url": "", "update_interval": 3600, "last_update": None}
        
        with open(self.config_path, "r") as f:
            return json.load(f)

    def save_config(self, config):
        """Save configuration to file"""
        with open(self.config_path, "w") as f:
            json.dump(config, f)

    def load_cached_proxy(self):
        """Load cached transformed configuration"""
        if not self.cache_path.exists():
            return None
        
        with open(self.cache_path, "r") as f:
            return yaml.safe_load(f)

    def save_cached_proxy(self, config: dict):
        """Save transformed configuration to cache"""
        with open(self.cache_path, "w") as f:
            yaml.dump(config, f, allow_unicode=True)

    def update_last_update_time(self):
        """Update the last update timestamp in config"""
        config = self.load_config()
        config["last_update"] = datetime.now().isoformat()
        self.save_config(config)
        return config["last_update"]


# Create a singleton instance
config_manager = ConfigManager() 