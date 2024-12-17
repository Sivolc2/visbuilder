from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
import os

from .api.models import Dataset, DatasetTemplate, GridDataset, StorageConfig
from .services.data_service import DataService
from .services.preprocessing import PreprocessingService
from .services.templating import TemplatingService
from .services.grid_service import GridService
from .services.storage import StorageService
from .utils.json_utils import DateTimeEncoder

app = FastAPI(title="Visbuilder API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize storage service
storage_config = StorageConfig(
    storage_type=os.getenv('STORAGE_TYPE', 'local'),
    parameters={'base_path': os.getenv('STORAGE_PATH', './data')}
)
storage_service = StorageService(storage_config)

# In-memory storage for demonstration
datasets: Dict[str, Dataset] = {}
templates: Dict[str, DatasetTemplate] = {}
grid_datasets: Dict[str, GridDataset] = {}

# Custom JSON response class
class CustomJSONResponse(JSONResponse):
    def render(self, content) -> bytes:
        return super().render(DateTimeEncoder().encode(content))

# Use custom response class for all endpoints
app.router.default_response_class = CustomJSONResponse

@app.get("/")
async def root():
    return {"message": "Welcome to Visbuilder API"}

@app.post("/datasets/", response_model=Dataset)
async def create_dataset(name: str, description: str):
    """Create a new dataset with sample data"""
    # Pull and create initial dataset
    dataset = DataService.create_dataset(name, description)
    
    # Apply preprocessing
    dataset = PreprocessingService.process_dataset(dataset)
    
    # Store dataset
    datasets[dataset.id] = dataset
    storage_service.save_dataset(dataset)
    
    return dataset

@app.get("/datasets/", response_model=List[Dataset])
async def list_datasets():
    """List all available datasets"""
    return list(datasets.values())

@app.get("/datasets/{dataset_id}", response_model=Dataset)
async def get_dataset(dataset_id: str):
    """Get a specific dataset"""
    # Try to get from memory first
    dataset = datasets.get(dataset_id)
    if not dataset:
        # Try to load from storage
        data = storage_service.load_dataset(dataset_id)
        if data:
            dataset = Dataset(**data)
            datasets[dataset_id] = dataset
        else:
            raise HTTPException(status_code=404, detail="Dataset not found")
    return dataset

@app.post("/datasets/{dataset_id}/grid", response_model=GridDataset)
async def create_grid_version(
    dataset_id: str,
    resolution: int,
    value_field: str = 'value'
):
    """Create an H3 grid version of a dataset"""
    dataset = await get_dataset(dataset_id)
    
    # Create grid dataset
    grid_dataset = GridService.create_grid_dataset(
        dataset, resolution, value_field
    )
    
    # Store grid dataset
    grid_datasets[grid_dataset.id] = grid_dataset
    storage_service.save_grid_dataset(grid_dataset)
    
    # Update and save original dataset with grid reference
    storage_service.save_dataset(dataset)
    
    return grid_dataset

@app.get("/datasets/{dataset_id}/grid/{resolution}", response_model=Optional[GridDataset])
async def get_grid_version(dataset_id: str, resolution: int):
    """Get a specific grid version of a dataset"""
    dataset = await get_dataset(dataset_id)
    
    if resolution not in dataset.grid_versions:
        return None
    
    grid_id = dataset.grid_versions[resolution]
    
    # Try to get from memory first
    grid_dataset = grid_datasets.get(grid_id)
    if not grid_dataset:
        # Try to load from storage
        data = storage_service.load_grid_dataset(grid_id)
        if data:
            grid_dataset = GridDataset(**data)
            grid_datasets[grid_id] = grid_dataset
    
    return grid_dataset

@app.post("/templates/", response_model=DatasetTemplate)
async def create_template(dataset_id: str, parameters: Dict[str, any]):
    """Create a template from a dataset"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    template = TemplatingService.create_template(
        datasets[dataset_id], parameters
    )
    templates[template.id] = template
    return template

@app.post("/datasets/{dataset_id}/variants", response_model=Dataset)
async def create_variant(dataset_id: str, variant_params: Dict[str, any]):
    """Create a variant of a dataset"""
    if dataset_id not in datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    variant = TemplatingService.create_variant(
        datasets[dataset_id], variant_params
    )
    datasets[variant.id] = variant
    storage_service.save_dataset(variant)
    return variant 