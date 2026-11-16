# =============================================================================
# Frontend Dockerfile — multi-stage build (Node build → Nginx serve)
# =============================================================================

# ---------------------------------------------------------------------------
# Stage 1: builder — compile the React/Vite app
# ---------------------------------------------------------------------------
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package manifests first for better layer caching
COPY package.json package-lock.json* ./

# Install exact versions from lockfile (clean install, no audit)
RUN npm ci --silent

# Copy the rest of the source
COPY . .

# Build the production bundle (output goes to /app/dist)
RUN npm run build

# ---------------------------------------------------------------------------
# Stage 2: runtime — serve with Nginx
# ---------------------------------------------------------------------------
FROM nginx:alpine AS runtime

# Remove the default Nginx config
RUN rm /etc/nginx/conf.d/default.conf

# Copy our custom Nginx config
COPY nginx.conf /etc/nginx/conf.d/app.conf

# Copy the compiled frontend from the builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Nginx listens on port 80
EXPOSE 80

# Nginx runs in the foreground by default in its Docker image
CMD ["nginx", "-g", "daemon off;"]
