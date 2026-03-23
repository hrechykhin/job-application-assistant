# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

ARG VITE_API_BASE_URL=/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

# Serve stage with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/templates/default.conf.template

EXPOSE 80

# nginx's docker-entrypoint runs envsubst on templates/ automatically,
# replacing ${PORT} with Railway's injected PORT value.
# Falls back to 80 if PORT is not set (local dev).
ENV PORT=80
CMD ["nginx", "-g", "daemon off;"]
