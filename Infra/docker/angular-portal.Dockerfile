# Build for any VKP Angular portal (admin-portal, vehicle-search-portal).
# Build context = the portal root. Produces a static bundle served by nginx; API routing that the
# dev proxy.conf.json handled locally is done by the Kubernetes Ingress in-cluster.
#
#   docker build -f Infra/docker/angular-portal.Dockerfile \
#     --build-arg PROJECT=admin-portal -t vkp/admin-portal:0.1.0 Portals/admin-portal
ARG PROJECT

FROM node:20-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
# Angular CLI writes to dist/<project>/browser in v17+.
RUN npm run build

FROM nginx:1.27-alpine AS runtime
ARG PROJECT
COPY --from=build /app/dist/${PROJECT}/browser /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
