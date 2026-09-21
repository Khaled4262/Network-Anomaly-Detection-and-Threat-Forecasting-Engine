# Build context is src/frontend/ itself.
# VITE_API_BASE_URL is baked in at BUILD time (Vite inlines env vars into
# the static bundle) -- it is NOT read at container-start time. That means
# "localhost:8000" only works for local docker-compose testing. For an EC2
# deploy you MUST pass the instance's public IP/domain as the build arg,
# or every browser that loads the page will try to reach its own localhost.
# See DEPLOYMENT.md.
#
# Build:  docker build -f Dockerfile --build-arg VITE_API_BASE_URL=http://<EC2-PUBLIC-IP>:8000 -t nadtfe-frontend .
# Run:    docker run -p 80:80 nadtfe-frontend

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
ARG VITE_API_BASE_URL=http://localhost:8000
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
RUN npm run build

FROM nginx:alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
