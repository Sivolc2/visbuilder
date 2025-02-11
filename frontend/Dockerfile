# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source files
COPY . .

# Build the application with environment variables
ARG VITE_MAPBOX_ACCESS_TOKEN
ARG VITE_BACKEND_URL
ENV VITE_MAPBOX_ACCESS_TOKEN=$VITE_MAPBOX_ACCESS_TOKEN
ENV VITE_BACKEND_URL=$VITE_BACKEND_URL

RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files from build stage
COPY --from=build /app/dist /usr/share/nginx/html

# Add nginx configuration for SPA and API proxy
RUN echo $'server {\n\
    listen 80;\n\
    \n\
    location / {\n\
        root /usr/share/nginx/html;\n\
        index index.html;\n\
        try_files $uri $uri/ /index.html;\n\
    }\n\
    \n\
    location /api/ {\n\
        proxy_pass ${BACKEND_URL};\n\
        proxy_http_version 1.1;\n\
        proxy_set_header Upgrade $http_upgrade;\n\
        proxy_set_header Connection "upgrade";\n\
        proxy_set_header Host $host;\n\
        proxy_cache_bypass $http_upgrade;\n\
    }\n\
}' > /etc/nginx/conf.d/default.conf

# Add script to replace environment variables at runtime
RUN echo $'\
#!/bin/sh\n\
envsubst < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp\n\
mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf\n\
nginx -g "daemon off;"\
' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

EXPOSE 80

CMD ["/docker-entrypoint.sh"] 