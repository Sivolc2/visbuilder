from flask import Blueprint, jsonify
from ..config.view_manager import ViewManager
import os

views_routes = Blueprint('views', __name__)
view_manager = ViewManager(os.getenv('CONFIG_DIR', 'app/config'))

# Start watching for config changes
view_manager.start_watching()

@views_routes.route('/api/views', methods=['GET'])
def get_views():
    """Get all available views"""
    try:
        views = view_manager.get_all_views()
        return jsonify(views)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@views_routes.route('/api/views/<view_id>', methods=['GET'])
def get_view(view_id):
    """Get a specific view configuration"""
    try:
        view = view_manager.get_view(view_id)
        if view is None:
            return jsonify({'error': 'View not found'}), 404
        return jsonify(view)
    except Exception as e:
        return jsonify({'error': str(e)}), 500 