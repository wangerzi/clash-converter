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
        self.rules_path = self.data_dir / "rules_config.json"

    def load_config(self):
        """Load configuration from file"""
        if not self.config_path.exists():
            return {
                "url": "",
                "update_interval": 3600,
                "last_update": 0,
                "auth_tokens": []
            }
        
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

    def load_rules_config(self):
        """Load rules configuration from file"""
        if not self.rules_path.exists():
            # Return default rules from utils.py
            from .utils import DEFAULT_RULES, DEFAULT_RULE_PROVIDERS
            return {
                "rules": DEFAULT_RULES,
                "rule_providers": DEFAULT_RULE_PROVIDERS
            }
        
        with open(self.rules_path, "r") as f:
            return json.load(f)

    def save_rules_config(self, rules_config):
        """Save rules configuration to file"""
        with open(self.rules_path, "w") as f:
            json.dump(rules_config, f, indent=2, ensure_ascii=False)

    def update_last_update_time(self):
        """Update the last update timestamp in config"""
        config = self.load_config()
        config["last_update"] = datetime.now().timestamp()
        self.save_config(config)
        return config["last_update"]
    
    def need_update(self) -> bool:
        """检查是否需要更新配置
        
        Returns:
            bool: True 表示需要更新，False 表示不需要更新
        """
        config = self.load_config()
        last_update = config.get("last_update")
        update_interval = config.get("update_interval", 3600)
        
        # 如果没有上次更新时间,需要更新
        if not last_update:
            return True
            
        now = datetime.now().timestamp()
        # 如果当前时间大于上次更新时间+更新间隔,需要更新
        return (last_update + update_interval) < now


# Create a singleton instance
config_manager = ConfigManager() 