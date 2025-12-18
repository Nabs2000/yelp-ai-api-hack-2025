# Docker Setup Guide

Complete guide for running Moving Assistant with Docker.

## Architecture

```
┌─────────────────────────────────────────────────┐
│                Docker Compose                    │
└─────────────────────────────────────────────────┘
                       │
        ┌──────────────┴──────────────┐
        │                              │
┌───────▼────────┐           ┌────────▼────────┐
│    Frontend    │           │    Backend      │
│   (Nginx)      │◄──────────┤   (FastAPI)     │
│   Port: 80     │   HTTP    │   Port: 8000    │
└────────────────┘           └─────────────────┘
```

## Files Overview

### Docker Configuration Files

| File | Purpose |
|------|---------|
| `docker-compose.yml` | Production setup |
| `docker-compose.dev.yml` | Development with hot reload |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend multi-stage build |
| `frontend/nginx.conf` | Nginx configuration for SPA |
| `start.sh` / `start.bat` | Quick start scripts |

## Production Setup

### 1. Prerequisites

- Docker Desktop installed and running
- 4GB+ RAM available
- Backend `.env` file configured

### 2. Build and Run

```bash
# Build images and start containers
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### 3. Access the Application

- **Frontend**: http://localhost
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Development Setup

Includes hot reload for both frontend and backend:

```bash
# Start in development mode
docker-compose -f docker-compose.dev.yml up

# Backend will reload on Python file changes
# Frontend will reload on React file changes
```

Access at:
- Frontend: http://localhost:5173 (Vite dev server)
- Backend: http://localhost:8000

## Common Commands

### Starting & Stopping

```bash
# Start services
docker-compose up

# Start in background
docker-compose up -d

# Stop services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### Viewing Logs

```bash
# All logs
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Frontend only
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100
```

### Rebuilding

```bash
# Rebuild all services
docker-compose build

# Rebuild specific service
docker-compose build backend

# Force rebuild (no cache)
docker-compose build --no-cache

# Rebuild and restart
docker-compose up --build
```

### Container Management

```bash
# List running containers
docker-compose ps

# Restart services
docker-compose restart

# Restart specific service
docker-compose restart backend

# Execute command in container
docker-compose exec backend bash
docker-compose exec frontend sh
```

## Troubleshooting

### Issue: Port Already in Use

**Error**: `Bind for 0.0.0.0:80 failed: port is already allocated`

**Solution**:
```bash
# Find what's using the port
# Windows:
netstat -ano | findstr :80

# Linux/Mac:
lsof -i :80

# Change port in docker-compose.yml
ports:
  - "8080:80"  # Use port 8080 instead
```

### Issue: Backend Not Starting

**Symptoms**: Backend container exits immediately

**Solution**:
```bash
# Check logs
docker-compose logs backend

# Common causes:
# 1. Missing .env file
cp backend/.env.example backend/.env

# 2. Invalid API keys
# Edit backend/.env with valid keys

# 3. Dependency issues
docker-compose build --no-cache backend
```

### Issue: Frontend Can't Connect to Backend

**Symptoms**: API calls fail with CORS or connection errors

**Solution**:
1. Check backend is running:
```bash
curl http://localhost:8000/docs
```

2. Verify environment variables:
```bash
# frontend/.env.local should have:
VITE_API_BASE_URL=http://localhost:8000
```

3. Rebuild frontend:
```bash
docker-compose build frontend
docker-compose up -d
```

### Issue: Database Connection Failed

**Symptoms**: Backend logs show Supabase connection errors

**Solution**:
```bash
# Verify Supabase credentials in backend/.env
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_API_KEY=xxx

# Test connection from container
docker-compose exec backend python -c "from supabase_init import supabase; print(supabase)"
```

### Issue: Slow Performance

**Causes & Solutions**:

1. **Docker Desktop Resource Limits**
   - Increase RAM: Docker Desktop → Settings → Resources
   - Recommended: 4GB+ RAM

2. **Image Layers Too Large**
```bash
# Check image sizes
docker images

# Rebuild with --no-cache
docker-compose build --no-cache
```

3. **Volume Mounting Overhead (Dev Mode)**
   - Use production mode for better performance
   - Or optimize Docker Desktop file sharing

### Issue: Cannot Install httpx

**Error**: `No matching distribution found for httpx`

**Solution**:
```bash
# Update pyproject.toml is correct
# Rebuild backend
docker-compose build --no-cache backend

# Or install manually in container
docker-compose exec backend pip install httpx
```

## Environment Variables

### Backend (.env)

Required variables:
```env
CLIENT_ID=your_yelp_client_id
YELP_API_KEY=your_yelp_api_key
OPENAI_API_KEY=sk-proj-xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_API_KEY=eyJxxx
```

### Frontend (.env.local)

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Multi-Platform Builds

Building for different architectures:

```bash
# Build for ARM64 (Apple Silicon, Raspberry Pi)
docker buildx build --platform linux/arm64 -t moving-assistant-backend ./backend

# Build for AMD64 (Intel/AMD)
docker buildx build --platform linux/amd64 -t moving-assistant-backend ./backend

# Build for both
docker buildx build --platform linux/amd64,linux/arm64 -t moving-assistant-backend ./backend
```

## Production Deployment

### Using Docker Compose

```bash
# Set production environment
export COMPOSE_FILE=docker-compose.yml

# Start with restart policy
docker-compose up -d
```

### Environment Variables for Production

```bash
# Use secrets or environment variable management
# Don't commit .env files!

# Option 1: Use .env file (gitignored)
docker-compose --env-file .env.production up -d

# Option 2: Export variables
export YELP_API_KEY=xxx
export OPENAI_API_KEY=xxx
docker-compose up -d
```

### Reverse Proxy (Nginx/Caddy)

Example nginx config for hosting on a domain:

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Health Checks

Both services include health checks:

```yaml
# Backend health check
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/docs"]
  interval: 30s
  timeout: 10s
  retries: 3

# Frontend health check
healthcheck:
  test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:80"]
  interval: 30s
  timeout: 10s
  retries: 3
```

Check health status:
```bash
docker-compose ps
```

## Cleaning Up

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove all unused Docker resources
docker system prune -a

# Remove specific images
docker rmi moving-assistant-backend
docker rmi moving-assistant-frontend
```

## CI/CD Integration

Example GitHub Actions workflow:

```yaml
name: Build Docker Images

on:
  push:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2

      - name: Build images
        run: docker-compose build

      - name: Run tests
        run: docker-compose up -d && sleep 10 && docker-compose down
```

## Best Practices

1. **Never commit `.env` files** - Use `.env.example` templates
2. **Use `.dockerignore`** - Exclude unnecessary files from build context
3. **Multi-stage builds** - Keep production images small
4. **Health checks** - Monitor container health
5. **Resource limits** - Set memory/CPU limits in production
6. **Logging** - Use centralized logging (ELK, Splunk, etc.)
7. **Security** - Keep base images updated

## Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [FastAPI in Docker](https://fastapi.tiangolo.com/deployment/docker/)
- [Nginx Documentation](https://nginx.org/en/docs/)

---

**Need Help?**

Check logs first:
```bash
docker-compose logs -f
```

Open an issue on GitHub with:
- Error messages from logs
- Your `docker-compose ps` output
- OS and Docker version
