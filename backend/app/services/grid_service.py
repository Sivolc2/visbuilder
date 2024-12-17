from typing import List, Dict, Any
import uuid
import h3
from collections import defaultdict

from ..api.models import Dataset, GridDataset, H3Cell, Coordinate, Feature

class GridService:
    @staticmethod
    def point_to_h3(lat: float, lon: float, resolution: int) -> str:
        """Convert a lat/lon point to H3 index"""
        return h3.geo_to_h3(lat, lon, resolution)

    @staticmethod
    def h3_to_center(h3_index: str) -> Coordinate:
        """Get the center point of an H3 cell"""
        lat, lon = h3.h3_to_geo(h3_index)
        return Coordinate(latitude=lat, longitude=lon)

    @staticmethod
    def features_to_grid(
        features: List[Feature],
        resolution: int,
        value_field: str = 'value'
    ) -> List[H3Cell]:
        """Convert point features to H3 grid cells with aggregated values"""
        cell_values = defaultdict(list)
        cell_properties = defaultdict(lambda: defaultdict(list))

        # Aggregate values by H3 cell
        for feature in features:
            h3_index = GridService.point_to_h3(
                feature.coordinates.latitude,
                feature.coordinates.longitude,
                resolution
            )
            
            # Store H3 index in feature for future reference
            if not feature.h3_cells:
                feature.h3_cells = {}
            feature.h3_cells[resolution] = h3_index
            
            # Aggregate values
            cell_values[h3_index].append(
                feature.properties.get(value_field, 0)
            )
            
            # Aggregate all properties
            for key, value in feature.properties.items():
                if key != value_field:
                    cell_properties[h3_index][key].append(value)

        # Create H3 cells with aggregated values
        cells = []
        for h3_index, values in cell_values.items():
            # Calculate average value for the cell
            avg_value = sum(values) / len(values)
            
            # Aggregate other properties
            properties = {}
            for key, prop_values in cell_properties[h3_index].items():
                if all(isinstance(v, (int, float)) for v in prop_values):
                    # Numeric properties: calculate average
                    properties[f"avg_{key}"] = sum(prop_values) / len(prop_values)
                else:
                    # Non-numeric properties: store as list
                    properties[f"all_{key}"] = prop_values

            cells.append(H3Cell(
                h3_index=h3_index,
                resolution=resolution,
                center=GridService.h3_to_center(h3_index),
                value=avg_value,
                properties=properties
            ))

        return cells

    @staticmethod
    def create_grid_dataset(
        dataset: Dataset,
        resolution: int,
        value_field: str = 'value'
    ) -> GridDataset:
        """Create a grid dataset from a point dataset"""
        cells = GridService.features_to_grid(
            dataset.features, resolution, value_field
        )

        grid_dataset = GridDataset(
            id=str(uuid.uuid4()),
            name=f"{dataset.name} (H3 Grid r{resolution})",
            description=f"H3 grid version of {dataset.name} at resolution {resolution}",
            resolution=resolution,
            cells=cells,
            source_dataset_id=dataset.id,
            metadata={
                'source_dataset': dataset.id,
                'resolution': resolution,
                'cell_count': len(cells),
                'value_field': value_field
            }
        )

        # Store reference to grid version in original dataset
        dataset.grid_versions[resolution] = grid_dataset.id

        return grid_dataset 