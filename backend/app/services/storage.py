from typing import Optional, Dict, Any
import json
import os
from abc import ABC, abstractmethod
from pathlib import Path
import redis
from ..api.models import Dataset, GridDataset, StorageConfig
from ..utils.json_utils import serialize_to_json, parse_json

class StorageBackend(ABC):
    @abstractmethod
    def save_dataset(self, dataset_id: str, data: Dict[str, Any]) -> bool:
        pass

    @abstractmethod
    def load_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        pass

class LocalStorageBackend(StorageBackend):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def save_dataset(self, dataset_id: str, data: Dict[str, Any]) -> bool:
        try:
            file_path = self.base_path / f"{dataset_id}.json"
            with open(file_path, 'w') as f:
                f.write(serialize_to_json(data))
            return True
        except Exception as e:
            print(f"Error saving to local storage: {e}")
            return False

    def load_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        try:
            file_path = self.base_path / f"{dataset_id}.json"
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return parse_json(f.read())
        except Exception as e:
            print(f"Error loading from local storage: {e}")
        return None

class RedisCache:
    def __init__(self, host='redis', port=6379, db=0):
        self.redis = redis.Redis(host=host, port=port, db=db)
        self.default_ttl = 3600  # 1 hour default TTL

    def set_dataset(self, dataset_id: str, data: Dict[str, Any], ttl: int = None) -> bool:
        try:
            self.redis.set(
                f"dataset:{dataset_id}",
                serialize_to_json(data),
                ex=ttl or self.default_ttl
            )
            return True
        except Exception as e:
            print(f"Error caching dataset: {e}")
            return False

    def get_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        try:
            data = self.redis.get(f"dataset:{dataset_id}")
            if data:
                return parse_json(data)
        except Exception as e:
            print(f"Error retrieving cached dataset: {e}")
        return None

class StorageService:
    def __init__(self, config: StorageConfig):
        self.config = config
        self.cache = RedisCache()
        
        # Initialize storage backend based on config
        if config.storage_type == 'local':
            self.backend = LocalStorageBackend(config.parameters.get('base_path', './data'))
        else:
            # Add more storage backends as needed (S3, Database, etc.)
            raise ValueError(f"Unsupported storage type: {config.storage_type}")

    def save_dataset(self, dataset: Dataset) -> bool:
        """Save dataset to both cache and persistent storage"""
        dataset_dict = dataset.dict()
        
        # Save to cache
        self.cache.set_dataset(dataset.id, dataset_dict)
        
        # Save to persistent storage
        return self.backend.save_dataset(dataset.id, dataset_dict)

    def save_grid_dataset(self, grid_dataset: GridDataset) -> bool:
        """Save grid dataset to both cache and persistent storage"""
        grid_dict = grid_dataset.dict()
        
        # Save to cache with different prefix
        self.cache.set_dataset(f"grid:{grid_dataset.id}", grid_dict)
        
        # Save to persistent storage
        return self.backend.save_dataset(f"grid:{grid_dataset.id}", grid_dict)

    def load_dataset(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        """Try to load dataset from cache first, then persistent storage"""
        # Try cache first
        data = self.cache.get_dataset(dataset_id)
        if data:
            return data
        
        # Try persistent storage
        data = self.backend.load_dataset(dataset_id)
        if data:
            # Update cache
            self.cache.set_dataset(dataset_id, data)
            return data
        
        return None

    def load_grid_dataset(self, grid_id: str) -> Optional[Dict[str, Any]]:
        """Try to load grid dataset from cache first, then persistent storage"""
        # Try cache first
        data = self.cache.get_dataset(f"grid:{grid_id}")
        if data:
            return data
        
        # Try persistent storage
        data = self.backend.load_dataset(f"grid:{grid_id}")
        if data:
            # Update cache
            self.cache.set_dataset(f"grid:{grid_id}", data)
            return data
        
        return None 