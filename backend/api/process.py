import threading
import uuid
from pathlib import Path
from flask import request, jsonify
from backend.api.routes import api_bp
from backend.config import Config
from backend.core.db import files_col, jobs_col
from backend.core.batch import BatchProcessor
from backend.core.processor import ProcessingTask, ProcessingResult

def run_batch_processing(job_id, tasks, use_cache, max_workers):
    """Background processing thread function using MongoDB persistence"""
    processor = BatchProcessor(max_workers=max_workers, use_cache=use_cache)
    
    completed_count = 0
    total_count = len(tasks)
    
    def result_callback(result: ProcessingResult):
        nonlocal completed_count
        completed_count += 1
        
        # Find which file_id this result belongs to
        matched_file_id = None
        try:
            # Query by path (stored as string in MongoDB)
            file_info = files_col.find_one({'path': str(result.file_path)})
            if file_info:
                matched_file_id = file_info['_id']
                if result.success and result.output_path:
                    files_col.update_one(
                        {'_id': matched_file_id},
                        {'$set': {'output_path': str(result.output_path)}}
                    )
        except Exception as e:
            print(f"Error updating file path in MongoDB: {e}")
                    
        result_dict = {
            'file_id': matched_file_id,
            'name': result.file_path.name,
            'success': result.success,
            'original_size': result.original_size,
            'new_size': result.new_size,
            'compression_ratio': result.compression_ratio,
            'processing_time': result.processing_time,
            'error': result.error
        }
        
        try:
            # Push result and update progress in MongoDB
            jobs_col.update_one(
                {'_id': job_id},
                {
                    '$push': {'results': result_dict},
                    '$set': {
                        'progress': completed_count,
                        'status': 'done' if completed_count >= total_count else 'processing'
                    }
                }
            )
        except Exception as e:
            print(f"Error updating job status in MongoDB: {e}")
                
    try:
        processor.process_batch(tasks, result_callback=result_callback)
    except Exception as e:
        try:
            jobs_col.update_one(
                {'_id': job_id},
                {'$set': {'status': 'error', 'error': str(e)}}
            )
        except Exception as db_err:
            print(f"Failed to set job error in database: {db_err}")

@api_bp.route('/process', methods=['POST'])
def start_processing():
    """Start batch processing of images"""
    data = request.json or {}
    file_ids = data.get('file_ids', [])
    settings = data.get('settings', {})
    
    if not file_ids:
        return jsonify({'error': 'No file_ids provided'}), 400
        
    job_id = uuid.uuid4().hex
    
    # Prepare tasks
    tasks = []
    invalid_ids = []
    
    for idx, file_id in enumerate(file_ids):
        # Query file info from MongoDB
        info = files_col.find_one({'_id': file_id})
        if not info:
            invalid_ids.append(file_id)
            continue
            
        file_path = Path(info['path'])
        
        # Create a path inside outputs/<job_id>
        output_name = file_path.name
        output_path = Config.OUTPUT_FOLDER / job_id / output_name
        
        task = ProcessingTask(
            file_path=file_path,
            output_path=output_path,
            settings=settings,
            index=idx + 1,
            total=len(file_ids)
        )
        tasks.append(task)
            
    if invalid_ids:
        return jsonify({'error': f'Invalid file_ids: {invalid_ids}'}), 400
        
    # Initialize job in MongoDB
    jobs_col.insert_one({
        '_id': job_id,
        'status': 'processing',
        'progress': 0,
        'total': len(tasks),
        'results': []
    })
        
    # Read batch execution settings
    max_workers = settings.get('max_workers', 4)
    use_cache = settings.get('use_cache', True)
    
    # Run processing in background thread
    thread = threading.Thread(target=run_batch_processing, args=(job_id, tasks, use_cache, max_workers))
    thread.daemon = True
    thread.start()
    
    return jsonify({'job_id': job_id})
