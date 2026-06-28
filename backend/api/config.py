from flask import request, jsonify
from backend.api.routes import api_bp
from backend.core.config_manager import ConfigManager

config_manager = ConfigManager()

@api_bp.route('/config', methods=['GET'])
def get_config():
    """Get saved user configurations"""
    return jsonify(config_manager.config)

@api_bp.route('/config', methods=['PUT'])
def update_config():
    """Update user configurations"""
    data = request.json or {}
    config_manager.update(data)
    return jsonify({'success': True, 'config': config_manager.config})
