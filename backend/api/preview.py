from io import BytesIO
from flask import request, send_file, jsonify
from PIL import Image, ImageFilter, ImageEnhance
from backend.api.routes import api_bp
from backend.core.db import files_col
from backend.core.format_selector import SmartFormatSelector
from backend.core.processor import resize_image

@api_bp.route('/preview/<file_id>', methods=['GET'])
def get_preview(file_id):
    """Generate in-memory preview image with specified settings"""
    info = files_col.find_one({'_id': file_id})
    if not info:
        return jsonify({'error': 'File not found'}), 404
    file_path = info['path']
        
    # Check if original is requested directly
    if request.args.get('original', 'false').lower() == 'true':
        return send_file(str(file_path))
        
    # Parse settings from query parameters
    try:
        quality = int(request.args.get('quality', 85))
        output_format = request.args.get('output_format', 'jpg')
        
        target_width = request.args.get('target_width')
        target_width = int(target_width) if target_width else None
        
        target_height = request.args.get('target_height')
        target_height = int(target_height) if target_height else None
        
        maintain_aspect = request.args.get('maintain_aspect', 'true').lower() == 'true'
        smart_format = request.args.get('smart_format', 'true').lower() == 'true'
        
        sharpen = int(request.args.get('sharpen', 0))
        blur = float(request.args.get('blur', 0))
        brightness = float(request.args.get('brightness', 1.0))
        contrast = float(request.args.get('contrast', 1.0))
        
        settings = {
            'quality': quality,
            'output_format': output_format,
            'target_width': target_width,
            'target_height': target_height,
            'maintain_aspect': maintain_aspect,
            'smart_format': smart_format,
            'sharpen': sharpen,
            'blur': blur,
            'brightness': brightness,
            'contrast': contrast
        }
    except Exception as e:
        return jsonify({'error': f'Invalid query parameters: {e}'}), 400
        
    try:
        with Image.open(file_path) as img:
            # Process in-memory
            # Convert RGBA to RGB if saving as JPG
            if settings.get('output_format') == 'jpg' and img.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode in ('RGBA', 'LA') else None)
                img = background
            elif img.mode not in ('RGB', 'RGBA', 'L'):
                img = img.convert('RGB')
                
            # Resize
            if settings.get('target_width') or settings.get('target_height'):
                img = resize_image(img, settings)
                
            # Filters
            if settings.get('sharpen', 0) > 0:
                for _ in range(settings['sharpen']):
                    img = img.filter(ImageFilter.SHARPEN)
            if settings.get('blur', 0) > 0:
                img = img.filter(ImageFilter.GaussianBlur(settings['blur']))
                
            # Contrast/brightness
            if settings.get('brightness', 1.0) != 1.0:
                img = ImageEnhance.Brightness(img).enhance(settings['brightness'])
            if settings.get('contrast', 1.0) != 1.0:
                img = ImageEnhance.Contrast(img).enhance(settings['contrast'])
                
            # Smart Format selection
            final_format = settings.get('output_format', 'jpg')
            if settings.get('smart_format', False):
                final_format = SmartFormatSelector.select_format(img, final_format)
                
            # Save to memory buffer
            buffered = BytesIO()
            save_kwargs = {'quality': settings.get('quality', 85), 'optimize': True}
            
            if final_format == 'jpg':
                save_kwargs['format'] = 'JPEG'
                mimetype = 'image/jpeg'
            elif final_format == 'webp':
                save_kwargs['format'] = 'WEBP'
                save_kwargs['method'] = 6
                mimetype = 'image/webp'
            elif final_format == 'png':
                save_kwargs['format'] = 'PNG'
                save_kwargs['compress_level'] = 9
                mimetype = 'image/png'
            else:
                save_kwargs['format'] = 'JPEG'
                mimetype = 'image/jpeg'
                
            img.save(buffered, **save_kwargs)
            buffered.seek(0)
            
            return send_file(buffered, mimetype=mimetype)
            
    except Exception as e:
        return jsonify({'error': f'Preview processing failed: {e}'}), 500
