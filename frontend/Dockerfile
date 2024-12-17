FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

RUN touch .env

EXPOSE 3000
CMD ["npm", "start"] 