from typing import List
import uuid
from datetime import datetime, timedelta
import random

from ..api.models import Feature, Coordinate, Dataset

class DataService:
    @staticmethod
    def pull_data() -> List[Feature]:
        """Generate sample data points around San Francisco"""
        base_lat, base_lon = 37.7749, -122.4194  # San Francisco coordinates
        features = []
        
        # Generate 100 random points
        for _ in range(100):
            # Random offset from base coordinates (roughly within San Francisco)
            lat_offset = random.uniform(-0.1, 0.1)
            lon_offset = random.uniform(-0.1, 0.1)
            
            # Generate random properties
            value = random.uniform(0, 100)
            category = random.choice(['A', 'B', 'C'])
            timestamp = datetime.now() - timedelta(days=random.randint(0, 30))
            
            feature = Feature(
                id=str(uuid.uuid4()),
                coordinates=Coordinate(
                    latitude=base_lat + lat_offset,
                    longitude=base_lon + lon_offset
                ),
                properties={
                    'value': value,
                    'category': category,
                    'intensity': value / 100,
                },
                timestamp=timestamp
            )
            features.append(feature)
        
        return features

    @staticmethod
    def create_dataset(name: str, description: str) -> Dataset:
        """Create a new dataset with sample data"""
        features = DataService.pull_data()
        
        return Dataset(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            features=features,
            metadata={
                'source': 'sample_data',
                'point_count': len(features),
                'categories': ['A', 'B', 'C']
            }
        ) 