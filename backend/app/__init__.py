from flask import Flask
from flask_cors import CORS
import os
from .routes.views import views_routes
from .routes.data import data_routes
from .routes.status import status_routes

def create_app():
    app = Flask(__name__,
                template_folder=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    app.register_blueprint(views_routes)
    app.register_blueprint(data_routes)
    app.register_blueprint(status_routes)
    
    return app 