from typing import Dict, Any
import uuid
from copy import deepcopy

from ..api.models import Dataset, DatasetTemplate

class TemplatingService:
    @staticmethod
    def create_template(dataset: Dataset, parameters: Dict[str, Any]) -> DatasetTemplate:
        """Create a template from a dataset with parameterizable fields"""
        return DatasetTemplate(
            id=str(uuid.uuid4()),
            name=f"Template for {dataset.name}",
            description=f"Template created from {dataset.name}",
            parameters=parameters,
            metadata={
                'source_dataset': dataset.id,
                'parameter_count': len(parameters)
            }
        )

    @staticmethod
    def apply_template(template: DatasetTemplate, parameter_values: Dict[str, Any]) -> Dataset:
        """Create a new dataset variant from a template"""
        # Validate parameters
        for required_param in template.parameters:
            if required_param not in parameter_values:
                raise ValueError(f"Missing required parameter: {required_param}")

        # Create a new dataset with modified parameters
        dataset = Dataset(
            id=str(uuid.uuid4()),
            name=f"Dataset from template {template.id}",
            description="Generated from template",
            features=[],  # Will be populated based on parameters
            template_id=template.id
        )

        # Example of parameter application:
        # - filter_threshold: filter features based on value
        # - scaling_factor: scale numeric values
        # - category_mapping: map categories to new values
        
        if 'filter_threshold' in parameter_values:
            threshold = parameter_values['filter_threshold']
            dataset.features = [
                f for f in dataset.features 
                if f.properties.get('value', 0) > threshold
            ]

        if 'scaling_factor' in parameter_values:
            scale = parameter_values['scaling_factor']
            for feature in dataset.features:
                feature.properties['value'] *= scale

        if 'category_mapping' in parameter_values:
            mapping = parameter_values['category_mapping']
            for feature in dataset.features:
                if 'category' in feature.properties:
                    old_category = feature.properties['category']
                    feature.properties['category'] = mapping.get(
                        old_category, old_category
                    )

        # Update metadata
        dataset.metadata.update({
            'template_parameters': parameter_values,
            'source_template': template.id
        })

        return dataset

    @staticmethod
    def create_variant(
        dataset: Dataset,
        variant_params: Dict[str, Any],
        name: str = None
    ) -> Dataset:
        """Create a variant of a dataset with modified parameters"""
        new_dataset = deepcopy(dataset)
        new_dataset.id = str(uuid.uuid4())
        new_dataset.name = name or f"Variant of {dataset.name}"
        
        # Apply variant parameters
        if 'value_multiplier' in variant_params:
            mult = variant_params['value_multiplier']
            for feature in new_dataset.features:
                feature.properties['value'] *= mult

        if 'category_filter' in variant_params:
            categories = variant_params['category_filter']
            new_dataset.features = [
                f for f in new_dataset.features 
                if f.properties.get('category') in categories
            ]

        # Update metadata
        new_dataset.metadata.update({
            'variant_params': variant_params,
            'source_dataset': dataset.id
        })

        return new_dataset 