# ShortTune API 🎵

Complete API for creating short music videos with advanced search, download, transcription, and audio editing capabilities.

## 🚀 Key Features

- **🔍 Smart Search**: YouTube Music integration for finding music tracks
- **📥 Secure Download**: Audio download in MP3/WAV formats with validation
- **🎤 Precise Transcription**: Local Whisper + OpenAI fallback with word-level timestamps
- **✂️ Advanced Cutting**: Precise audio editing with FFmpeg integration
- **🛡️ Rate Limiting**: Protection against abuse (10 req/min configurable)
- **🧹 Auto-Cleanup**: Automatic temporary file management
- **📚 Documentation**: Automatic Swagger/OpenAPI documentation
- **🐳 Docker Ready**: Complete containerization for production deployment
- **🔧 Modular Architecture**: Clean separation of concerns with routers/services/utils
- **⚡ Async Performance**: Full async/await implementation for optimal performance

## 📋 Requirements

- **Python 3.8+** (recommended 3.10+)
- **FFmpeg** installed on system (auto-configured)
- **Stable internet** connection
- **4GB+ RAM** (for local transcription)
- **Storage**: 2GB+ free space for temporary files

## 🛠️ FFmpeg Installation

FFmpeg is required for audio processing. Install it first:

### Windows

```bash
# Using Chocolatey (recommended)
choco install ffmpeg

# Using Scoop
scoop install ffmpeg

# Manual download from https://ffmpeg.org/download.html
# Extract to C:\ffmpeg and add C:\ffmpeg\bin to PATH
```

### Linux (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install ffmpeg
```

### macOS

```bash
# Using Homebrew
brew install ffmpeg

# Using MacPorts
sudo port install ffmpeg
```

### Verify Installation

```bash
ffmpeg -version
```

> **Note**: The API will automatically detect FFmpeg in common locations and configure the PATH accordingly.

## 🔧 Quick Installation

### Option 1: Local Development

```bash
# Clone the repository
git clone <repository-url>
cd shorttune-api

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings

# Run the server
python -m uvicorn main:app --reload --port 8000
```

### Option 2: Docker (Recommended)

```bash
# Build and run with docker-compose
docker-compose up --build

# Or using Docker directly
docker build -t shorttune-api .
docker run -p 8000:8000 shorttune-api
```

### Option 3: VS Code Tasks

Use the built-in VS Code tasks for development:

- `Ctrl+Shift+P` → "Run Task" → "Run API (Development)"
- Access at http://localhost:8000

## ⚙️ Configuration

### Environment Variables (.env)

```env
# API Configuration
DEBUG=true
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# File Management
TEMP_DIR=temp
MAX_FILE_SIZE_MB=100
CLEANUP_INTERVAL_MINUTES=30
MAX_FILE_AGE_HOURS=24

# Rate Limiting
RATE_LIMIT_REQUESTS=10
RATE_LIMIT_WINDOW=60

# OpenAI (optional - for transcription fallback)
OPENAI_API_KEY=your_openai_api_key_here

# Advanced Settings
WHISPER_MODEL=base  # tiny, base, small, medium, large
AUDIO_QUALITY=high  # low, medium, high
```

## 🚀 Running the Server

```bash
# Development with auto-reload
python -m uvicorn main:app --reload --port 8000

# Production
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# Using VS Code tasks
# Ctrl+Shift+P → "Run Task" → "Run API (Development)"
```

## 📚 API Documentation

After starting the server, access:

- **Swagger UI**: http://localhost:8000/docs (Interactive API testing)
- **ReDoc**: http://localhost:8000/redoc (Clean documentation)
- **Health Check**: http://localhost:8000/health (System status)

## 🔍 API Endpoints

### 🔍 Search Music

```http
GET /search?query=Imagine Dragons Bones&limit=10
```

Search for music tracks on YouTube Music with intelligent filtering.

### 📥 Download Audio

```http
POST /download
Content-Type: application/json

{
  "video_id": "abc123",
  "format": "mp3",
  "quality": "high"
}
```

### 🎤 Transcribe Audio

```http
POST /transcribe
Content-Type: multipart/form-data

file: <audio_file>
provider: local|openai
language: en|pt|es|fr
```

### ✂️ Cut Audio

```http
POST /cut
Content-Type: application/json

{
  "filepath": "temp/audio.mp3",
  "start": 30.5,
  "end": 60.0,
  "fade_in": 0.5,
  "fade_out": 0.5
}
```

### 💚 Health Check

```http
GET /health
```

Returns system status, available services, and performance metrics.

## 🧪 Testing

### Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage report
pytest tests/ -v --cov=. --cov-report=html --cov-report=term

# Integration tests
python test_complete_integration.py

# API workflow tests
python test_api_workflow.py
```

### VS Code Test Tasks

- `Ctrl+Shift+P` → "Run Task" → "Run Tests"
- `Ctrl+Shift+P` → "Run Task" → "Run Tests with Coverage"

## 🏗️ Architecture

```
ShortTune API/
├── routers/          # API route handlers
│   ├── search.py     # Music search endpoints
│   ├── download.py   # Audio download endpoints
│   ├── transcribe.py # Transcription endpoints
│   ├── cut.py        # Audio editing endpoints
│   └── health.py     # Health check endpoints
├── services/         # Business logic layer
│   ├── youtube_music_service.py
│   ├── download_service.py
│   ├── transcription_service.py
│   └── audio_edit_service.py
├── utils/            # Utility functions
│   ├── file_manager.py
│   └── audio_converter.py
├── models/           # Pydantic schemas
│   └── schemas.py
├── config/           # Configuration
│   ├── settings.py
│   └── logging.py
└── tests/            # Test suite
    ├── test_api.py
    └── test_utils.py
```

## 🔒 Security & Performance

### Rate Limiting

- **10 requests per minute** per IP (configurable)
- Automatic temporary file cleanup
- **100MB file size limit** (configurable)
- Request timeout protection

### Privacy & Legal

- **Educational purposes only**
- **Fair use compliance**
- **Automatic content cleanup**
- **No persistent storage** of copyrighted content

**Important**: Please respect YouTube's Terms of Service and copyright laws.

## 🛠️ Technology Stack

### Core Framework

- **FastAPI 0.104.1** - Modern, fast web framework
- **Uvicorn** - Lightning-fast ASGI server
- **Pydantic v2** - Data validation and serialization

### Audio & AI Processing

- **yt-dlp (2025.05.22)** - YouTube download with SSL fixes
- **ytmusicapi (1.3.2)** - YouTube Music search integration
- **OpenAI Whisper** - Local AI transcription engine
- **FFmpeg** - Professional audio processing

### Development & Testing

- **pytest** - Comprehensive testing framework
- **Docker** - Containerization for deployment
- **slowapi** - Rate limiting middleware

### Key Dependencies

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
yt-dlp>=2025.05.22
ytmusicapi==1.3.2
openai-whisper==20231117
pydantic-settings==2.0.3
python-multipart==0.0.6
slowapi==0.1.9
pytest==7.4.3
```

## 🚀 Production Deployment

### Docker Deployment

```bash
# Build and deploy
docker-compose up --build -d

# Scale for production
docker-compose up --scale api=3
```

### Environment Setup

```bash
# Production environment
export DEBUG=false
export LOG_LEVEL=WARNING
export RATE_LIMIT_REQUESTS=30
export MAX_FILE_SIZE_MB=200
```

### Health Monitoring

- Health endpoint: `/health`
- Metrics: CPU, Memory, Disk usage
- Service status: YouTube, Whisper, FFmpeg
- Automatic log rotation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'feat: add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

### Development Guidelines

- Follow Python PEP 8 style guide
- Add tests for new features
- Update documentation
- Use conventional commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the excellent framework
- [OpenAI Whisper](https://github.com/openai/whisper) for AI transcription
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) for YouTube integration
- [FFmpeg](https://ffmpeg.org/) for audio processing

---

**Made with ❤️ for the music and AI community**
