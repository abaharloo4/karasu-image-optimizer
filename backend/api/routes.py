from flask import Blueprint

api_bp = Blueprint('api', __name__)

# Define basic health check route
@api_bp.route('/health', methods=['GET'])
def health():
    return {'status': 'healthy', 'message': 'Karasu Image Optimizer API is running'}

# Import sub-modules to register routes
from backend.api import upload, process, preview, presets, config, stats, download, history
