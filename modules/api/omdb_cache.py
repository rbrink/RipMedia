import os
import yaml

from config import Config

class OMDBCache:
    def __init__(self):
        os.makedirs(Config.get('Cache Directory'), exist_ok=True)
        self.cache_path = f"{Config.get('Cache Directory')}/omdb_cache.yaml"
        self.cache = self.load()
    
    def load(self):
        if os.path.exists(self.cache_path):
            with open(self.cache_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}
    
    def save(self):
        with open(self.cache_path, "w", encoding="utf-8") as f:
            yaml.dump(self.cache, f, allow_unicode=True)
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, data):
        self.cache[key] = data
        self.save()
