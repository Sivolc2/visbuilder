# VisBuilder

A modern data visualization builder application that allows users to create and customize interactive dashboards with multiple visualization layers. The application consists of a React-based frontend for the visualization interface and a Flask backend for data processing and API services.

## Project Structure

```
visbuilder/
├── frontend/          # React + TypeScript frontend application
├── backend/           # Flask Python backend
├── example.png        # Example visualization
└── README.md
```

## Tech Stack

### Frontend
- React 18 with TypeScript
- Vite for build tooling
- DeckGL for map visualizations
- Plotly.js for charts
- Ant Design for UI components
- MapboxGL for base maps
- Axios for API calls

### Backend
- Flask
- Flask-CORS
- Pandas for data processing
- Boto3 for AWS integration
- Python-dotenv for environment management

## Local Development Setup

### Frontend Setup
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Create a `.env` file with required environment variables
4. Start the development server:
   ```bash
   npm start
   ```

### Backend Setup
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up environment variables
5. Run the development server:
   ```bash
   python run.py
   ```

## Docker Setup

### Building Docker Images
1. Build the backend image:
   ```bash
   cd backend
   docker build -t visbuilder-backend .
   ```

2. Build the frontend image:
   ```bash
   cd frontend
   docker build -t visbuilder-frontend .
   ```

### Running Containers

1. Start the backend container:
   ```bash
   docker run -d \
     --name visbuilder-backend \
     -p 5003:5003 \
     -e FLASK_APP=run.py \
     -e FLASK_ENV=production \
     visbuilder-backend
   ```

2. Start the frontend container:
   ```bash
   docker run -d \
     --name visbuilder-frontend \
     -p 80:80 \
     -e VITE_BACKEND_URL=http://localhost:5003 \
     -e VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here \
     visbuilder-frontend
   ```

### Accessing the Application
- Frontend: http://localhost
- Backend API: http://localhost:5003

### Container Management
```bash
# View running containers
docker ps

# View container logs
docker logs visbuilder-frontend
docker logs visbuilder-backend

# Stop containers
docker stop visbuilder-frontend visbuilder-backend

# Remove containers
docker rm visbuilder-frontend visbuilder-backend

# Remove images
docker rmi visbuilder-frontend visbuilder-backend
```

### Development Mode
For development with hot-reload:

1. Backend (with volume mount):
   ```bash
   docker run -d \
     --name visbuilder-backend \
     -p 5003:5003 \
     -e FLASK_APP=run.py \
     -e FLASK_ENV=development \
     -v $(pwd)/backend:/app \
     visbuilder-backend
   ```

2. Frontend (with volume mount):
   ```bash
   docker run -d \
     --name visbuilder-frontend \
     -p 80:80 \
     -e VITE_BACKEND_URL=http://localhost:5003 \
     -e VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here \
     -v $(pwd)/frontend:/app \
     visbuilder-frontend
   ```

## AWS Deployment TODO List

### Infrastructure Setup
- [ ] Create a new AWS account or use existing one
- [ ] Set up IAM roles and policies
- [ ] Configure VPC with public and private subnets
- [ ] Set up security groups for frontend and backend

### Frontend Deployment
- [ ] Create S3 bucket for static website hosting
- [ ] Configure CloudFront distribution
- [ ] Set up Route53 DNS records (if using custom domain)
- [ ] Configure SSL certificate through ACM
- [ ] Set up CI/CD pipeline using AWS CodePipeline or GitHub Actions

### Backend Deployment
- [ ] Create ECS cluster
- [ ] Set up ECR repository for Docker images
- [ ] Create ECS task definition and service
- [ ] Configure Application Load Balancer
- [ ] Set up Auto Scaling policies
- [ ] Configure RDS if needed for data persistence
- [ ] Set up S3 bucket for file storage (if needed)

### Monitoring and Maintenance
- [ ] Set up CloudWatch monitoring and alerts
- [ ] Configure logging and log retention
- [ ] Set up backup policies
- [ ] Create health check endpoints
- [ ] Configure AWS X-Ray for tracing (optional)

### Security
- [ ] Review and configure CORS policies
- [ ] Set up WAF rules
- [ ] Configure network ACLs
- [ ] Set up AWS Shield (if needed)
- [ ] Implement proper secret management using AWS Secrets Manager

### Cost Management
- [ ] Set up AWS Budget alerts
- [ ] Configure resource tagging strategy
- [ ] Review and optimize instance sizes
- [ ] Set up Cost Explorer monitoring

## Contributing
Please read our contributing guidelines before submitting pull requests.

## License
[Add appropriate license information]
