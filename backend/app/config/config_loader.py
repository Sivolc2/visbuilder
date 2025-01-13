import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConfigLoader:
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        
    def load_view_config(self, config_path: str) -> Optional[Dict[str, Any]]:
        """Load a view configuration from a specific file"""
        try:
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
                if self.validate_config(config):
                    return config
                else:
                    print(f"Invalid config format in {config_path}")
                    return None
        except Exception as e:
            print(f"Error loading view config from {config_path}: {str(e)}")
            return None
            
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate the configuration format"""
        required_fields = {'name', 'type', 'description', 'data_sources', 'components'}
        if not all(field in config for field in required_fields):
            print(f"Missing required fields. Required: {required_fields}")
            return False
            
        # Validate data sources
        if not isinstance(config['data_sources'], list):
            print("data_sources must be a list")
            return False
            
        for ds in config['data_sources']:
            if not isinstance(ds, dict) or 'id' not in ds or 'type' not in ds:
                print(f"Invalid data source format: {ds}")
                return False
                
        # Validate components
        if not isinstance(config['components'], list):
            print("components must be a list")
            return False
            
        for comp in config['components']:
            if not isinstance(comp, dict) or 'type' not in comp:
                print(f"Invalid component format: {comp}")
                return False
                
            if comp['type'] == 'map':
                if 'layers' not in comp or not isinstance(comp['layers'], list):
                    print(f"Map component missing layers list: {comp}")
                    return False
                    
            elif comp['type'] == 'grid':
                if 'visualizations' not in comp or not isinstance(comp['visualizations'], list):
                    print(f"Grid component missing visualizations list: {comp}")
                    return False
                    
        return True 