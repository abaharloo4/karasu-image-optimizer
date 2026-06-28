import json
import hashlib
import time
import threading
from pathlib import Path
from typing import Dict, Tuple, Optional
from PIL import Image

class ImageCache:
    """LRU cache for processed images"""
    
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.cache: Dict[str, Tuple[Image.Image, float]] = {}
        self.access_times: Dict[str, float] = {}
        self.lock = threading.Lock()
    
    def _generate_key(self, file_path: Path, settings: dict) -> str:
        """Generate cache key from file path and settings"""
        settings_str = json.dumps(settings, sort_keys=True)
        key_str = f"{file_path}:{settings_str}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get(self, file_path: Path, settings: dict) -> Optional[Image.Image]:
        """Get cached image"""
        with self.lock:
            key = self._generate_key(file_path, settings)
            if key in self.cache:
                self.access_times[key] = time.time()
                return self.cache[key][0].copy()
            return None
    
    def put(self, file_path: Path, settings: dict, image: Image.Image):
        """Put image in cache"""
        with self.lock:
            if len(self.cache) >= self.max_size:
                self._evict_oldest()
            
            key = self._generate_key(file_path, settings)
            self.cache[key] = (image.copy(), time.time())
            self.access_times[key] = time.time()
    
    def _evict_oldest(self):
        """Evict least recently used item"""
        if not self.access_times:
            return
        
        oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
        if oldest_key in self.cache:
            self.cache[oldest_key][0].close()
            del self.cache[oldest_key]
        del self.access_times[oldest_key]
    
    def clear(self):
        """Clear all cached images"""
        with self.lock:
            for img, _ in self.cache.values():
                img.close()
            self.cache.clear()
            self.access_times.clear()
