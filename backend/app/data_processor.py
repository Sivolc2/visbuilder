import pandas as pd
import h3
import json
from pathlib import Path
from typing import Dict, Any
from .utils.aggregations import create_heatmap_geojson, create_h3_grid_geojson

class DataProcessor:
    def __init__(self, datasets_dir: str = 'datasets', processed_dir: str = 'processed_data'):
        self.base_dir = Path(datasets_dir)
        self.processed_dir = Path(processed_dir)
        self.processed_dir.mkdir(exist_ok=True)
        
    def preprocess_dataset(self, file_path: str, dataset_id: str) -> None:
        """Preprocess a dataset and save different versions (raw points, heatmap, h3) to disk"""
        print(f"Preprocessing dataset: {dataset_id} from {file_path}")
        
        # Check if processed files already exist
        if self._check_processed_files_exist(dataset_id):
            print(f"Processed files already exist for {dataset_id}, skipping preprocessing")
            return
            
        try:
            # Read the dataset
            df = pd.read_csv(self.base_dir / file_path)
            print(f"Loaded dataset with {len(df)} rows")
            
            # Create processed data directory if it doesn't exist
            dataset_dir = self.processed_dir / dataset_id
            dataset_dir.mkdir(exist_ok=True)
            
            # 1. Create and save raw points GeoJSON
            points_geojson = self._create_points_geojson(df)
            self._save_geojson(points_geojson, dataset_dir / 'points.geojson')
            
            # 2. Create and save heatmap GeoJSON
            heatmap_geojson = create_heatmap_geojson(df)
            self._save_geojson(heatmap_geojson, dataset_dir / 'heatmap.geojson')
            
            # 3. Create and save H3 grid GeoJSON
            h3_geojson = create_h3_grid_geojson(df, resolution=4)  # Set resolution to 4 for larger hexagons
            self._save_geojson(h3_geojson, dataset_dir / 'h3_grid.geojson')
            
            print(f"Successfully preprocessed dataset {dataset_id}")
            
        except Exception as e:
            print(f"Error preprocessing dataset {dataset_id}: {str(e)}")
            raise
    
    def _check_processed_files_exist(self, dataset_id: str) -> bool:
        """Check if all processed files exist for a dataset"""
        dataset_dir = self.processed_dir / dataset_id
        required_files = ['points.geojson', 'heatmap.geojson', 'h3_grid.geojson']
        return all((dataset_dir / file).exists() for file in required_files)
    
    def _create_points_geojson(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert DataFrame to points GeoJSON"""
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
    
    def _save_geojson(self, data: Dict[str, Any], file_path: Path) -> None:
        """Save GeoJSON data to file"""
        with open(file_path, 'w') as f:
            json.dump(data, f)
    
    def get_processed_data(self, dataset_id: str, data_type: str = 'points') -> Dict[str, Any]:
        """Load preprocessed data from disk"""
        try:
            file_path = self.processed_dir / dataset_id / f'{data_type}.geojson'
            if not file_path.exists():
                raise FileNotFoundError(f"Processed data not found: {file_path}")
                
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading processed data: {str(e)}")
            raise 