import os
import time
from typing import Dict, Any, Optional
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .config_loader import ConfigLoader

class ViewConfigHandler(FileSystemEventHandler):
    def __init__(self, view_manager):
        self.view_manager = view_manager
        
    def on_created(self, event):
        if event.src_path.endswith('.yaml'):
            print(f"New config file detected: {event.src_path}")
            self.view_manager.load_view_config(event.src_path)
            
    def on_modified(self, event):
        if event.src_path.endswith('.yaml'):
            print(f"Config file modified: {event.src_path}")
            self.view_manager.load_view_config(event.src_path)
            
class ViewManager:
    def __init__(self, config_dir: str):
        self.config_dir = Path(config_dir)
        self.views_dir = self.config_dir / 'views'
        self.views_dir.mkdir(exist_ok=True)
        print(f"Watching directory: {self.views_dir}")
        self.config_loader = ConfigLoader(str(self.config_dir))
        self.views: Dict[str, Dict[str, Any]] = {}
        self.observer: Optional[Observer] = None
        
    def start_watching(self):
        """Start watching for config file changes"""
        print("Starting file watcher...")
        self.observer = Observer()
        handler = ViewConfigHandler(self)
        self.observer.schedule(handler, str(self.views_dir), recursive=False)
        self.observer.start()
        print("File watcher started")
        
        # Load existing views
        self.load_all_views()
        
    def stop_watching(self):
        """Stop watching for config file changes"""
        if self.observer:
            print("Stopping file watcher...")
            self.observer.stop()
            self.observer.join()
            
    def load_view_config(self, config_path: str):
        """Load or reload a view configuration"""
        try:
            print(f"Loading view config from: {config_path}")
            view_id = Path(config_path).stem
            config = self.config_loader.load_view_config(config_path)
            
            if config:
                print(f"Successfully loaded config for view: {view_id}")
                self.views[view_id] = {
                    'id': view_id,
                    'config': config,
                    'last_updated': time.time()
                }
                print(f"Current views: {list(self.views.keys())}")
            else:
                print(f"Failed to load config for view: {view_id}")
                
        except Exception as e:
            print(f"Error loading view configuration {config_path}: {str(e)}")
            
    def load_all_views(self):
        """Load all view configurations from the views directory"""
        print(f"Loading all views from: {self.views_dir}")
        if not self.views_dir.exists():
            print(f"Views directory does not exist: {self.views_dir}")
            return
            
        yaml_files = list(self.views_dir.glob('*.yaml'))
        print(f"Found {len(yaml_files)} YAML files")
        
        for config_file in yaml_files:
            print(f"Found config file: {config_file}")
            self.load_view_config(str(config_file))
            
        print(f"Finished loading views. Current views: {list(self.views.keys())}")
            
    def get_view(self, view_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific view configuration"""
        view = self.views.get(view_id)
        if view:
            print(f"Returning view configuration for: {view_id}")
        else:
            print(f"View not found: {view_id}")
        return view
        
    def get_all_views(self) -> Dict[str, Dict[str, Any]]:
        """Get all view configurations"""
        print(f"Returning all views: {list(self.views.keys())}")
        return self.views 