from app import create_app
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5003))
    debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    ) 