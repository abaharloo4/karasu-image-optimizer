import uuid
import base64
from io import BytesIO
from pathlib import Path
from flask import request, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
from backend.api.routes import api_bp
from backend.config import Config
from backend.core.db import files_col

@api_bp.route('/upload', methods=['POST'])
def upload_files():
    """Upload one or more image files"""
    if 'files' not in request.files:
        return jsonify({'error': 'No files part in the request'}), 400
    
    files = request.files.getlist('files')
    results = []
    
    for file in files:
        if file.filename == '':
            continue
            
        filename = secure_filename(file.filename)
        file_id = uuid.uuid4().hex
        
        # Create folder for this file to avoid conflicts
        file_dir = Config.UPLOAD_FOLDER / file_id
        file_dir.mkdir(parents=True, exist_ok=True)
        file_path = file_dir / filename
        
        # Save original file
        file.save(str(file_path))
        
        # Get file size
        file_size = file_path.stat().st_size
        
        # Generate base64 thumbnail
        thumb_base64 = ""
        try:
            with Image.open(file_path) as img:
                # Keep aspect ratio for thumbnail
                img.thumbnail((100, 100))
                buffered = BytesIO()
                
                # Check for transparency to choose thumbnail format
                if img.mode in ('RGBA', 'LA', 'P'):
                    img.save(buffered, format="PNG")
                    thumb_type = "image/png"
                else:
                    img.save(buffered, format="JPEG")
                    thumb_type = "image/jpeg"
                    
                thumb_base64 = f"data:{thumb_type};base64," + base64.b64encode(buffered.getvalue()).decode('utf-8')
        except Exception as e:
            print(f"Thumbnail generation error for {filename}: {e}")
            
        files_col.insert_one({
            '_id': file_id,
            'path': str(file_path),
            'name': filename,
            'size': file_size
        })
            
        results.append({
            'id': file_id,
            'name': filename,
            'size': file_size,
            'thumb': thumb_base64
        })
        
    return jsonify(results)
