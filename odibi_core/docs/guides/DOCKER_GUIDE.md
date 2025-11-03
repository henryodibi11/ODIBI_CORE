# ODIBI CORE - Docker Deployment Guide

## Overview

This guide covers Docker deployment of ODIBI CORE with LearnODIBI Studio (Streamlit UI).

**What's included:**
- 🐳 Multi-stage Dockerfile (optimized for production)
- 🚀 Docker Compose for one-command deployment
- 🔒 Security best practices (non-root user, minimal image)
- 📊 LearnODIBI Studio on port 8501
- 💾 Persistent volumes for logs and artifacts

---

## Quick Start (5 seconds)

```bash
docker-compose up
```

Open browser: [http://localhost:8501](http://localhost:8501)

That's it! 🎉

---

## Detailed Installation

### Prerequisites

1. **Install Docker Desktop:**
   - [Windows/Mac](https://www.docker.com/products/docker-desktop)
   - Linux: `curl -fsSL https://get.docker.com | sh`

2. **Verify installation:**
   ```bash
   docker --version
   docker-compose --version
   ```

### Build and Run

**Option 1: Docker Compose (Recommended)**

```bash
# Start in foreground (see logs in terminal)
docker-compose up

# Start in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

**Option 2: Docker CLI**

```bash
# Build image
docker build -t odibi-core:latest .

# Run container
docker run -d \
  --name odibi-studio \
  -p 8501:8501 \
  -v $(pwd)/logs:/logs \
  -v $(pwd)/artifacts:/app/artifacts \
  odibi-core:latest

# View logs
docker logs -f odibi-studio

# Stop
docker stop odibi-studio
docker rm odibi-studio
```

---

## Architecture

### Multi-Stage Build

The Dockerfile uses a two-stage build:

1. **Builder Stage** - Installs dependencies with build tools
2. **Runtime Stage** - Minimal production image (python:3.10-slim)

**Benefits:**
- ✅ Smaller final image (~500MB vs ~1.5GB)
- ✅ Faster deployments
- ✅ Reduced attack surface

### Image Layers

```
python:3.10-slim (base)
├── System packages (gcc removed after build)
├── Python dependencies
│   ├── pandas, streamlit, plotly
│   ├── duckdb, watchdog
│   └── ODIBI CORE package
├── Application code
└── Non-root user (odibi:odibi)
```

---

## Configuration

### Environment Variables

Set in `docker-compose.yml` or pass with `-e`:

```yaml
environment:
  # Streamlit
  - STREAMLIT_SERVER_PORT=8501
  - STREAMLIT_SERVER_ADDRESS=0.0.0.0
  - STREAMLIT_SERVER_HEADLESS=true
  - STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
  
  # ODIBI CORE
  - ODIBI_ENV=production
  - ODIBI_LOG_LEVEL=INFO
  
  # Python
  - PYTHONUNBUFFERED=1
```

### Volume Mounts

Persist data between container restarts:

```yaml
volumes:
  - ./logs:/logs                    # Application logs
  - ./artifacts:/app/artifacts      # Output files
  - ./data:/data                    # Input data
  - ./examples:/app/examples        # Example notebooks
```

**Custom paths:**

```yaml
volumes:
  - /path/to/my/data:/data
  - /path/to/my/logs:/logs
```

### Port Mapping

Default: `8501:8501` (host:container)

**Change host port:**

```yaml
ports:
  - "9000:8501"  # Access at http://localhost:9000
```

---

## Resource Management

### Memory and CPU Limits

In `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'      # Max 2 CPU cores
      memory: 2G       # Max 2GB RAM
    reservations:
      cpus: '0.5'      # Reserved 0.5 cores
      memory: 512M     # Reserved 512MB
```

**Adjust for your workload:**
- Small datasets: 1 CPU, 1GB RAM
- Large datasets: 4 CPUs, 4GB RAM

---

## Health Checks

Built-in health monitoring:

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1
```

**Check health:**

```bash
docker-compose ps
# Healthy status means Streamlit is running
```

---

## Common Tasks

### View Logs

```bash
# All logs
docker-compose logs

# Follow logs (live)
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service
docker-compose logs odibi-studio
```

### Restart Service

```bash
# Restart without rebuilding
docker-compose restart

# Rebuild and restart (after code changes)
docker-compose up --build

# Force recreate
docker-compose up --force-recreate
```

### Execute Commands in Container

```bash
# Open bash shell
docker-compose exec odibi-studio bash

# Run Python command
docker-compose exec odibi-studio python -c "from odibi_core.engine import PandasEngineContext; print('OK')"

# Run tests
docker-compose exec odibi-studio pytest
```

### Cleanup

```bash
# Stop and remove containers
docker-compose down

# Remove containers and volumes
docker-compose down -v

# Remove containers, volumes, and images
docker-compose down -v --rmi all

# Full cleanup (remove all unused Docker resources)
docker system prune -a --volumes
```

---

## Production Deployment

### Security Best Practices

✅ **Non-root user** - Container runs as `odibi:odibi` (UID 1000)
✅ **Minimal base image** - python:3.10-slim (no unnecessary packages)
✅ **No secrets in image** - Use environment variables or secrets management
✅ **Read-only filesystem** - Consider adding `--read-only` flag with tmpfs

**Example production run:**

```bash
docker run -d \
  --name odibi-studio \
  --read-only \
  --tmpfs /tmp \
  -p 8501:8501 \
  -v $(pwd)/logs:/logs:rw \
  -v $(pwd)/artifacts:/app/artifacts:rw \
  -e ODIBI_ENV=production \
  odibi-core:latest
```

### Reverse Proxy (Nginx)

Expose via Nginx for HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name studio.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Cloud Deployment

**AWS ECS:**

```bash
# Build and push to ECR
aws ecr get-login-password | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
docker tag odibi-core:latest <account>.dkr.ecr.<region>.amazonaws.com/odibi-core:latest
docker push <account>.dkr.ecr.<region>.amazonaws.com/odibi-core:latest
```

**Google Cloud Run:**

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/odibi-core
gcloud run deploy odibi-studio --image gcr.io/<project-id>/odibi-core --platform managed
```

**Azure Container Instances:**

```bash
# Push to ACR
az acr build --registry <registry-name> --image odibi-core:latest .
az container create --resource-group <rg> --name odibi-studio --image <registry-name>.azurecr.io/odibi-core:latest --ports 8501
```

---

## Troubleshooting

### Issue: Port 8501 already in use

**Solution:**

```bash
# Change host port
docker-compose down
# Edit docker-compose.yml: ports: - "9000:8501"
docker-compose up
```

### Issue: Permission denied on volumes

**Solution:**

```bash
# Fix ownership
sudo chown -R 1000:1000 logs/ artifacts/

# Or run with current user
docker-compose run --user $(id -u):$(id -g) odibi-studio
```

### Issue: Container exits immediately

**Solution:**

```bash
# Check logs
docker-compose logs

# Check health
docker-compose ps

# Debug with bash
docker-compose run odibi-studio bash
```

### Issue: Out of memory

**Solution:**

```yaml
# Increase memory limit in docker-compose.yml
deploy:
  resources:
    limits:
      memory: 4G
```

### Issue: Slow builds

**Solution:**

```bash
# Use BuildKit for faster builds
DOCKER_BUILDKIT=1 docker build -t odibi-core:latest .

# Or enable globally
export DOCKER_BUILDKIT=1
```

---

## Performance Optimization

### Build Cache

Use `.dockerignore` to exclude unnecessary files:

```
# Already configured in .dockerignore
__pycache__/
*.pyc
.git/
tests/
```

### Multi-platform Builds

Build for multiple architectures:

```bash
docker buildx create --use
docker buildx build --platform linux/amd64,linux/arm64 -t odibi-core:latest .
```

### Layer Caching

Order Dockerfile instructions from least to most frequently changing:

1. Base image
2. System dependencies
3. Python dependencies (rarely change)
4. Application code (changes often)

---

## Monitoring

### Container Metrics

```bash
# Real-time stats
docker stats odibi-studio

# Resource usage
docker-compose top
```

### Application Logs

```bash
# Streamlit logs
docker-compose logs -f odibi-studio

# ODIBI CORE logs (in mounted volume)
tail -f logs/odibi.log
```

### Health Endpoint

```bash
# Check Streamlit health
curl http://localhost:8501/_stcore/health

# Expected response: {"status": "ok"}
```

---

## Development Workflow

### Live Code Reload

Mount source code for development:

```yaml
volumes:
  - ./odibi_core:/app/odibi_core  # Live reload
  - ./examples:/app/examples
```

Streamlit auto-reloads on file changes.

### Debug Mode

```yaml
environment:
  - ODIBI_LOG_LEVEL=DEBUG
  - STREAMLIT_LOGGER_LEVEL=debug
```

### VS Code Remote Container

Add `.devcontainer/devcontainer.json`:

```json
{
  "name": "ODIBI CORE",
  "dockerComposeFile": "../docker-compose.yml",
  "service": "odibi-studio",
  "workspaceFolder": "/app"
}
```

---

## FAQ

**Q: Can I run without Docker Compose?**  
A: Yes, use `docker run` with manual port and volume mappings.

**Q: How do I update the image?**  
A: `docker-compose up --build` rebuilds with latest code.

**Q: Can I use with Spark?**  
A: Yes, but add PySpark to Dockerfile dependencies and increase memory limits.

**Q: Is this production-ready?**  
A: Yes, with proper security (HTTPS, secrets management, resource limits).

**Q: How do I backup data?**  
A: Volume mounts (`./logs`, `./artifacts`) persist data. Back up these directories.

---

## Next Steps

1. ✅ Start with `docker-compose up`
2. ✅ Access Studio at http://localhost:8501
3. ✅ Explore interactive tutorials
4. ✅ Customize `docker-compose.yml` for your needs
5. ✅ Deploy to cloud (AWS/GCP/Azure)

**Resources:**
- [INSTALL.md](INSTALL.md) - Full installation guide
- [README.md](README.md) - ODIBI CORE documentation
- [Docker Docs](https://docs.docker.com/) - Official Docker documentation
