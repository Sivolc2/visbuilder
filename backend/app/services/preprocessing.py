from typing import List, Dict, Any
from ..api.models import Feature, Dataset

class PreprocessingService:
    @staticmethod
    def normalize_values(features: List[Feature], field: str = 'value') -> List[Feature]:
        """Normalize values in the dataset to range [0,1]"""
        values = [f.properties.get(field, 0) for f in features]
        min_val = min(values)
        max_val = max(values)
        range_val = max_val - min_val

        for feature in features:
            if field in feature.properties:
                normalized = (feature.properties[field] - min_val) / range_val
                feature.properties[f'normalized_{field}'] = normalized

        return features

    @staticmethod
    def add_derived_fields(features: List[Feature], calculations: Dict[str, Any]) -> List[Feature]:
        """Add calculated fields based on existing properties"""
        for feature in features:
            for new_field, formula in calculations.items():
                try:
                    # Example formula: lambda x: x['value'] * 2
                    feature.properties[new_field] = formula(feature.properties)
                except Exception as e:
                    print(f"Error calculating {new_field}: {e}")

        return features

    @staticmethod
    def process_dataset(dataset: Dataset) -> Dataset:
        """Apply all preprocessing steps to a dataset"""
        # Normalize the 'value' field
        dataset.features = PreprocessingService.normalize_values(dataset.features)

        # Add some derived fields
        calculations = {
            'value_squared': lambda props: props.get('value', 0) ** 2,
            'high_value': lambda props: props.get('value', 0) > 75
        }
        dataset.features = PreprocessingService.add_derived_fields(
            dataset.features, calculations
        )

        # Update metadata
        dataset.metadata.update({
            'preprocessing': {
                'normalized_fields': ['value'],
                'derived_fields': list(calculations.keys())
            }
        })

        return dataset 