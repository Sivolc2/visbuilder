from flask import Blueprint, jsonify, request
import boto3
from botocore.exceptions import ClientError
import os
import importlib
from ..config.config_loader import ConfigLoader
from ..config.data_sources import DataSourceType
from ..data_processor import DataProcessor
import pandas as pd
import json
import requests
from typing import Any, Dict, List
from pathlib import Path
from ..mock_data import generate_traffic_data, generate_historical_data
import yaml

data_routes = Blueprint('data', __name__)
config_loader = ConfigLoader(os.getenv('CONFIG_DIR', 'app/config'))
data_processor = DataProcessor(
    datasets_dir=os.getenv('DATASETS_DIR', 'datasets'),
    processed_dir=os.getenv('PROCESSED_DIR', 'processed_data')
)

def initialize_data():
    """Initialize data processing on startup"""
    print("Initializing data processing...")
    try:
        # Get all data sources from config
        for config_file in Path(os.getenv('CONFIG_DIR', 'app/config')).glob('views/*.yaml'):
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                if not config or 'data_sources' not in config:
                    continue
                
                for source in config['data_sources']:
                    if source['type'] == DataSourceType.FILE:
                        data_processor.preprocess_dataset(
                            file_path=source['path'],
                            dataset_id=source['id']
                        )
        print("Data preprocessing complete")
    except Exception as e:
        print(f"Error during data initialization: {str(e)}")

def convert_to_geojson(df: pd.DataFrame, layer_config: Dict = None) -> Dict[str, Any]:
    """Convert DataFrame with lat/lon to GeoJSON format with optional aggregation"""
    if layer_config and 'aggregation' in layer_config:
        if layer_config['aggregation'] == 'heatmap':
            return create_heatmap_geojson(
                df,
                intensity_field=layer_config.get('properties', {}).get('intensity_field', 'Flight_Usage_Mbps'),
                resolution=layer_config.get('properties', {}).get('resolution', 8)
            )
        elif layer_config['aggregation'] == 'h3':
            return create_h3_grid_geojson(
                df,
                value_field=layer_config.get('properties', {}).get('value_field', 'Flight_Usage_Mbps'),
                resolution=layer_config.get('properties', {}).get('resolution', 8)
            )
    
    # Default point GeoJSON conversion
    features = []
    for _, row in df.iterrows():
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(row['Longitude']), float(row['Latitude'])]
            },
            "properties": {
                key: value for key, value in row.items() 
                if key not in ['Latitude', 'Longitude']
            }
        }
        features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def fetch_from_local(file_path: str, file_format: str = 'csv') -> Dict[str, Any]:
    """Fetch data from a local file"""
    try:
        # Get the absolute path to the datasets directory
        base_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
        datasets_dir = base_dir / 'datasets'
        full_path = datasets_dir / file_path

        # Ensure the path is within the datasets directory (security check)
        if not str(full_path.resolve()).startswith(str(datasets_dir.resolve())):
            raise ValueError("Access to files outside datasets directory is not allowed")

        if file_format.lower() == 'csv':
            df = pd.read_csv(full_path)
            return {'data': df.to_dict(orient='records')}
        elif file_format.lower() in ['json', 'jsonl']:
            with open(full_path, 'r') as f:
                return json.load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
    except Exception as e:
        print(f"Error reading local file: {str(e)}")
        raise

def fetch_from_s3(bucket: str, key: str, region: str = 'us-east-1') -> Dict[str, Any]:
    """Fetch data from S3 bucket"""
    try:
        s3_client = boto3.client('s3', region_name=region)
        response = s3_client.get_object(Bucket=bucket, Key=key)
        data = response['Body'].read().decode('utf-8')
        return json.loads(data)
    except ClientError as e:
        print(f"Error fetching from S3: {str(e)}")
        raise

@data_routes.route('/data/<source_id>', methods=['GET'])
def get_data(source_id: str):
    """Get data from a specific data source"""
    try:
        print(f"Processing data request for source: {source_id}")
        
        # For development with no AWS credentials, return mock data
        if os.getenv('FLASK_ENV') == 'development':
            if source_id == 'traffic_api':
                return jsonify(generate_traffic_data())
            elif source_id == 'historical_data':
                return jsonify(generate_historical_data())
        
        # In production, fetch from actual sources
        source_config = config_loader.load_data_source_config(source_id)
        if not source_config:
            print(f"Data source config not found for: {source_id}")
            return jsonify({'error': 'Data source not found'}), 404
            
        if source_config['type'] == DataSourceType.S3:
            data = fetch_from_s3(
                bucket=source_config['bucket'],
                key=source_config['key'],
                region=source_config.get('region', 'us-east-1')
            )
            return jsonify(data)
        elif source_config['type'] == DataSourceType.FILE:
            data = fetch_from_local(
                file_path=source_config['path'],
                file_format=source_config.get('format', 'csv')
            )
            print(f"Fetched data: {data.keys()}")  # Debug log
            return jsonify(data)
        elif source_config['type'] == DataSourceType.API:
            # Implement API fetching here
            pass
            
        return jsonify({'error': 'Data source type not implemented'}), 501
        
    except Exception as e:
        print(f"Error in get_data: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_routes.route('/config', methods=['GET'])
def get_config():
    """Get all configuration including layers, visualizations, and layout"""
    try:
        return jsonify(config_loader.load_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/layers', methods=['GET'])
def get_layers():
    """Get all layer configurations"""
    try:
        return jsonify(config_loader.load_layers())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/visualizations', methods=['GET'])
def get_visualizations():
    """Get all visualization configurations"""
    try:
        return jsonify(config_loader.load_visualizations())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/data/<source_id>/columns', methods=['GET'])
def get_columns(source_id: str):
    """Get column metadata for a specific data source"""
    try:
        if source_id == 'local_dataset':
            # Load the NDR dataset
            source_config = config_loader.load_data_source_config(source_id)
            if not source_config:
                return jsonify({'error': 'Data source not found'}), 404
                
            data = fetch_from_local(source_config['path'])
            df = pd.DataFrame(data['data'])
        elif source_id == 'traffic_api':
            data = generate_traffic_data()['metadata']
            df = pd.DataFrame(data)
        elif source_id == 'historical_data':
            data = generate_historical_data()['data']
            df = pd.DataFrame(data)
        else:
            return jsonify({'error': 'Data source not found'}), 404
            
        columns = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            column_type = 'categorical' if dtype == 'object' or df[col].nunique() < 10 else 'numerical'
            unique_values = df[col].unique().tolist() if column_type == 'categorical' else None
            columns.append({
                'name': col,
                'type': column_type,
                'unique_values': unique_values,
                'min': float(df[col].min()) if column_type == 'numerical' else None,
                'max': float(df[col].max()) if column_type == 'numerical' else None
            })
        
        return jsonify(columns)
        
    except Exception as e:
        print(f"Error in get_columns: {str(e)}")
        return jsonify({'error': str(e)}), 500

@data_routes.route('/data/<source_id>/filtered', methods=['POST'])
def get_filtered_data(source_id: str):
    """Get filtered data based on provided criteria"""
    try:
        filters = request.json.get('filters', [])
        layer_config = request.json.get('layer_config', {})
        layer_type = layer_config.get('type', '')
        print(f"Processing filtered data request for source: {source_id}, layer type: {layer_type}")
        
        if source_id == 'local_dataset':
            # Map layer types to data types
            data_type_map = {
                'scatterplot': 'points',
                'heatmap': 'heatmap',
                'polygon': 'h3_grid'
            }
            
            data_type = data_type_map.get(layer_type, 'points')
            print(f"Selected data type: {data_type} for layer type: {layer_type}")
            
            # Load preprocessed data
            result = data_processor.get_processed_data(source_id, data_type)
            print(f"Loaded {data_type} data with {len(result['features'])} features")
            if len(result['features']) > 0:
                print(f"Sample feature: {result['features'][0]}")
            
            # Apply filters if needed
            if filters:
                filtered_features = []
                for feature in result['features']:
                    include_feature = True
                    for filter_def in filters:
                        column = filter_def.get('column')
                        operator = filter_def.get('operator')
                        value = filter_def.get('value')
                        
                        if not all([column, operator, value]):
                            continue
                        
                        # Handle both GeoJSON properties and H3 direct properties
                        feature_value = (
                            feature.get('properties', {}).get(column) if 'properties' in feature 
                            else feature.get(column)
                        )
                        
                        if operator == 'equals' and feature_value != value:
                            include_feature = False
                        elif operator == 'contains' and not str(feature_value).find(value) >= 0:
                            include_feature = False
                        elif operator == 'greater_than' and not feature_value > value:
                            include_feature = False
                        elif operator == 'less_than' and not feature_value < value:
                            include_feature = False
                        elif operator == 'in' and feature_value not in value:
                            include_feature = False
                    
                    if include_feature:
                        filtered_features.append(feature)
                
                result['features'] = filtered_features
            
            print(f"Returning {result['type']} with {len(result['features'])} features")
            return jsonify(result)
            
        elif source_id == 'traffic_api':
            data = generate_traffic_data()
            return jsonify(data['data'])
        elif source_id == 'historical_data':
            data = generate_historical_data()['data']
            df = pd.DataFrame(data)
            return jsonify(df.to_dict(orient='records'))
        else:
            return jsonify({'error': 'Data source not found'}), 404
            
    except Exception as e:
        print(f"Error in get_filtered_data: {str(e)}")
        return jsonify({'error': str(e)}), 500 