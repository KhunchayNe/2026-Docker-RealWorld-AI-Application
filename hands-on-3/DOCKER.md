# Docker Guide - Oil Price Prediction Application

## Overview

This application uses Docker and Docker Compose to create a complete development environment with:
- **Frontend**: React + Vite (TypeScript)
- **Backend**: FastAPI (Python 3.12)
- **Vector Database**: Qdrant
- **Reverse Proxy**: Traefik

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Traefik Proxy                        │
│                    (Port 80 on Host)                        │
└─────────────────────────────────────────────────────────────┘
                              │
            ┌─────────────────┴─────────────────┐
            │                                   │
            ▼                                   ▼
┌──────────────────────┐         ┌──────────────────────┐
│   React Client       │         │   FastAPI Backend    │
│   (Port 5173)        │         │   (Port 8000)        │
│                      │         │                      │
│ - Vite Dev Server    │         │ - Prediction API     │
│ - Hot Reload         │         │ - Qdrant Integration │
└──────────────────────┘         └──────────────────────┘
                                          │
                                          ▼
                              ┌──────────────────────┐
                              │      Qdrant          │
                              │   (Port 6333)        │
                              │                      │
                              │ - Vector Storage     │
                              │ - Similarity Search  │
                              └──────────────────────┘
```

## Quick Start

### Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose)
- Docker Compose v2.20+ (for Compose Watch feature)

### Start the Application

```bash
# From the hands-on-3 directory
docker compose up --build
```

This will:
1. Build the Docker images
2. Start all services (proxy, client, backend, qdrant)
3. Enable hot-reload for development
4. Expose the application on http://localhost

### Access Points

- **Main Application**: http://localhost
- **API Endpoints**: http://localhost/api/*
- **Qdrant Web UI**: http://qdrant.localhost

## Dockerfile Stages

### Client Stages

#### `client-base`
- Installs Node.js dependencies
- Copies source code
- Shared base for dev and build stages

#### `client-dev`
- Runs Vite development server
- Supports hot-reload via Compose Watch
- Exposed on port 5173

#### `client-build`
- Builds production bundle
- Outputs to `./dist`
- Used by final production stage

### Backend Stages

#### `backend-base`
- Python 3.12 slim base image
- Installs dependencies from `requirements.txt`
- Copies Python source code
- Exposed on port 8000

#### `backend-dev`
- Runs FastAPI with `--reload` flag
- Auto-restarts on code changes
- Connects to Qdrant service

#### `final`
- Production-ready image
- Includes bundled client static files
- Single container deployment

## Docker Compose Services

### 1. Proxy (Traefik)

```yaml
proxy:
  image: traefik:v3.6
  ports:
    - 80:80
```

**Purpose**: Routes requests to appropriate services

**Routing Rules**:
- `localhost/api/*` → Backend (port 8000)
- `localhost` → Client (port 5173)
- `qdrant.localhost` → Qdrant Web UI (port 6333)

### 2. Backend (FastAPI)

```yaml
backend:
  build:
    target: backend-dev
  environment:
    QDRANT_HOST: qdrant
    QDRANT_PORT: 6333
  depends_on:
    qdrant:
      condition: service_healthy
```

**Features**:
- Auto-reload on code changes
- Connects to Qdrant vector database
- Health check ensures Qdrant is ready first

**Compose Watch**:
```yaml
develop:
  watch:
    - path: ./backend
      action: sync
      target: /app
```

### 3. Client (React + Vite)

```yaml
client:
  build:
    target: client-dev
  develop:
    watch:
      - path: ./client/src
        action: sync
        target: /usr/local/app/src
```

**Features**:
- Hot Module Replacement (HMR)
- Auto-reload on code changes
- TypeScript support

### 4. Qdrant (Vector Database)

```yaml
qdrant:
  image: qdrant/qdrant:v1.12.0
  volumes:
    - oil-price-qdrant-data:/qdrant/storage
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:6333/health"]
```

**Features**:
- Persistent storage via Docker volume
- Health check for service readiness
- Used for similarity search

### 5. Qdrant Web UI

```yaml
qdrant-web-ui:
  image: qdrant/qdrant:v1.12.0
  labels:
    traefik.http.routers.qdrant.rule: Host(`qdrant.localhost`)
```

**Purpose**: Web interface for Qdrant management

## Common Commands

### Development

```bash
# Start all services
docker compose up

# Start with build (first time or after changes)
docker compose up --build

# Start in detached mode
docker compose up -d

# View logs
docker compose logs -f

# View specific service logs
docker compose logs -f backend
docker compose logs -f client
```

### Stopping

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v

# Stop but keep containers
docker compose stop
```

### Rebuilding

```bash
# Rebuild specific service
docker compose build backend

# Rebuild all services
docker compose build

# Rebuild without cache
docker compose build --no-cache
```

### Debugging

```bash
# Enter backend container
docker compose exec backend bash

# Enter client container
docker compose exec client sh

# View running containers
docker compose ps

# Check service health
docker compose ps
```

## Development Workflow

### 1. Initial Setup

```bash
# Clone and navigate to project
cd hands-on-3

# Start services
docker compose up --build
```

### 2. Development

**Backend Changes**:
- Edit files in `backend/`
- Changes are automatically synced to container
- FastAPI auto-reloads (watch via `uvicorn --reload`)

**Frontend Changes**:
- Edit files in `client/src/`
- Changes are automatically synced
- Vite HMR updates browser instantly

**Dependencies**:

```bash
# Backend: Add new Python package
echo "new-package==1.0.0" >> backend/requirements.txt
docker compose build backend
docker compose up backend

# Frontend: Add new npm package
cd client
npm install new-package
# Compose Watch detects package.json change and rebuilds
```

### 3. Testing

```bash
# Test API endpoints
curl http://localhost/api/

# Test with web interface
open http://localhost

# Test Qdrant connection
curl http://qdrant.localhost/
```

### 4. Cleanup

```bash
# Stop services
docker compose down

# Remove volumes (deletes Qdrant data!)
docker compose down -v

# Clean build cache
docker builder prune
```

## Volumes

### oil-price-qdrant-data

**Purpose**: Persist Qdrant vector database

**Location**: Docker managed volume

**Backup**:
```bash
# Backup Qdrant data
docker run --rm -v oil-price-qdrant-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/qdrant-backup.tar.gz /data

# Restore Qdrant data
docker run --rm -v oil-price-qdrant-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/qdrant-backup.tar.gz -C /
```

## Environment Variables

### Backend

```yaml
QDRANT_HOST: qdrant      # Qdrant service hostname
QDRANT_PORT: 6333        # Qdrant port
```

### Adding Environment Variables

Edit `compose.yaml`:

```yaml
backend:
  environment:
    QDRANT_HOST: qdrant
    QDRANT_PORT: 6333
    NEW_VAR: value
```

Or create `.env` file:

```bash
QDRANT_HOST=qdrant
QDRANT_PORT=6333
```

## Production Deployment

### Build Production Image

```bash
# Build final stage
docker build --target final -t oil-price-app:prod .

# Run production container
docker run -p 8000:8000 oil-price-app:prod
```

### Production Compose

Create `compose.prod.yaml`:

```yaml
services:
  backend:
    build:
      target: final
    environment:
      QDRANT_HOST: qdrant
      QDRANT_PORT: 6333
    ports:
      - 8000:8000

  qdrant:
    image: qdrant/qdrant:v1.12.0
    volumes:
      - oil-price-qdrant-data:/qdrant/storage
```

```bash
docker compose -f compose.prod.yaml up -d
```

## Troubleshooting

### Port Already in Use

```bash
# Check what's using port 80
sudo lsof -i :80

# Change Traefik port in compose.yaml
ports:
  - 8080:80  # Use port 8080 instead
```

### Container Won't Start

```bash
# Check logs
docker compose logs backend

# Check container status
docker compose ps

# Rebuild without cache
docker compose build --no-cache backend
```

### Qdrant Connection Issues

```bash
# Check Qdrant is healthy
docker compose exec qdrant curl http://localhost:6333/health

# Check backend can reach Qdrant
docker compose exec backend ping qdrant

# View Qdrant logs
docker compose logs qdrant
```

### Hot Reload Not Working

```bash
# Ensure Compose Watch is working
docker compose up --build

# Check if files are syncing
docker compose exec backend ls -la /app

# Restart service
docker compose restart backend
```

### Client Build Issues

```bash
# Clear node modules
rm -rf client/node_modules
docker compose build --no-cache client

# Check client logs
docker compose logs client
```

## Performance Tips

### 1. Use BuildKit

```bash
export DOCKER_BUILDKIT=1
docker compose build
```

### 2. Layer Caching

- Don't change `requirements.txt` frequently
- Group related COPY commands
- Use `.dockerignore` to exclude unnecessary files

### 3. Resource Limits

Add to `compose.yaml`:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
```

## Security Notes

### Production Checklist

- [ ] Change default passwords
- [ ] Use secrets for sensitive data
- [ ] Enable HTTPS/TLS
- [ ] Restrict network access
- [ ] Scan images for vulnerabilities
- [ ] Keep images updated
- [ ] Use non-root user in containers

### Example Secrets

```bash
# Create secrets
echo "secret_password" | docker secret create qdrant_password -

# Use in compose.yaml
services:
  qdrant:
    secrets:
      - qdrant_password

secrets:
  qdrant_password:
    external: true
```

## Next Steps

1. **Development**: Start coding with hot-reload
2. **Testing**: Use web interface at http://localhost
3. **Qdrant UI**: Manage vectors at http://qdrant.localhost
4. **API Testing**: Check endpoints at http://localhost/api/
5. **Production**: Build and deploy final image

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Watch](https://docs.docker.com/compose/file-watch/)
- [FastAPI Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Vite Docker](https://vitejs.dev/guide/backend-integration.html)
- [Qdrant Documentation](https://qdrant.tech/documentation/)
- [Traefik Documentation](https://doc.traefik.io/traefik/)
