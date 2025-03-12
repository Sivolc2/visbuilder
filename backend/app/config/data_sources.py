from typing import TypedDict, List, Union, Optional
from enum import Enum

class DataSourceType(str, Enum):
    S3 = "s3"
    API = "api"
    DATABASE = "database"
    FILE = "file"
    FUNCTION = "function"
    ATHENA = "athena"

class BaseDataSourceConfig(TypedDict):
    id: str
    name: str
    type: DataSourceType
    description: str
    refresh_interval: Optional[int]  # in seconds
    cache_enabled: bool

class S3DataSourceConfig(BaseDataSourceConfig):
    bucket: str
    key: str
    region: str
    format: str  # csv, json, parquet, etc.

class APIDataSourceConfig(BaseDataSourceConfig):
    url: str
    method: str
    headers: Optional[dict]
    params: Optional[dict]
    body: Optional[dict]

class DatabaseDataSourceConfig(BaseDataSourceConfig):
    connection_string: str
    query: str
    parameters: Optional[dict]

class FileDataSourceConfig(BaseDataSourceConfig):
    path: str
    format: str

class FunctionDataSourceConfig(BaseDataSourceConfig):
    module: str
    function: str
    parameters: Optional[dict]

class AthenaDataSourceConfig(BaseDataSourceConfig):
    query: str
    database: Optional[str]
    workgroup: Optional[str]
    region: Optional[str]
    environment: Optional[str]  # prod, preprod, dev
    output_location: Optional[str]  # S3 location for query results

# Factory for creating data source configs
class DataSourceConfigFactory:
    @staticmethod
    def create_data_source_config(source_type: DataSourceType, config_data: dict) -> BaseDataSourceConfig:
        source_config_map = {
            DataSourceType.S3: S3DataSourceConfig,
            DataSourceType.API: APIDataSourceConfig,
            DataSourceType.DATABASE: DatabaseDataSourceConfig,
            DataSourceType.FILE: FileDataSourceConfig,
            DataSourceType.FUNCTION: FunctionDataSourceConfig,
            DataSourceType.ATHENA: AthenaDataSourceConfig
        }
        
        if source_type not in source_config_map:
            raise ValueError(f"Unsupported data source type: {source_type}")
            
        config_class = source_config_map[source_type]
        return config_class(**config_data) 