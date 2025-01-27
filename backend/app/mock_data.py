import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_traffic_data():
    """Generate mock traffic data"""
    num_points = 100
    now = datetime.now()
    timestamps = [(now - timedelta(minutes=i)).isoformat() for i in range(num_points)]
    
    # Create congestion levels array with exact length
    congestion_options = ['High', 'Medium', 'Low']
    congestion_levels = [congestion_options[i % len(congestion_options)] for i in range(num_points)]
    
    # Generate routes around San Francisco
    routes = []
    for _ in range(20):
        # Create a route with start and end points
        start_lat = 37.7749 + np.random.normal(0, 0.02)
        start_lng = -122.4194 + np.random.normal(0, 0.02)
        end_lat = 37.7749 + np.random.normal(0, 0.02)
        end_lng = -122.4194 + np.random.normal(0, 0.02)
        congestion = np.random.randint(1, 10)
        
        routes.append({
            'start_point': [start_lng, start_lat],  # [longitude, latitude]
            'end_point': [end_lng, end_lat],
            'congestion_level': congestion
        })
    
    return {
        'data': routes,
        'metadata': {
            'timestamps': timestamps,
            'volume': [int(50 + 30 * np.sin(i/10) + np.random.normal(0, 5)) for i in range(num_points)],
            'congestion_levels': congestion_levels
        }
    }

def generate_historical_data():
    """Generate mock historical traffic data"""
    num_points = 1000
    start_date = datetime.now() - timedelta(days=30)
    dates = [(start_date + timedelta(hours=i)).isoformat() for i in range(num_points)]
    
    return {
        'data': {
            'timestamps': dates,
            'volume': [int(100 + 50 * np.sin(i/100) + np.random.normal(0, 10)) for i in range(num_points)],
            'congestion_distribution': {
                'High': np.random.randint(100, 200),
                'Medium': np.random.randint(300, 500),
                'Low': np.random.randint(400, 600)
            }
        }
    } 