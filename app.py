"""
Karasu Image Optimizer v4.1 Ultra Professional Edition
Advanced image optimization tool with GPU acceleration, smart compression, and modern UI
"""

import os
import sys
import json
import threading
import queue
import time
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any
from collections import defaultdict
from dataclasses import dataclass, asdict
import customtkinter as ctk
from tkinter import filedialog, messagebox, Canvas, StringVar, IntVar, DoubleVar, BooleanVar
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import piexif
import piexif.helper
import numpy as np
import tkinter as tk
from tkinter import ttk
import cv2
import tempfile
import pyglet
from pathlib import Path
from PIL import ImageFont
import pyglet

# Try to import GPU acceleration libraries
try:
    import cv2
    GPU_AVAILABLE = cv2.cuda.getCudaEnabledDeviceCount() > 0
except:
    GPU_AVAILABLE = False

# ==================== Font Manager ====================
class FontManager:
    """Manages YekanBakh font loading"""
    
    _instance = None
    _fonts = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.font_dir = Path(__file__).parent / "fonts"
            if not self.font_dir.exists():
                self.font_dir = Path(__file__).parent / "frontend" / "public" / "fonts"
            self.font_path = self.font_dir / "YekanBakh-Regular.ttf"
            self.font_bold_path = self.font_dir / "YekanBakh-Bold.ttf"
            self.initialized = True
            self._load_fonts()
    
    def _load_fonts(self):
        """Load YekanBakh fonts"""
        try:
            # ثبت فونت‌ها با pyglet
            if self.font_path.exists():
                pyglet.font.add_file(str(self.font_path))
                self._fonts['regular'] = "YekanBakh"
            else:
                self._fonts['regular'] = "Segoe UI"
            
            if self.font_bold_path.exists():
                pyglet.font.add_file(str(self.font_bold_path))
                self._fonts['bold'] = "YekanBakh"
            else:
                self._fonts['bold'] = "Segoe UI"
                
            print(f"Fonts loaded: {self._fonts}")
        except Exception as e:
            print(f"Font loading error: {e}")
            self._fonts['regular'] = "Segoe UI"
            self._fonts['bold'] = "Segoe UI"
    
    def get_font(self, size: int = 12, bold: bool = False) -> tuple:
        """Get font tuple for tkinter/customtkinter"""
        font_name = self._fonts.get('bold' if bold else 'regular', 'Segoe UI')
        weight = "bold" if bold else "normal"
        return (font_name, size, weight)
    
    def get_pil_font(self, size: int = 12, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get PIL font for image drawing"""
        try:
            font_path = self.font_bold_path if bold else self.font_path
            if font_path.exists():
                return ImageFont.truetype(str(font_path), size)
        except:
            pass
        return ImageFont.load_default()
    
# Global font manager instance
font_manager = FontManager()

# ==================== Constants ====================
VERSION = "4.1.0"
APP_NAME = "Karasu Image Optimizer"

PRESETS = {
    "web_optimized": {
        "name": "بهینه وب",
        "target_width": 1920,
        "target_height": None,
        "quality": 85,
        "output_format": "webp",
        "maintain_aspect": True,
        "sharpen": 1,
        "preserve_exif": False
    },
    "mobile_optimized": {
        "name": "بهینه موبایل",
        "target_width": 1080,
        "target_height": None,
        "quality": 80,
        "output_format": "webp",
        "maintain_aspect": True,
        "sharpen": 0,
        "preserve_exif": False
    },
    "thumbnail": {
        "name": "تامبنیل",
        "target_width": 400,
        "target_height": 400,
        "quality": 75,
        "output_format": "jpg",
        "maintain_aspect": True,
        "sharpen": 1,
        "preserve_exif": False
    },
    "max_compression": {
        "name": "فشرده‌سازی حداکثر",
        "target_width": None,
        "target_height": None,
        "quality": 65,
        "output_format": "webp",
        "maintain_aspect": True,
        "sharpen": 0,
        "preserve_exif": False
    },
    "high_quality": {
        "name": "کیفیت بالا",
        "target_width": None,
        "target_height": None,
        "quality": 95,
        "output_format": "png",
        "maintain_aspect": True,
        "sharpen": 0,
        "preserve_exif": True
    },
    "social_media": {
        "name": "شبکه‌های اجتماعی",
        "target_width": 1200,
        "target_height": 1200,
        "quality": 85,
        "output_format": "jpg",
        "maintain_aspect": True,
        "sharpen": 1,
        "preserve_exif": False
    }
}

# ==================== Data Classes ====================
@dataclass
class ProcessingTask:
    """Data class for processing tasks"""
    file_path: Path
    output_path: Path
    settings: Dict[str, Any]
    index: int
    total: int

@dataclass
class ProcessingResult:
    """Data class for processing results"""
    success: bool
    file_path: Path
    output_path: Optional[Path]
    error: Optional[str]
    original_size: int
    new_size: int
    compression_ratio: float
    processing_time: float

# ==================== Configuration Manager ====================
class ConfigManager:
    """Manages application configuration and user preferences"""
    
    def __init__(self):
        self.config_dir = Path.home() / ".image_optimizer_pro"
        self.config_file = self.config_dir / "config.json"
        self.config_dir.mkdir(exist_ok=True)
        self.default_config = {
            "theme": "dark",
            "language": "fa",
            "last_input_path": "",
            "last_output_path": "",
            "recent_presets": [],
            "window_geometry": "1400x900",
            "use_gpu": False,
            "max_workers": os.cpu_count() or 4,
            "auto_backup": True,
            "show_comparison": True,
            "output_format": "webp",
            "quality": 85,
            "maintain_aspect": True,
            "smart_format": True,
            "cache_enabled": True,
            "auto_preview": False
        }
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return {**self.default_config, **json.load(f)}
        except Exception as e:
            print(f"Error loading config: {e}")
        return self.default_config.copy()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
        self.save_config()
# ==================== Image Cache ====================
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

# ==================== Smart Format Selector ====================
class SmartFormatSelector:
    """Intelligently selects the best output format based on image characteristics"""
    
    @staticmethod
    def analyze_image(img: Image.Image) -> dict:
        """Analyze image characteristics"""
        has_transparency = img.mode in ('RGBA', 'LA', 'P') and (
            img.mode == 'P' and 'transparency' in img.info or
            img.mode in ('RGBA', 'LA')
        )
        
        # Count unique colors (sample for large images)
        if img.size[0] * img.size[1] > 1000000:
            img_sample = img.resize((500, 500), Image.Resampling.LANCZOS)
        else:
            img_sample = img
        
        colors = len(img_sample.getcolors(maxcolors=10000) or [])
        
        return {
            'has_transparency': has_transparency,
            'color_count': colors,
            'width': img.size[0],
            'height': img.size[1],
            'mode': img.mode
        }
    
    @staticmethod
    def select_format(img: Image.Image, user_format: str = 'auto') -> str:
        """Select best format based on image analysis"""
        if user_format != 'auto':
            return user_format
        
        analysis = SmartFormatSelector.analyze_image(img)
        
        # PNG for transparency
        if analysis['has_transparency']:
            return 'png'
        
        # PNG for images with few colors (like screenshots, diagrams)
        if analysis['color_count'] < 256:
            return 'png'
        
        # WebP for modern web optimization
        if analysis['width'] * analysis['height'] > 500000:
            return 'webp'
        
        # JPG for photos
        return 'jpg'

# ==================== Image Processor ====================
def process_image_worker(task: ProcessingTask) -> ProcessingResult:
    """Worker function for image processing (top-level for pickling)"""
    start_time = time.time()
    
    try:
        file_path = task.file_path
        output_path = task.output_path
        settings = task.settings
        
        # Get original file size
        original_size = file_path.stat().st_size
        
        # Open image
        with Image.open(file_path) as img:
            # Convert RGBA to RGB if saving as JPG
            if settings.get('output_format') == 'jpg' and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')
            
            # Store EXIF data
            exif_data = None
            if settings.get('preserve_exif', False):
                try:
                    exif_data = img.info.get('exif')
                except:
                    pass
            
            # Resize if needed
            if settings.get('target_width') or settings.get('target_height'):
                img = resize_image(img, settings)
            
            # Apply filters
            if settings.get('sharpen', 0) > 0:
                for _ in range(settings['sharpen']):
                    img = img.filter(ImageFilter.SHARPEN)
            
            if settings.get('blur', 0) > 0:
                img = img.filter(ImageFilter.GaussianBlur(settings['blur']))
            
            # Adjust brightness
            if settings.get('brightness', 1.0) != 1.0:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(settings['brightness'])
            
            # Adjust contrast
            if settings.get('contrast', 1.0) != 1.0:
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(settings['contrast'])
            
            # Smart format selection
            output_format = settings.get('output_format', 'jpg')
            if settings.get('smart_format', False):
                output_format = SmartFormatSelector.select_format(img, output_format)
            
            # Update output path extension
            output_path = output_path.with_suffix(f'.{output_format}')
            
            # Save image
            save_kwargs = {'quality': settings.get('quality', 85), 'optimize': True}
            
            if output_format == 'jpg':
                save_kwargs['format'] = 'JPEG'
                if exif_data:
                    save_kwargs['exif'] = exif_data
            elif output_format == 'webp':
                save_kwargs['format'] = 'WEBP'
                save_kwargs['method'] = 6
            elif output_format == 'png':
                save_kwargs['format'] = 'PNG'
                save_kwargs['compress_level'] = 9
            
            img.save(output_path, **save_kwargs)
        
        # Get new file size
        new_size = output_path.stat().st_size
        compression_ratio = ((original_size - new_size) / original_size * 100) if original_size > 0 else 0
        processing_time = time.time() - start_time
        
        return ProcessingResult(
            success=True,
            file_path=file_path,
            output_path=output_path,
            error=None,
            original_size=original_size,
            new_size=new_size,
            compression_ratio=compression_ratio,
            processing_time=processing_time
        )
    
    except Exception as e:
        processing_time = time.time() - start_time
        return ProcessingResult(
            success=False,
            file_path=task.file_path,
            output_path=None,
            error=str(e),
            original_size=0,
            new_size=0,
            compression_ratio=0,
            processing_time=processing_time
        )

def resize_image(img: Image.Image, settings: dict) -> Image.Image:
    """Resize image based on settings"""
    target_width = settings.get('target_width')
    target_height = settings.get('target_height')
    maintain_aspect = settings.get('maintain_aspect', True)
    
    if not target_width and not target_height:
        return img
    
    original_width, original_height = img.size
    
    if maintain_aspect:
        if target_width and target_height:
            ratio = min(target_width / original_width, target_height / original_height)
        elif target_width:
            ratio = target_width / original_width
        else:
            ratio = target_height / original_height
        
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)
    else:
        new_width = target_width or original_width
        new_height = target_height or original_height
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)

# ==================== Batch Processor ====================
class BatchProcessor:
    """Handles batch image processing with threading"""
    
    def __init__(self, max_workers: int = 4, use_cache: bool = True):
        self.max_workers = max_workers
        self.use_cache = use_cache
        self.cache = ImageCache() if use_cache else None
        self.is_cancelled = False
        self.current_threads: List[threading.Thread] = []
        self.results_queue = queue.Queue()
        self.tasks_queue = queue.Queue()
    
    def process_batch(self, tasks: List[ProcessingTask], 
                     progress_callback=None, 
                     result_callback=None):
        """Process batch of images"""
        self.is_cancelled = False
        
        # Add tasks to queue
        for task in tasks:
            self.tasks_queue.put(task)
        
        # Create worker threads
        threads = []
        for _ in range(min(self.max_workers, len(tasks))):
            thread = threading.Thread(target=self._worker, 
                                    args=(progress_callback, result_callback))
            thread.daemon = True
            thread.start()
            threads.append(thread)
        
        self.current_threads = threads
        
        # Wait for completion
        for thread in threads:
            thread.join()
    
    def _worker(self, progress_callback=None, result_callback=None):
        """Worker thread function"""
        while not self.is_cancelled:
            try:
                task = self.tasks_queue.get(timeout=0.1)
            except queue.Empty:
                break
            
            # Check cache
            cached_result = None
            if self.use_cache and self.cache:
                cached_img = self.cache.get(task.file_path, task.settings)
                if cached_img:
                    # Use cached image
                    try:
                        output_format = task.settings.get('output_format', 'jpg')
                        output_path = task.output_path.with_suffix(f'.{output_format}')
                        
                        save_kwargs = {'quality': task.settings.get('quality', 85), 'optimize': True}
                        if output_format == 'jpg':
                            save_kwargs['format'] = 'JPEG'
                        elif output_format == 'webp':
                            save_kwargs['format'] = 'WEBP'
                        elif output_format == 'png':
                            save_kwargs['format'] = 'PNG'
                        
                        cached_img.save(output_path, **save_kwargs)
                        
                        original_size = task.file_path.stat().st_size
                        new_size = output_path.stat().st_size
                        
                        cached_result = ProcessingResult(
                            success=True,
                            file_path=task.file_path,
                            output_path=output_path,
                            error=None,
                            original_size=original_size,
                            new_size=new_size,
                            compression_ratio=((original_size - new_size) / original_size * 100),
                            processing_time=0.01
                        )
                    except:
                        cached_result = None
            
            # Process image
            if cached_result:
                result = cached_result
            else:
                result = process_image_worker(task)
                
                # Cache successful result
                if result.success and self.use_cache and self.cache:
                    try:
                        with Image.open(result.output_path) as img:
                            self.cache.put(task.file_path, task.settings, img)
                    except:
                        pass
            
            # Callbacks
            if progress_callback:
                progress_callback(task.index, task.total)
            
            if result_callback:
                result_callback(result)
            
            self.tasks_queue.task_done()
    
    def cancel(self):
        """Cancel processing"""
        self.is_cancelled = True
        
        # Clear queue
        while not self.tasks_queue.empty():
            try:
                self.tasks_queue.get_nowait()
                self.tasks_queue.task_done()
            except queue.Empty:
                break
# ==================== Preset System ====================
class PresetManager:
    """Manages processing presets"""
    
    PRESETS = {
        'web_optimized': {
            'name': 'بهینه وب',
            'description': 'بهینه‌سازی برای وب با کیفیت متوسط',
            'settings': {
                'quality': 80,
                'output_format': 'webp',
                'target_width': 1920,
                'maintain_aspect': True,
                'smart_format': True
            }
        },
        'mobile_optimized': {
            'name': 'بهینه موبایل',
            'description': 'بهینه‌سازی برای موبایل با حجم کم',
            'settings': {
                'quality': 75,
                'output_format': 'webp',
                'target_width': 1080,
                'maintain_aspect': True,
                'smart_format': True
            }
        },
        'thumbnail': {
            'name': 'تصویر بندانگشتی',
            'description': 'ایجاد تصاویر کوچک',
            'settings': {
                'quality': 85,
                'output_format': 'jpg',
                'target_width': 300,
                'target_height': 300,
                'maintain_aspect': True
            }
        },
        'max_compression': {
            'name': 'فشرده‌سازی حداکثر',
            'description': 'کمترین حجم ممکن',
            'settings': {
                'quality': 60,
                'output_format': 'webp',
                'target_width': 1280,
                'maintain_aspect': True,
                'smart_format': True
            }
        },
        'high_quality': {
            'name': 'کیفیت بالا',
            'description': 'حفظ کیفیت با فشرده‌سازی کم',
            'settings': {
                'quality': 95,
                'output_format': 'png',
                'maintain_aspect': True,
                'preserve_exif': True
            }
        },
        'social_media': {
            'name': 'شبکه‌های اجتماعی',
            'description': 'بهینه برای اینستاگرام و توییتر',
            'settings': {
                'quality': 85,
                'output_format': 'jpg',
                'target_width': 1080,
                'target_height': 1080,
                'maintain_aspect': True
            }
        }
    }
    
    @classmethod
    def get_preset(cls, preset_name: str) -> Optional[dict]:
        """Get preset settings"""
        return cls.PRESETS.get(preset_name)
    
    @classmethod
    def get_preset_names(cls) -> List[str]:
        """Get list of preset names"""
        return list(cls.PRESETS.keys())
    
    @classmethod
    def get_preset_display_name(cls, preset_name: str) -> str:
        """Get display name for preset"""
        preset = cls.PRESETS.get(preset_name)
        return preset['name'] if preset else preset_name

# ==================== Config Manager ====================
class ConfigManager:
    """Manages application configuration"""
    
    def __init__(self, config_file: Path = Path.home() / '.image_optimizer_config.json'):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        return self.get_default_config()
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def get_default_config(self) -> dict:
        """Get default configuration"""
        return {
            'last_input_path': str(Path.home()),
            'last_output_path': str(Path.home() / 'optimized_images'),
            'quality': 85,
            'output_format': 'jpg',
            'maintain_aspect': True,
            'preserve_exif': False,
            'max_workers': 4,
            'use_cache': True,
            'theme': 'light',
            'window_geometry': '1000x700'
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

# ==================== Statistics Window ====================
class StatisticsWindow(tk.Toplevel):
    """Window for displaying processing statistics"""
    
    def __init__(self, parent, results: List[ProcessingResult]):
        super().__init__(parent)
        self.title("آمار پردازش")
        self.geometry("600x500")
        self.resizable(False, False)
        
        # Calculate statistics
        total = len(results)
        successful = sum(1 for r in results if r.success)
        failed = total - successful
        
        total_original = sum(r.original_size for r in results if r.success)
        total_new = sum(r.new_size for r in results if r.success)
        total_saved = total_original - total_new
        avg_compression = (total_saved / total_original * 100) if total_original > 0 else 0
        
        total_time = sum(r.processing_time for r in results)
        avg_time = total_time / total if total > 0 else 0
        
        # Create UI
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📊 آمار کامل پردازش", 
                               font=('YekanBakh', 16, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(main_frame, text="آمار کلی", padding="15")
        stats_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        stats = [
            ("تعداد کل فایل‌ها:", f"{total}"),
            ("موفق:", f"{successful} ✓", "green"),
            ("ناموفق:", f"{failed} ✗", "red" if failed > 0 else "gray"),
            ("", ""),
            ("حجم اصلی:", self.format_size(total_original)),
            ("حجم نهایی:", self.format_size(total_new)),
            ("حجم ذخیره شده:", self.format_size(total_saved), "blue"),
            ("میانگین فشرده‌سازی:", f"{avg_compression:.1f}%", "blue"),
            ("", ""),
            ("زمان کل:", f"{total_time:.2f} ثانیه"),
            ("میانگین زمان:", f"{avg_time:.3f} ثانیه"),
        ]
        
        for i, stat in enumerate(stats):
            if len(stat) == 2:
                label, value = stat
                color = "black"
            else:
                label, value, color = stat
            
            if label:
                row_frame = ttk.Frame(stats_frame)
                row_frame.pack(fill=tk.X, pady=2)
                
                ttk.Label(row_frame, text=label, font=('YekanBakh', 10)).pack(side=tk.RIGHT)
                ttk.Label(row_frame, text=value, font=('YekanBakh', 10, 'bold'),
                         foreground=color).pack(side=tk.LEFT)
        
        # Failed files list
        if failed > 0:
            failed_frame = ttk.LabelFrame(main_frame, text="فایل‌های ناموفق", padding="10")
            failed_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
            
            # Scrollable list
            list_frame = ttk.Frame(failed_frame)
            list_frame.pack(fill=tk.BOTH, expand=True)
            
            scrollbar = ttk.Scrollbar(list_frame)
            scrollbar.pack(side=tk.LEFT, fill=tk.Y)
            
            failed_list = tk.Listbox(list_frame, yscrollcommand=scrollbar.set,
                                    font=('YekanBakh', 9), height=8)
            failed_list.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
            scrollbar.config(command=failed_list.yview)
            
            for result in results:
                if not result.success:
                    failed_list.insert(tk.END, f"{result.file_path.name}: {result.error}")
        
        # Close button
        ttk.Button(main_frame, text="بستن", command=self.destroy).pack(pady=(10, 0))
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

# ==================== Live Preview Window ====================
class LivePreviewWindow(tk.Toplevel):
    """Window for live preview of image processing"""
    
    def __init__(self, parent, file_path: Path, settings: dict):
        super().__init__(parent)
        self.title("پیش‌نمایش زنده")
        self.geometry("900x700")
        
        self.file_path = file_path
        self.settings = settings
        self.original_img = None
        self.processed_img = None
        
        self.setup_ui()
        self.load_and_process()
    
    def setup_ui(self):
        """Setup UI"""
        main_frame = ttk.Frame(self, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        ttk.Label(main_frame, text=f"پیش‌نمایش: {self.file_path.name}",
                 font=('YekanBakh', 12, 'bold')).pack(pady=(0, 10))
        
        # Images frame
        images_frame = ttk.Frame(main_frame)
        images_frame.pack(fill=tk.BOTH, expand=True)
        
        # Original image
        original_frame = ttk.LabelFrame(images_frame, text="تصویر اصلی", padding="10")
        original_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.original_label = ttk.Label(original_frame)
        self.original_label.pack(fill=tk.BOTH, expand=True)
        
        self.original_info = ttk.Label(original_frame, text="", font=('YekanBakh', 9))
        self.original_info.pack(pady=(5, 0))
        
        # Processed image
        processed_frame = ttk.LabelFrame(images_frame, text="تصویر پردازش شده", padding="10")
        processed_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        self.processed_label = ttk.Label(processed_frame)
        self.processed_label.pack(fill=tk.BOTH, expand=True)
        
        self.processed_info = ttk.Label(processed_frame, text="", font=('YekanBakh', 9))
        self.processed_info.pack(pady=(5, 0))
        
        # Close button
        ttk.Button(main_frame, text="بستن", command=self.destroy).pack(pady=(10, 0))
    
    def load_and_process(self):
        """Load and process image"""
        try:
            # Load original
            self.original_img = Image.open(self.file_path)
            original_size = self.file_path.stat().st_size
            
            # Display original
            self.display_image(self.original_img, self.original_label)
            self.original_info.config(
                text=f"{self.original_img.size[0]}x{self.original_img.size[1]} | {self.format_size(original_size)}"
            )
            
            # Process image
            temp_output = Path(tempfile.gettempdir()) / f"preview_{self.file_path.name}"
            task = ProcessingTask(
                file_path=self.file_path,
                output_path=temp_output,
                settings=self.settings,
                index=0,
                total=1
            )
            
            result = process_image_worker(task)
            
            if result.success:
                self.processed_img = Image.open(result.output_path)
                self.display_image(self.processed_img, self.processed_label)
                
                compression = result.compression_ratio
                self.processed_info.config(
                    text=f"{self.processed_img.size[0]}x{self.processed_img.size[1]} | "
                         f"{self.format_size(result.new_size)} | "
                         f"فشرده‌سازی: {compression:.1f}%"
                )
                
                # Clean up temp file
                result.output_path.unlink()
            else:
                self.processed_info.config(text=f"خطا: {result.error}")
        
        except Exception as e:
            messagebox.showerror("خطا", f"خطا در بارگذاری تصویر:\n{str(e)}")
            self.destroy()
    
    def display_image(self, img: Image.Image, label: ttk.Label):
        """Display image in label"""
        # Resize for display
        display_img = img.copy()
        max_size = (400, 400)
        display_img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        photo = ImageTk.PhotoImage(display_img)
        label.config(image=photo)
        label.image = photo
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
# ==================== Main Application ====================
class ImageOptimizerApp:
    """Main application class"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Karasu Image Optimizer 4.1 Ultra Professional Edition")
        self.root.geometry("1000x700")
        
        # Load YekanBakh font
        self.load_fonts()
        
        # Initialize components
        self.config_manager = ConfigManager()
        self.batch_processor = BatchProcessor(
            max_workers=self.config_manager.get('max_workers', 4),
            use_cache=self.config_manager.get('use_cache', True)
        )
        
        # Variables
        self.input_path = tk.StringVar(value=self.config_manager.get('last_input_path', ''))
        self.output_path = tk.StringVar(value=self.config_manager.get('last_output_path', ''))
        self.quality = tk.IntVar(value=self.config_manager.get('quality', 85))
        self.output_format = tk.StringVar(value=self.config_manager.get('output_format', 'jpg'))
        self.target_width = tk.StringVar()
        self.target_height = tk.StringVar()
        self.maintain_aspect = tk.BooleanVar(value=self.config_manager.get('maintain_aspect', True))
        self.preserve_exif = tk.BooleanVar(value=self.config_manager.get('preserve_exif', False))
        self.smart_format = tk.BooleanVar(value=True)
        self.sharpen = tk.IntVar(value=0)
        self.blur = tk.IntVar(value=0)
        self.brightness = tk.DoubleVar(value=1.0)
        self.contrast = tk.DoubleVar(value=1.0)
        self.rename_pattern = tk.StringVar(value="{name}_optimized")
        self.selected_preset = tk.StringVar(value='')
        
        self.processing_results: List[ProcessingResult] = []
        self.is_processing = False
        
        # Setup UI
        self.setup_ui()
        
        # Setup drag and drop
        try:
            from tkinterdnd2 import DND_FILES, TkinterDnD
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
        except ImportError:
            print("tkinterdnd2 not available. Drag & drop disabled.")
        
        # Bind close event
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def load_fonts(self):
        """Load YekanBakh fonts"""
        fonts_dir = Path(__file__).parent / 'fonts'
        if fonts_dir.exists():
            for font_file in fonts_dir.glob('*.ttf'):
                try:
                    pyglet.font.add_file(str(font_file))
                except:
                    pass
    
    def setup_ui(self):
        """Setup user interface"""
        # Main container
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title
        title_frame = ttk.Frame(main_container)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(title_frame, text="🖼️ Karasu Image Optimizer 4.1 Ultra Professional",
                 font=('YekanBakh', 16, 'bold')).pack()
        ttk.Label(title_frame, text="بهینه‌ساز حرفه‌ای تصاویر با پردازش هوشمند",
                 font=('YekanBakh', 10)).pack()
        
        # Notebook for tabs
        notebook = ttk.Notebook(main_container)
        notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Basic Settings
        basic_tab = ttk.Frame(notebook, padding="10")
        notebook.add(basic_tab, text="تنظیمات اصلی")
        self.setup_basic_tab(basic_tab)
        
        # Tab 2: Advanced Settings
        advanced_tab = ttk.Frame(notebook, padding="10")
        notebook.add(advanced_tab, text="تنظیمات پیشرفته")
        self.setup_advanced_tab(advanced_tab)
        
        # Tab 3: Presets
        presets_tab = ttk.Frame(notebook, padding="10")
        notebook.add(presets_tab, text="پیش‌تنظیم‌ها")
        self.setup_presets_tab(presets_tab)
        
        # Progress frame
        self.progress_frame = ttk.LabelFrame(main_container, text="پیشرفت پردازش", padding="10")
        self.progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='determinate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_label = ttk.Label(self.progress_frame, text="آماده", font=('YekanBakh', 9))
        self.progress_label.pack()
        
        # Buttons frame
        buttons_frame = ttk.Frame(main_container)
        buttons_frame.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(buttons_frame, text="🚀 شروع پردازش", 
                  command=self.start_processing).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="⏹️ لغو", 
                  command=self.cancel_processing).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="👁️ پیش‌نمایش", 
                  command=self.show_preview).pack(side=tk.RIGHT, padx=2)
        ttk.Button(buttons_frame, text="📊 آمار", 
                  command=self.show_statistics).pack(side=tk.RIGHT, padx=2)
    
    def setup_basic_tab(self, parent):
        """Setup basic settings tab"""
        # Input/Output paths
        paths_frame = ttk.LabelFrame(parent, text="مسیرها", padding="10")
        paths_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Input
        input_frame = ttk.Frame(paths_frame)
        input_frame.pack(fill=tk.X, pady=5)
        ttk.Label(input_frame, text="ورودی:", width=15).pack(side=tk.RIGHT)
        ttk.Entry(input_frame, textvariable=self.input_path).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        ttk.Button(input_frame, text="انتخاب", command=self.browse_input).pack(side=tk.RIGHT)
        
        # Output
        output_frame = ttk.Frame(paths_frame)
        output_frame.pack(fill=tk.X, pady=5)
        ttk.Label(output_frame, text="خروجی:", width=15).pack(side=tk.RIGHT)
        ttk.Entry(output_frame, textvariable=self.output_path).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        ttk.Button(output_frame, text="انتخاب", command=self.browse_output).pack(side=tk.RIGHT)
        
        # Quality and Format
        quality_frame = ttk.LabelFrame(parent, text="کیفیت و فرمت", padding="10")
        quality_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quality slider
        quality_row = ttk.Frame(quality_frame)
        quality_row.pack(fill=tk.X, pady=5)
        ttk.Label(quality_row, text="کیفیت:", width=15).pack(side=tk.RIGHT)
        quality_value_label = ttk.Label(quality_row, text="85", width=5)
        quality_value_label.pack(side=tk.LEFT, padx=5)
        quality_slider = ttk.Scale(quality_row, from_=1, to=100, variable=self.quality, orient=tk.HORIZONTAL,
                                   command=lambda v: quality_value_label.config(text=f"{int(float(v))}"))
        quality_slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Format
        format_row = ttk.Frame(quality_frame)
        format_row.pack(fill=tk.X, pady=5)
        ttk.Label(format_row, text="فرمت خروجی:", width=15).pack(side=tk.RIGHT)
        formats = ['jpg', 'png', 'webp', 'auto']
        for fmt in formats:
            ttk.Radiobutton(format_row, text=fmt.upper(), variable=self.output_format, 
                           value=fmt).pack(side=tk.RIGHT, padx=5)
        
        # Smart format
        ttk.Checkbutton(quality_frame, text="انتخاب هوشمند فرمت", 
                       variable=self.smart_format).pack(anchor=tk.E, pady=5)
        
        # Resize
        resize_frame = ttk.LabelFrame(parent, text="تغییر اندازه", padding="10")
        resize_frame.pack(fill=tk.X, pady=(0, 10))
        
        size_row = ttk.Frame(resize_frame)
        size_row.pack(fill=tk.X, pady=5)
        ttk.Label(size_row, text="عرض:", width=10).pack(side=tk.RIGHT)
        ttk.Entry(size_row, textvariable=self.target_width, width=10).pack(side=tk.RIGHT, padx=5)
        ttk.Label(size_row, text="ارتفاع:", width=10).pack(side=tk.RIGHT, padx=(20, 0))
        ttk.Entry(size_row, textvariable=self.target_height, width=10).pack(side=tk.RIGHT, padx=5)
        
        ttk.Checkbutton(resize_frame, text="حفظ نسبت تصویر", 
                       variable=self.maintain_aspect).pack(anchor=tk.E, pady=5)
        
        # Options
        options_frame = ttk.LabelFrame(parent, text="گزینه‌ها", padding="10")
        options_frame.pack(fill=tk.X)
        
        ttk.Checkbutton(options_frame, text="حفظ اطلاعات EXIF", 
                       variable=self.preserve_exif).pack(anchor=tk.E, pady=2)
    
    def setup_advanced_tab(self, parent):
        """Setup advanced settings tab"""
        # Filters
        filters_frame = ttk.LabelFrame(parent, text="فیلترها", padding="10")
        filters_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Sharpen
        sharpen_row = ttk.Frame(filters_frame)
        sharpen_row.pack(fill=tk.X, pady=5)
        ttk.Label(sharpen_row, text="وضوح:", width=15).pack(side=tk.RIGHT)
        sharpen_value = ttk.Label(sharpen_row, text="0", width=5)
        sharpen_value.pack(side=tk.LEFT, padx=5)
        ttk.Scale(sharpen_row, from_=0, to=5, variable=self.sharpen, orient=tk.HORIZONTAL,
                 command=lambda v: sharpen_value.config(text=f"{int(float(v))}")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Blur
        blur_row = ttk.Frame(filters_frame)
        blur_row.pack(fill=tk.X, pady=5)
        ttk.Label(blur_row, text="محو:", width=15).pack(side=tk.RIGHT)
        blur_value = ttk.Label(blur_row, text="0", width=5)
        blur_value.pack(side=tk.LEFT, padx=5)
        ttk.Scale(blur_row, from_=0, to=10, variable=self.blur, orient=tk.HORIZONTAL,
                 command=lambda v: blur_value.config(text=f"{int(float(v))}")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Adjustments
        adjust_frame = ttk.LabelFrame(parent, text="تنظیمات رنگ", padding="10")
        adjust_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Brightness
        brightness_row = ttk.Frame(adjust_frame)
        brightness_row.pack(fill=tk.X, pady=5)
        ttk.Label(brightness_row, text="روشنایی:", width=15).pack(side=tk.RIGHT)
        brightness_value = ttk.Label(brightness_row, text="1.0", width=5)
        brightness_value.pack(side=tk.LEFT, padx=5)
        ttk.Scale(brightness_row, from_=0.5, to=2.0, variable=self.brightness, orient=tk.HORIZONTAL,
                 command=lambda v: brightness_value.config(text=f"{float(v):.1f}")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Contrast
        contrast_row = ttk.Frame(adjust_frame)
        contrast_row.pack(fill=tk.X, pady=5)
        ttk.Label(contrast_row, text="کنتراست:", width=15).pack(side=tk.RIGHT)
        contrast_value = ttk.Label(contrast_row, text="1.0", width=5)
        contrast_value.pack(side=tk.LEFT, padx=5)
        ttk.Scale(contrast_row, from_=0.5, to=2.0, variable=self.contrast, orient=tk.HORIZONTAL,
                 command=lambda v: contrast_value.config(text=f"{float(v):.1f}")).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Rename pattern
        rename_frame = ttk.LabelFrame(parent, text="الگوی نام‌گذاری", padding="10")
        rename_frame.pack(fill=tk.X)
        
        ttk.Label(rename_frame, text="الگو:", width=15).pack(side=tk.RIGHT)
        ttk.Entry(rename_frame, textvariable=self.rename_pattern).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=5)
        ttk.Label(rename_frame, text="{name}, {index}, {date}, {time}", 
                 font=('YekanBakh', 8), foreground='gray').pack(anchor=tk.E, pady=5)
    
    def setup_presets_tab(self, parent):
        """Setup presets tab"""
        ttk.Label(parent, text="پیش‌تنظیم‌های آماده", 
                 font=('YekanBakh', 12, 'bold')).pack(pady=(0, 10))
        
        presets_frame = ttk.Frame(parent)
        presets_frame.pack(fill=tk.BOTH, expand=True)
        
        for preset_name in PresetManager.get_preset_names():
            preset = PresetManager.get_preset(preset_name)
            
            preset_card = ttk.LabelFrame(presets_frame, text=preset['name'], padding="10")
            preset_card.pack(fill=tk.X, pady=5)
            
            ttk.Label(preset_card, text=preset['description'], 
                     font=('YekanBakh', 9)).pack(anchor=tk.E)
            
            ttk.Button(preset_card, text="اعمال", 
                      command=lambda p=preset_name: self.apply_preset(p)).pack(anchor=tk.W, pady=(5, 0))
    
    def apply_preset(self, preset_name: str):
        """Apply preset settings"""
        preset = PresetManager.get_preset(preset_name)
        if not preset:
            return
        
        settings = preset['settings']
        
        self.quality.set(settings.get('quality', 85))
        self.output_format.set(settings.get('output_format', 'jpg'))
        self.target_width.set(settings.get('target_width', ''))
        self.target_height.set(settings.get('target_height', ''))
        self.maintain_aspect.set(settings.get('maintain_aspect', True))
        self.preserve_exif.set(settings.get('preserve_exif', False))
        self.smart_format.set(settings.get('smart_format', False))
        
        messagebox.showinfo("موفق", f"پیش‌تنظیم '{preset['name']}' اعمال شد.")
    
    def browse_input(self):
        """Browse for input file or directory"""
        choice = messagebox.askyesno("انتخاب", "آیا می‌خواهید یک پوشه انتخاب کنید؟\n(خیر = انتخاب فایل)")
        
        if choice:
            path = filedialog.askdirectory(title="انتخاب پوشه ورودی")
        else:
            path = filedialog.askopenfilename(
                title="انتخاب فایل ورودی",
                filetypes=[
                    ("Image files", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                    ("All files", "*.*")
                ]
            )
        
        if path:
            self.input_path.set(path)
    
    def browse_output(self):
        """Browse for output directory"""
        path = filedialog.askdirectory(title="انتخاب پوشه خروجی")
        if path:
            self.output_path.set(path)
    
    def on_drop(self, event):
        """Handle drag and drop"""
        files = self.root.tk.splitlist(event.data)
        if files:
            self.input_path.set(files[0])
    
    def get_settings(self) -> dict:
        """Get current settings"""
        return {
            'quality': self.quality.get(),
            'output_format': self.output_format.get(),
            'target_width': int(self.target_width.get()) if self.target_width.get() else None,
            'target_height': int(self.target_height.get()) if self.target_height.get() else None,
            'maintain_aspect': self.maintain_aspect.get(),
            'preserve_exif': self.preserve_exif.get(),
            'smart_format': self.smart_format.get(),
            'sharpen': self.sharpen.get(),
            'blur': self.blur.get(),
            'brightness': self.brightness.get(),
            'contrast': self.contrast.get(),
        }
    
    def start_processing(self):
        """Start image processing"""
        if self.is_processing:
            messagebox.showwarning("هشدار", "پردازش در حال انجام است!")
            return
        
        input_path = Path(self.input_path.get())
        output_path = Path(self.output_path.get())
        
        if not input_path.exists():
            messagebox.showerror("خطا", "مسیر ورودی معتبر نیست!")
            return
        
        if not output_path.exists():
            output_path.mkdir(parents=True, exist_ok=True)
        
        # Collect files
        if input_path.is_file():
            files = [input_path]
        else:
            files = []
            for ext in ['*.jpg', '*.jpeg', '*.png', '*.webp', '*.bmp', '*.tiff', '*.tif']:
                files.extend(input_path.glob(ext))
                files.extend(input_path.glob(ext.upper()))
        
        if not files:
            messagebox.showwarning("هشدار", "هیچ فایل تصویری یافت نشد!")
            return
        
        # Create tasks
        settings = self.get_settings()
        tasks = []
        
        for i, file_path in enumerate(files):
            # Generate output filename
            pattern = self.rename_pattern.get() or "{name}_optimized"
            output_name = pattern.format(
                name=file_path.stem,
                index=i+1,
                date=datetime.now().strftime("%Y%m%d"),
                time=datetime.now().strftime("%H%M%S")
            )
            
            output_file = output_path / f"{output_name}{file_path.suffix}"
            
            tasks.append(ProcessingTask(
                file_path=file_path,
                output_path=output_file,
                settings=settings,
                index=i,
                total=len(files)
            ))
        
        # Start processing in thread
        self.is_processing = True
        self.processing_results = []
        self.progress_bar['maximum'] = len(tasks)
        self.progress_bar['value'] = 0
        
        threading.Thread(target=self._process_batch, args=(tasks,), daemon=True).start()
    
    def _process_batch(self, tasks: List[ProcessingTask]):
        """Process batch in background thread"""
        def progress_callback(index, total):
            self.root.after(0, self._update_progress, index + 1, total)
        
        def result_callback(result: ProcessingResult):
            self.processing_results.append(result)
        
        try:
            self.batch_processor.process_batch(tasks, progress_callback, result_callback)
            self.root.after(0, self._processing_complete)
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("خطا", f"خطا در پردازش:\n{str(e)}"))
            self.is_processing = False
    
    def _update_progress(self, current, total):
        """Update progress bar"""
        self.progress_bar['value'] = current
        self.progress_label.config(text=f"در حال پردازش: {current}/{total}")
    
    def _processing_complete(self):
        """Handle processing completion"""
        self.is_processing = False
        self.progress_label.config(text="پردازش کامل شد!")
        
        # Save config
        self.config_manager.update({
            'last_input_path': self.input_path.get(),
            'last_output_path': self.output_path.get(),
            'quality': self.quality.get(),
            'output_format': self.output_format.get(),
            'maintain_aspect': self.maintain_aspect.get(),
            'preserve_exif': self.preserve_exif.get(),
        })
        
        # Show results
        successful = sum(1 for r in self.processing_results if r.success)
        total = len(self.processing_results)
        
        messagebox.showinfo("تمام", f"پردازش کامل شد!\n\nموفق: {successful}/{total}")
        
        if total > 0:
            self.show_statistics()
    
    def cancel_processing(self):
        """Cancel processing"""
        if self.is_processing:
            self.batch_processor.cancel()
            self.is_processing = False
            self.progress_label.config(text="لغو شد")
            messagebox.showinfo("لغو", "پردازش لغو شد.")
    
    def show_preview(self):
        """Show live preview"""
        input_path = Path(self.input_path.get())
        
        if not input_path.exists() or not input_path.is_file():
            messagebox.showwarning("هشدار", "لطفاً یک فایل تصویر انتخاب کنید!")
            return
        
        settings = self.get_settings()
        LivePreviewWindow(self.root, input_path, settings)
    
    def show_statistics(self):
        """Show statistics window"""
        if not self.processing_results:
            messagebox.showinfo("اطلاعات", "هنوز پردازشی انجام نشده است!")
            return
        
        StatisticsWindow(self.root, self.processing_results)
    
    def on_close(self):
        """Handle window close"""
        if self.is_processing:
            if messagebox.askyesno("تأیید", "پردازش در حال انجام است. آیا می‌خواهید خارج شوید؟"):
                self.batch_processor.cancel()
                self.root.destroy()
        else:
            self.root.destroy()

# ==================== Main Entry Point ====================
def main():
    """Main entry point"""
    try:
        from tkinterdnd2 import TkinterDnD
        root = TkinterDnD.Tk()
    except ImportError:
        root = tk.Tk()
        print("Warning: tkinterdnd2 not installed. Drag & drop will be disabled.")
    
    app = ImageOptimizerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
