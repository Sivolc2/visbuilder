from flask import Flask
from flask_cors import CORS
from .routes.views import views_routes
from .routes.data import data_routes

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    app.register_blueprint(views_routes)
    app.register_blueprint(data_routes)
    
    return app 