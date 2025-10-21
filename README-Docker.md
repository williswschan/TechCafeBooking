# TechCafeBooking - Docker Container

This document explains how to build and run the TechCafeBooking application as a Docker container.

## 🐳 Quick Start

### Build the Docker Image
```bash
# Build with default tag (latest)
./build-docker.sh

# Build with custom tag
./build-docker.sh v1.0
```

### Run with Docker Compose (Recommended)
```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Run with Docker directly
```bash
# Run the container
docker run -d -p 5000:5000 --name techcafebooking-app techcafebooking:latest

# View logs
docker logs -f techcafebooking-app

# Stop the container
docker stop techcafebooking-app
docker rm techcafebooking-app
```

## 🔧 Configuration

### Environment Variables
- `FLASK_DEBUG`: Set to `False` for production (default: `False`)
- `ADMIN_PASSWORD`: Admin panel password (default: `admin123`)

### Volumes
The following files are mounted as volumes to persist data:
- `bookings.json` - Main booking data
- `bookings_2025-10-22.csv` - Daily booking exports
- `bookings_2025-10-23.csv` - Daily booking exports
- `bad_words.txt` - Bad words filter
- `display_name.txt` - Display names

## 📦 Image Details

- **Base Image**: Python 3.9-slim
- **Working Directory**: `/app`
- **Port**: 5000
- **User**: Non-root user `app` for security
- **Health Check**: HTTP check on `/` endpoint

## 🚀 Production Deployment

### Using Docker Compose
1. Update environment variables in `docker-compose.yml`
2. Set proper admin password
3. Configure volume mounts for data persistence
4. Run: `docker-compose up -d`

### Using Docker Swarm/Kubernetes
The image can be deployed to container orchestration platforms:
- Docker Swarm
- Kubernetes
- AWS ECS
- Azure Container Instances

## 🔍 Troubleshooting

### View Container Logs
```bash
docker logs techcafebooking-app
```

### Access Container Shell
```bash
docker exec -it techcafebooking-app /bin/bash
```

### Check Container Health
```bash
docker inspect techcafebooking-app | grep -A 10 Health
```

### Restart Container
```bash
docker restart techcafebooking-app
```

## 📋 Management Commands

```bash
# List all containers
docker ps -a

# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# View resource usage
docker stats techcafebooking-app
```

## 🔒 Security Notes

- Container runs as non-root user
- No unnecessary packages installed
- Health checks enabled
- Environment variables for configuration
- Volume mounts for data persistence
