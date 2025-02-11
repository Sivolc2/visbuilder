from flask import Blueprint, jsonify, current_app, url_for, render_template
import psutil
import datetime
from typing import Dict, List, Any

status_routes = Blueprint('status', __name__)

def get_endpoint_details() -> List[Dict[str, Any]]:
    """Get details of all registered endpoints"""
    endpoints = []
    
    # Get all registered rules
    for rule in current_app.url_map.iter_rules():
        if rule.endpoint.startswith(('static', 'status')):
            continue
            
        endpoints.append({
            'endpoint': rule.rule,
            'methods': list(rule.methods - {'HEAD', 'OPTIONS'}),
            'description': current_app.view_functions[rule.endpoint].__doc__ or 'No description available'
        })
    
    return endpoints

@status_routes.route('/status', methods=['GET'])
def status_page():
    """Render the API documentation page"""
    try:
        # Get system metrics and API information
        status_data = get_status().get_json()
        datasets_data = get_datasets().get_json()
        
        return render_template('api_docs.html', 
                             status=status_data,
                             datasets=datasets_data)
    except Exception as e:
        return f"Error loading documentation: {str(e)}", 500

@status_routes.route('/api/status', methods=['GET'])
def get_status():
    """Get system status and available datasets"""
    try:
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # Available datasets info
        datasets = [
            {
                'id': 'traffic_api',
                'name': 'Real-time Traffic Data',
                'type': 'geospatial',
                'description': 'Real-time traffic congestion and route information',
                'update_frequency': 'Real-time',
                'sample_fields': ['start_point', 'end_point', 'congestion_level']
            },
            {
                'id': 'historical_data',
                'name': 'Historical Traffic Data',
                'type': 'time-series',
                'description': 'Historical traffic volume and congestion distribution',
                'update_frequency': 'Daily',
                'sample_fields': ['timestamps', 'volume', 'congestion_distribution']
            }
        ]
        
        # Get all API endpoints
        api_endpoints = get_endpoint_details()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.datetime.now().isoformat(),
            'system': {
                'cpu_usage_percent': cpu_percent,
                'memory_usage_percent': memory.percent,
                'memory_available_mb': memory.available // (1024 * 1024)
            },
            'datasets': datasets,
            'api_endpoints': api_endpoints
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@status_routes.route('/api/datasets', methods=['GET'])
def get_datasets():
    """Get information about available datasets"""
    try:
        datasets = [
            {
                'id': 'traffic_api',
                'name': 'Real-time Traffic Data',
                'type': 'geospatial',
                'description': 'Real-time traffic congestion and route information',
                'endpoints': [
                    {'path': '/api/data/traffic_api', 'method': 'GET', 'description': 'Get real-time traffic data'},
                    {'path': '/api/data/traffic_api/columns', 'method': 'GET', 'description': 'Get traffic data columns'},
                    {'path': '/api/data/traffic_api/filtered', 'method': 'POST', 'description': 'Get filtered traffic data'}
                ],
                'sample_fields': ['start_point', 'end_point', 'congestion_level'],
                'update_frequency': 'Real-time'
            },
            {
                'id': 'historical_data',
                'name': 'Historical Traffic Data',
                'type': 'time-series',
                'description': 'Historical traffic volume and congestion distribution',
                'endpoints': [
                    {'path': '/api/data/historical_data', 'method': 'GET', 'description': 'Get historical traffic data'},
                    {'path': '/api/data/historical_data/columns', 'method': 'GET', 'description': 'Get historical data columns'},
                    {'path': '/api/data/historical_data/filtered', 'method': 'POST', 'description': 'Get filtered historical data'}
                ],
                'sample_fields': ['timestamps', 'volume', 'congestion_distribution'],
                'update_frequency': 'Daily'
            }
        ]
        
        return jsonify(datasets)
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

@status_routes.route('/health')
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'visbuilder-backend'
    }), 200 