from typing import List, Optional

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
