from flask import jsonify
from backend.api.routes import api_bp
from backend.core.db import jobs_col

@api_bp.route('/jobs/<job_id>', methods=['GET'])
def get_job_status(job_id):
    """Get status and results of a processing job from MongoDB"""
    job = jobs_col.find_one({'_id': job_id})
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    return jsonify(job)
