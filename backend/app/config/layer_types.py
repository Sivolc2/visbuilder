from typing import TypedDict, List, Union, Optional
from enum import Enum

class LayerType(str, Enum):
    LINE = "line"
    SCATTERPLOT = "scatterplot"
    HEATMAP = "heatmap"
    HEXAGON = "hexagon"
    GRID = "grid"

class BaseLayerConfig(TypedDict):
    id: str
    name: str
    type: LayerType
    description: str
    visible: bool
    opacity: float
    data_source: str
    color: Union[List[int], str]
    
class LineLayerConfig(BaseLayerConfig):
    width: float
    source_position: str
    target_position: str
    
class ScatterplotLayerConfig(BaseLayerConfig):
    radius: float
    position: str
    
class HeatmapLayerConfig(BaseLayerConfig):
    weight: str
    intensity: float
    threshold: float
    
class GridLayerConfig(BaseLayerConfig):
    cell_size: int
    elevation_scale: float
    elevation_range: List[float]

# Factory for creating layer configs
class LayerConfigFactory:
    @staticmethod
    def create_layer_config(layer_type: LayerType, config_data: dict) -> BaseLayerConfig:
        layer_config_map = {
            LayerType.LINE: LineLayerConfig,
            LayerType.SCATTERPLOT: ScatterplotLayerConfig,
            LayerType.HEATMAP: HeatmapLayerConfig,
            LayerType.GRID: GridLayerConfig
        }
        
        if layer_type not in layer_config_map:
            raise ValueError(f"Unsupported layer type: {layer_type}")
            
        config_class = layer_config_map[layer_type]
        return config_class(**config_data) 