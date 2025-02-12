import h3
import numpy as np
from typing import List, Dict, Any
import pandas as pd

def create_heatmap_geojson(df: pd.DataFrame, intensity_field: str = 'Flight_Usage_Mbps', resolution: int = 8) -> Dict[str, Any]:
    """
    Create a heatmap GeoJSON by aggregating points into a regular grid.
    """
    features = []
    
    # Create a grid of points and aggregate values
    lat_min, lat_max = df['Latitude'].min(), df['Latitude'].max()
    lon_min, lon_max = df['Longitude'].min(), df['Longitude'].max()
    
    # Create grid cells
    lat_steps = np.linspace(lat_min, lat_max, num=50)
    lon_steps = np.linspace(lon_min, lon_max, num=50)
    
    for lat in lat_steps:
        for lon in lon_steps:
            # Find points within the cell
            mask = (
                (df['Latitude'] >= lat - 0.01) & 
                (df['Latitude'] < lat + 0.01) &
                (df['Longitude'] >= lon - 0.01) & 
                (df['Longitude'] < lon + 0.01)
            )
            if mask.any():
                intensity = df.loc[mask, intensity_field].sum()
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(lon), float(lat)]
                    },
                    "properties": {
                        "intensity": float(intensity)
                    }
                }
                features.append(feature)
    
    return {
        "type": "FeatureCollection",
        "features": features
    }

def create_h3_grid_geojson(df: pd.DataFrame, value_field: str = 'Flight_Usage_Mbps', resolution: int = 8) -> Dict[str, Any]:
    """
    Create H3 hexagon data by aggregating point data into hexagons.
    Returns a list of objects with hex indices and values, ready for H3HexagonLayer.
    """
    print(f"Creating H3 grid with resolution {resolution}")
    print(f"Input DataFrame columns: {df.columns.tolist()}")
    print(f"First row: {df.iloc[0].to_dict()}")
    
    # Create a dictionary to store aggregated values for each hexagon
    hex_data = {}
    
    # Convert points to H3 indexes and aggregate values
    for _, row in df.iterrows():
        try:
            lat, lon = float(row['Latitude']), float(row['Longitude'])
            h3_index = h3.latlng_to_cell(lat, lon, resolution)
            value = float(row[value_field])
            
            if h3_index in hex_data:
                hex_data[h3_index]['value'] += value
                hex_data[h3_index]['point_count'] += 1
            else:
                hex_data[h3_index] = {
                    'hex': h3_index,
                    'value': value,
                    'point_count': 1
                }
        except Exception as e:
            print(f"Error processing row: {row}, Error: {str(e)}")
            continue
    
    print(f"Created {len(hex_data)} unique H3 hexagons")
    
    # Convert dictionary to list of objects
    features = list(hex_data.values())
    
    if features:
        print("First hexagon example:", features[0])
    
    result = {
        "type": "H3Collection",
        "features": features
    }
    print(f"Generated H3 data with {len(features)} hexagons")
    return result 