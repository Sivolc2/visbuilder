docker stop visbuilder-frontend
docker container prune -f
cd frontend
docker build -t visbuilder-frontend .
docker run -d \
     --name visbuilder-frontend \
     -p 80:80 \
     -e VITE_BACKEND_URL=http://localhost:5003 \
     -e VITE_MAPBOX_ACCESS_TOKEN=your_mapbox_token_here \
     visbuilder-frontend
