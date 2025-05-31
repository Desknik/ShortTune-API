# ShortTune API - Deployment Guide 🚀

This guide covers deployment scenarios and production considerations for the ShortTune API.

## 📋 Prerequisites

### Required Software
- **Python 3.8+** (recommended 3.10+)
- **FFmpeg** (auto-configured or manual installation)
- **Git** for repository cloning
- **Docker** (optional, for containerized deployment)

### System Requirements
- **Memory**: 4GB+ RAM (for Whisper transcription)
- **Storage**: 2GB+ free space for temporary files
- **Network**: Stable internet connection
- **OS**: Windows, Linux, or macOS

## 🔧 Local Development Setup

### 1. Clone Repository
```bash
git clone https://github.com/Desknik/ShortTune-API.git
cd ShortTune-API
```

### 2. Install FFmpeg
**Windows:**
```bash
# Using Chocolatey (recommended)
choco install ffmpeg

# Using Scoop
scoop install ffmpeg

# Manual: Download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update && sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Verify Installation:**
```bash
ffmpeg -version
```

### 3. Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings
# Minimum required:
DEBUG=true
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### 5. Run Development Server
```bash
# Using uvicorn directly
python -m uvicorn main:app --reload --port 8000

# Using VS Code tasks (if in VS Code)
# Ctrl+Shift+P → "Run Task" → "Run API (Development)"
```

## 🐳 Docker Deployment

### Option 1: Docker Compose (Recommended)
```bash
# Build and run
docker-compose up --build

# Run in background
docker-compose up --build -d

# Scale for production
docker-compose up --scale api=3 -d
```

### Option 2: Docker Direct
```bash
# Build image
docker build -t shorttune-api:latest .

# Run container
docker run -p 8000:8000 \
  -e DEBUG=false \
  -e LOG_LEVEL=WARNING \
  -v $(pwd)/temp:/app/temp \
  -v $(pwd)/logs:/app/logs \
  shorttune-api:latest
```

## 🌐 Production Deployment

### Environment Variables for Production
```env
# Production settings
DEBUG=false
LOG_LEVEL=WARNING
HOST=0.0.0.0
PORT=8000

# Performance tuning
RATE_LIMIT_REQUESTS=30
RATE_LIMIT_WINDOW=60
MAX_FILE_SIZE_MB=200
CLEANUP_INTERVAL_MINUTES=15
MAX_FILE_AGE_HOURS=12

# Security
# Add your OpenAI API key if using OpenAI transcription
OPENAI_API_KEY=your_production_key_here
```

### Nginx Reverse Proxy
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # File upload size limit
        client_max_body_size 200M;
        
        # Timeout settings
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 300s;
    }
}
```

### Systemd Service (Linux)
```ini
[Unit]
Description=ShortTune API
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/shorttune-api
Environment=PATH=/opt/shorttune-api/venv/bin
ExecStart=/opt/shorttune-api/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

## ☁️ Cloud Deployment

### AWS EC2
1. **Launch Instance**: Ubuntu 20.04+ with 4GB+ RAM
2. **Security Groups**: Open port 8000 (or 80/443 with nginx)
3. **Install Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3-pip ffmpeg git nginx
   ```
4. **Deploy Application**: Follow local setup steps
5. **Configure Nginx**: Use provided nginx configuration

### Google Cloud Platform
1. **Compute Engine**: Create VM with Ubuntu 20.04+
2. **Firewall Rules**: Allow HTTP/HTTPS traffic
3. **Install Dependencies**: Same as AWS
4. **Deploy**: Follow standard deployment steps

### Azure VM
1. **Create VM**: Ubuntu Server 20.04+
2. **Network Security**: Open required ports
3. **Install Dependencies**: Standard Linux installation
4. **Deploy**: Follow deployment guide

### Container Platforms
- **Google Cloud Run**: Deploy docker image directly
- **AWS ECS/Fargate**: Container deployment
- **Azure Container Instances**: Serverless containers

## 🔍 Health Monitoring

### Health Check Endpoint
```bash
curl http://localhost:8000/health
```

Response includes:
- System status
- Service availability (YouTube, Whisper, FFmpeg)
- Performance metrics
- Disk space and memory usage

### Log Files
- **Application logs**: `logs/app.log`
- **Error tracking**: Structured JSON logging
- **Performance metrics**: Request timing and resource usage

### Monitoring Setup
```bash
# Log rotation (add to crontab)
0 2 * * * find /path/to/logs -name "*.log" -mtime +7 -delete

# Disk space monitoring
df -h /path/to/temp/

# Process monitoring
ps aux | grep uvicorn
```

## 🔒 Security Considerations

### Rate Limiting
- Default: 10 requests per minute per IP
- Configurable via `RATE_LIMIT_REQUESTS` and `RATE_LIMIT_WINDOW`
- Implement additional rate limiting at nginx level for production

### File Security
- Automatic file cleanup enabled
- Temporary files isolated in `temp/` directory
- No persistent storage of copyrighted content

### API Security
```bash
# Add authentication middleware (optional)
# Implement API keys or JWT tokens for production use
```

## 🧪 Testing Deployment

### Functional Tests
```bash
# Run test suite
python -m pytest tests/ -v

# Integration tests
python test_complete_integration.py

# API workflow tests
python test_api_workflow.py
```

### Load Testing
```bash
# Install load testing tools
pip install locust

# Run basic load test
python load_test.py
```

### API Validation
```bash
# Test all endpoints
curl -X GET "http://localhost:8000/health"
curl -X GET "http://localhost:8000/search?query=test&limit=5"
curl -X POST "http://localhost:8000/download" -H "Content-Type: application/json" -d '{"video_id":"test","format":"mp3"}'
```

## 🚨 Troubleshooting

### Common Issues

**FFmpeg Not Found:**
```bash
# Check FFmpeg installation
ffmpeg -version

# Manual PATH configuration
export PATH="/usr/local/bin:$PATH"
```

**Memory Issues:**
```bash
# Monitor memory usage
free -h
htop

# Reduce Whisper model size
export WHISPER_MODEL=tiny  # or base instead of large
```

**Port Conflicts:**
```bash
# Check port usage
netstat -tlnp | grep 8000

# Use different port
python -m uvicorn main:app --port 8001
```

**Permission Errors:**
```bash
# Fix file permissions
chmod 755 /path/to/app
chown -R user:group /path/to/app
```

## 📊 Performance Tuning

### Resource Optimization
- **Whisper Model**: Use `base` for balanced performance/accuracy
- **File Cleanup**: Reduce `MAX_FILE_AGE_HOURS` for faster cleanup
- **Rate Limiting**: Adjust based on server capacity

### Scaling Strategies
- **Horizontal**: Multiple container instances with load balancer
- **Vertical**: Increase RAM/CPU for better transcription performance
- **Caching**: Implement Redis for frequent searches

## 📝 Maintenance

### Regular Tasks
- **Log rotation**: Weekly cleanup of old logs
- **Temp files**: Automatic cleanup via scheduled tasks
- **Dependencies**: Monthly update of Python packages
- **Security**: Regular review of access logs

### Updates
```bash
# Update dependencies
pip install -r requirements.txt --upgrade

# Restart service
systemctl restart shorttune-api

# Verify functionality
curl http://localhost:8000/health
```

---

**Need Help?** Check the main [README.md](README.md) for detailed API documentation and examples.
