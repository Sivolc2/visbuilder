from typing import TypedDict, List, Union, Optional
from enum import Enum

class VisualizationType(str, Enum):
    LINE_CHART = "line"
    BAR_CHART = "bar"
    PIE_CHART = "pie"
    SCATTER_PLOT = "scatter"
    HEATMAP = "heatmap"

class BaseVisualizationConfig(TypedDict):
    id: str
    name: str
    type: VisualizationType
    description: str
    data_source: str
    layout: dict
    config: dict

class TimeSeriesConfig(BaseVisualizationConfig):
    x_field: str
    y_field: str
    mode: str  # 'lines', 'markers', 'lines+markers'
    
class BarChartConfig(BaseVisualizationConfig):
    x_field: str
    y_field: str
    orientation: str  # 'v' or 'h'
    
class PieChartConfig(BaseVisualizationConfig):
    values_field: str
    labels_field: str
    
class ScatterPlotConfig(BaseVisualizationConfig):
    x_field: str
    y_field: str
    size_field: Optional[str]
    color_field: Optional[str]

# Factory for creating visualization configs
class VisualizationConfigFactory:
    @staticmethod
    def create_visualization_config(vis_type: VisualizationType, config_data: dict) -> BaseVisualizationConfig:
        vis_config_map = {
            VisualizationType.LINE_CHART: TimeSeriesConfig,
            VisualizationType.BAR_CHART: BarChartConfig,
            VisualizationType.PIE_CHART: PieChartConfig,
            VisualizationType.SCATTER_PLOT: ScatterPlotConfig
        }
        
        if vis_type not in vis_config_map:
            raise ValueError(f"Unsupported visualization type: {vis_type}")
            
        config_class = vis_config_map[vis_type]
        return config_class(**config_data) 