from flask import Blueprint, jsonify, request
import boto3
from botocore.exceptions import ClientError
import os
import importlib
from ..config.config_loader import ConfigLoader
from ..config.data_sources import DataSourceType
import pandas as pd
import json
import requests
from typing import Any, Dict
from ..mock_data import generate_traffic_data, generate_historical_data

data_routes = Blueprint('data', __name__)
config_loader = ConfigLoader(os.getenv('CONFIG_DIR', 'app/config'))

@data_routes.route('/api/data/<source_id>', methods=['GET'])
def get_data(source_id: str):
    """Get data from a specific data source"""
    try:
        # For development, return mock data
        if source_id == 'traffic_api':
            return jsonify(generate_traffic_data())
        elif source_id == 'historical_data':
            return jsonify(generate_historical_data())
            
        return jsonify({'error': 'Data source not found'}), 404
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/api/config', methods=['GET'])
def get_config():
    """Get all configuration including layers, visualizations, and layout"""
    try:
        return jsonify(config_loader.load_all())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/api/layers', methods=['GET'])
def get_layers():
    """Get all layer configurations"""
    try:
        return jsonify(config_loader.load_layers())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@data_routes.route('/api/visualizations', methods=['GET'])
def get_visualizations():
    """Get all visualization configurations"""
    try:
        return jsonify(config_loader.load_visualizations())
    except Exception as e:
        return jsonify({'error': str(e)}), 500 

@data_routes.route('/api/data/<source_id>/columns', methods=['GET'])
def get_columns(source_id: str):
    """Get column metadata for a specific data source"""
    try:
        # For development, return mock data columns
        if source_id == 'traffic_api':
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

@data_routes.route('/api/data/<source_id>/filtered', methods=['POST'])
def get_filtered_data(source_id: str):
    """Get filtered data based on provided criteria"""
    try:
        filters = request.json.get('filters', [])
        
        # Get base dataset
        if source_id == 'traffic_api':
            data = generate_traffic_data()
            # Return routes data directly for map layers
            return jsonify(data['data'])
        elif source_id == 'historical_data':
            data = generate_historical_data()['data']
            df = pd.DataFrame(data)
        else:
            return jsonify({'error': 'Data source not found'}), 404
            
        # Apply filters (only for historical data)
        if source_id == 'historical_data':
            for filter_def in filters:
                column = filter_def.get('column')
                operator = filter_def.get('operator')
                value = filter_def.get('value')
                
                if not all([column, operator, value]):
                    continue
                    
                if operator == 'equals':
                    df = df[df[column] == value]
                elif operator == 'contains':
                    df = df[df[column].str.contains(value, na=False)]
                elif operator == 'greater_than':
                    df = df[df[column] > value]
                elif operator == 'less_than':
                    df = df[df[column] < value]
                elif operator == 'in':
                    df = df[df[column].isin(value)]
                    
            return jsonify(df.to_dict(orient='records'))
        
    except Exception as e:
        print(f"Error in get_filtered_data: {str(e)}")
        return jsonify({'error': str(e)}), 500 