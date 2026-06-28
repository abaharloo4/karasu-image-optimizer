from PIL import Image

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
        if user_format != 'auto' and user_format is not None:
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
