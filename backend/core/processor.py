import os
import time
from pathlib import Path
from typing import Optional, Dict, Any
from dataclasses import dataclass
from PIL import Image, ImageFilter, ImageEnhance

# Import core modules
from backend.core.format_selector import SmartFormatSelector

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

def process_image_worker(task: ProcessingTask) -> ProcessingResult:
    """Worker function for image processing"""
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
            
            # Ensure target parent directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
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
