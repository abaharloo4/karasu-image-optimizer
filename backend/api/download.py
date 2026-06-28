import io
import zipfile
from pathlib import Path
from flask import send_file, jsonify
from backend.api.routes import api_bp
from backend.core.db import files_col, jobs_col
from backend.config import Config

@api_bp.route('/download/<file_id>', methods=['GET'])
def download_file(file_id):
    """Download a single optimized image"""
    info = files_col.find_one({'_id': file_id})
    if not info:
        return jsonify({'error': 'File not found'}), 404
    if 'output_path' not in info:
        return jsonify({'error': 'File not processed yet'}), 400
    output_path = info['output_path']
        
    path_obj = Path(output_path)
    if not path_obj.exists():
        return jsonify({'error': 'Processed file missing from disk'}), 404
        
    return send_file(str(path_obj), as_attachment=True, download_name=path_obj.name)

@api_bp.route('/download/zip/<job_id>', methods=['GET'])
def download_zip(job_id):
    """Download all optimized images of a job in a ZIP archive"""
    job = jobs_col.find_one({'_id': job_id})
    if not job:
        return jsonify({'error': 'Job not found'}), 404
            
    # Locate output directory for this job
    output_dir = Config.OUTPUT_FOLDER / job_id
    if not output_dir.exists():
        return jsonify({'error': 'No output folder found for this job'}), 404
        
    files = list(output_dir.glob('*.*'))
    if not files:
        return jsonify({'error': 'No output files found to zip'}), 404
        
    # Create ZIP archive in memory
    memory_file = io.BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for file_path in files:
            zip_file.write(str(file_path), file_path.name)
            
    memory_file.seek(0)
    
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name=f'optimized_images_{job_id[:8]}.zip'
    )
