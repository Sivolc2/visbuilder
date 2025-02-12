docker stop visbuilder-backend
docker container prune -f
cd backend
docker build -t visbuilder-backend .
docker run -d \
    --name visbuilder-backend \
    -p 5003:5003 \
    -e FLASK_APP=run.py \
    -e FLASK_ENV=production \
    visbuilder-backend