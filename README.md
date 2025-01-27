# Strategic Analytics Dashboard

Strategic dashboard for monitoring aircraft-antenna relationships and SLA metrics.

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── v1/
│   │   │       ├── endpoints/
│   │   │       │   ├── config.py
│   │   │       │   └── data.py
│   │   │       └── api.py
│   │   ├── core/
│   │   │   └── config.py
│   │   └── main.py
│   ├── Dockerfile
│   └── requirements.txt
```

## Quick Start

### Local Development

1. Set up environment:
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
cd backend
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
# Create .env file in project root
cp .env.example .env
# Edit .env with your AWS credentials and other settings
```

3. Run the application:
```bash
# Development mode
uvicorn app.main:app --reload --port 8000
```

### Docker Deployment

```bash
# Build the container
docker build -t dashboard-backend ./backend

# Run the container
docker run -p 8000:8000 -d dashboard-backend
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Key Endpoints

- `GET /api/v1/config`: Retrieve dashboard configuration
- `POST /api/v1/data`: Get filtered aircraft and antenna data

## Data Format

### YAML Configuration
```yaml
dashboard:
  title: "Q3 Coverage Analysis"
  refresh_rate: 3600

data_sources:
  - id: aircraft_positions
    type: s3_parquet
    path: s3://satcom-data/aircraft/
```

### Aircraft Data Schema
- `tail_id`: Aircraft identifier
- `timestamp`: UTC observation time
- `lat`: WGS84 latitude
- `lon`: WGS84 longitude
- `linked_antenna`: Current connected antenna ID
- `sla_metric`: Performance score (0-1)

### Antenna Data Schema
- `antenna_id`: Unique identifier
- `location`: Human-readable name
- `max_capacity`: Simultaneous aircraft supported
- `frequency_bands`: Supported bands [Ka, Ku]

## Contributing

1. Branch naming: `feature/description` or `fix/description`
2. Commit messages: Follow conventional commits
3. PR reviews required before merge

## License

MIT License - See LICENSE file for details
