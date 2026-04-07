FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN chmod +x node_modules/.bin/vite
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL
ARG VITE_WS_URL
ENV VITE_WS_URL=$VITE_WS_URL
RUN node_modules/.bin/vite build