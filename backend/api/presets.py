from flask import jsonify
from backend.api.routes import api_bp
from backend.core.preset_manager import PresetManager

@api_bp.route('/presets', methods=['GET'])
def get_presets():
    """Get all presets"""
    return jsonify(PresetManager.PRESETS)
