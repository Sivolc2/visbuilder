from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field
from datetime import datetime

class Coordinate(BaseModel):
    longitude: float
    latitude: float

class H3Cell(BaseModel):
    h3_index: str
    resolution: int
    center: Coordinate
    value: float
    properties: Dict[str, Any] = Field(default_factory=dict)

class Feature(BaseModel):
    id: str
    coordinates: Coordinate
    properties: Dict[str, Any]
    timestamp: Optional[datetime] = None
    h3_cells: Optional[Dict[int, str]] = None  # Resolution -> H3 Index

class GridDataset(BaseModel):
    id: str
    name: str
    description: str
    resolution: int
    cells: List[H3Cell]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    source_dataset_id: Optional[str] = None

class Dataset(BaseModel):
    id: str
    name: str
    description: str
    features: List[Feature]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)
    template_id: Optional[str] = None
    grid_versions: Dict[int, str] = Field(default_factory=dict)  # Resolution -> GridDataset ID

class DatasetTemplate(BaseModel):
    id: str
    name: str
    description: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.now)

class StorageConfig(BaseModel):
    """Configuration for external storage"""
    storage_type: str  # e.g., 's3', 'local', 'database'
    parameters: Dict[str, Any]  # Storage-specific parameters 