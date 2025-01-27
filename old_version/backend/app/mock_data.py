import numpy as np
import pandas as pd
from datetime import datetime, timedelta

def generate_traffic_data():
    """Generate mock traffic data"""
    num_points = 100
    now = datetime.now()
    timestamps = [(now - timedelta(minutes=i)).isoformat() for i in range(num_points)]
    
    return {
        'data': {
            'timestamps': timestamps,
            'volume': [int(50 + 30 * np.sin(i/10) + np.random.normal(0, 5)) for i in range(num_points)],
            'congestion_levels': ['High', 'Medium', 'Low'] * (num_points // 3 + 1),
            'routes': [
                {
                    'start_point': [-122.4194 + np.random.normal(0, 0.02), 37.7749 + np.random.normal(0, 0.02)],
                    'end_point': [-122.4194 + np.random.normal(0, 0.02), 37.7749 + np.random.normal(0, 0.02)],
                    'congestion_level': np.random.randint(1, 10)
                }
                for _ in range(20)
            ]
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