from flask import Flask
from flask_cors import CORS
import os
from .routes.views import views_routes
from .routes.data import data_routes, initialize_data
from .routes.status import status_routes

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    CORS(app)  # Allow CORS for all routes
    
    # Register blueprints with /api prefix
    app.register_blueprint(views_routes, url_prefix='/api')
    app.register_blueprint(data_routes, url_prefix='/api')
    app.register_blueprint(status_routes, url_prefix='/api')
    
    # Initialize data processing
    with app.app_context():
        initialize_data()
    
    # Print all registered routes
    print("\nRegistered Routes:")
    print("==================")
    for rule in sorted(app.url_map.iter_rules(), key=lambda x: str(x)):
        methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
        print(f"{methods:20s} {rule.rule}")
    print("==================\n")
    
    return app 