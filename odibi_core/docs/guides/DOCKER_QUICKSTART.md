# ODIBI CORE - Docker Quick Start

## 🚀 5-Second Start

```bash
docker-compose up
```

Open: **http://localhost:8501**

---

## 📦 Installation

### Prerequisites
- Docker Desktop (Windows/Mac)
- OR Docker Engine + Docker Compose (Linux)

### Download Docker
- **Windows/Mac:** https://www.docker.com/products/docker-desktop
- **Linux:** `curl -fsSL https://get.docker.com | sh`

---

## 🎯 Common Commands

### Start Studio
```bash
# Foreground (see logs)
docker-compose up

# Background (detached)
docker-compose up -d
```

### Stop Studio
```bash
# If foreground: Ctrl+C

# If background:
docker-compose down
```

### View Logs
```bash
docker-compose logs -f
```

### Restart
```bash
docker-compose restart
```

### Rebuild (after code changes)
```bash
docker-compose up --build
```

### Complete Cleanup
```bash
docker-compose down -v
```

---

## 📁 What's Included

- ✅ **LearnODIBI Studio** - Interactive Streamlit UI
- ✅ **ODIBI CORE** - Data engineering framework
- ✅ **Pandas** - DataFrame operations
- ✅ **DuckDB** - SQL support
- ✅ **Plotly** - Interactive visualizations
- ✅ **All dependencies** - Production-ready

---

## 🔧 Configuration

### Change Port
Edit `docker-compose.yml`:
```yaml
ports:
  - "9000:8501"  # Use port 9000 instead
```

### Increase Memory
Edit `docker-compose.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 4G  # 4GB instead of 2GB
```

### Custom Data Directory
Edit `docker-compose.yml`:
```yaml
volumes:
  - /path/to/my/data:/data
```

---

## 🐛 Troubleshooting

### Port already in use
```bash
# Change port in docker-compose.yml
ports:
  - "9000:8501"
```

### Container won't start
```bash
# Check logs
docker-compose logs

# Debug mode
docker-compose run odibi-studio bash
```

### Out of memory
```bash
# Increase limit in docker-compose.yml
memory: 4G
```

### Need to rebuild
```bash
docker-compose up --build --force-recreate
```

---

## 📚 More Information

- **Full Docker Guide:** [DOCKER_GUIDE.md](DOCKER_GUIDE.md)
- **Installation Guide:** [INSTALL.md](INSTALL.md)
- **Build Summary:** [DOCKER_BUILD_SUMMARY.md](DOCKER_BUILD_SUMMARY.md)
- **Main Documentation:** [README.md](README.md)

---

## 💡 Tips

1. **First time:** Build takes ~5-10 min (downloads dependencies)
2. **After that:** Start in ~5 seconds
3. **Data persists:** Files in `./logs`, `./artifacts` are saved
4. **Auto-restart:** Container restarts automatically on crash
5. **Health monitoring:** Built-in health checks

---

**That's it! Happy coding! 🎉**
