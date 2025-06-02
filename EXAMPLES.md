# ShortTune API - Usage Examples & Cookbook

This guide provides comprehensive examples for using the ShortTune API, from basic operations to complete workflows.

## 🚀 Quick Start

### Start the Server

```bash
# Local development
python -m uvicorn main:app --reload --port 8000

# Docker
docker-compose up --build

# Access documentation
open http://localhost:8000/docs
```

## 🔍 1. Music Search

### Basic Search

```bash
curl "http://localhost:8000/search?query=Imagine Dragons Bones&limit=5"
```

### Advanced Search with Filters

```bash
curl -X POST "http://localhost:8000/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Imagine Dragons Bones",
    "limit": 10,
    "filter": "songs"
  }'
```

### Python Example

```python
import requests

response = requests.get(
    "http://localhost:8000/search",
    params={"query": "Imagine Dragons Bones", "limit": 5}
)
results = response.json()
print(f"Found {len(results['results'])} tracks")
```

### Response Format

```json
{
  "results": [
    {
      "video_id": "lDdmYccv1fo",
      "title": "Bones",
      "artist": "Imagine Dragons",
      "album": "Mercury - Acts 1 & 2",
      "duration": "2:45",
      "thumbnail": "https://i.ytimg.com/vi/lDdmYccv1fo/hqdefault.jpg",
      "views": "284M",
      "year": "2022"
    }
  ],
  "total_results": 1,
  "query": "Imagine Dragons Bones",
  "search_time": 0.85
}
```

## 📥 2. Audio Download

### Basic Download

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "lDdmYccv1fo",
    "format": "mp3",
    "quality": "high"
  }'
```

### Download with Custom Settings

```bash
curl -X POST "http://localhost:8000/download" \
  -H "Content-Type: application/json" \
  -d '{
    "video_id": "lDdmYccv1fo",
    "format": "wav",
    "quality": "high",
    "max_duration": 300
  }'
```

### Python Example

```python
import requests

download_data = {
    "video_id": "lDdmYccv1fo",
    "format": "mp3",
    "quality": "high"
}

response = requests.post(
    "http://localhost:8000/download",
    json=download_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Downloaded: {result['filepath']}")
    print(f"Duration: {result['duration']}s")
    print(f"Size: {result['file_size']} bytes")
```

### Response Format

```json
{
  "success": true,
  "filepath": "temp/converted_20250531_120000_abc123.mp3",
  "title": "Bones",
  "artist": "Imagine Dragons",
  "duration": 165.5,
  "format": "mp3",
  "quality": "high",
  "file_size": 5242880,
  "bitrate": "320 kbps",
  "sample_rate": 44100,
  "channels": 2,
  "download_time": 12.3
}
```

## 🎤 3. Audio Transcription

### Local Whisper Transcription

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=local" \
  -F "target_lang=pt"
```

### Transcription with Translation (AI Models)

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=local" \
  -F "target_lang=pt" \
  -F "translation_engine=ai_model"
```

### Transcription with Translation (Google Translate)

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=local" \
  -F "target_lang=pt" \
  -F "translation_engine=deep_translator"
```

### OpenAI API Transcription (Fallback)

```bash
curl -X POST "http://localhost:8000/transcribe" \
  -F "file=@audio.mp3" \
  -F "engine=openai" \
  -F "target_lang=en"
```

### Get Available Translation Engines

```bash
curl -X GET "http://localhost:8000/transcribe/translation-engines"
```

### Python Example with Translation

```python
import requests

# Upload and transcribe audio file with translation
with open("audio.mp3", "rb") as audio_file:
    files = {"file": audio_file}
    data = {
        "engine": "local",
        "target_lang": "pt",  # Traduzir para português
        "translation_engine": "deep_translator"  # Usar Google Translate
    }

    response = requests.post(
        "http://localhost:8000/transcribe",
        files=files,
        data=data
    )

if response.status_code == 200:
    result = response.json()
    print(f"Language detected: {result['language']}")
    print(f"Full text: {result['full_text']}")

    # Print segments with translations
    for i, segment in enumerate(result['segments']):
        start = segment['start']
        end = segment['end']
        text = segment['text']
        translation = segment.get('translation', 'N/A')
        print(f"{i+1:2d}. [{start:6.1f}s - {end:6.1f}s]")
        print(f"    Original: {text}")
        print(f"    Tradução: {translation}")
```

### Response Format with Translation

```json
{
  "success": true,
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 3.5,
      "text": "I wake up to the sounds",
      "translation": "Eu acordo com os sons"
    },
    {
      "start": 3.5,
      "end": 7.2,
      "text": "of the silence that allows",
      "translation": "do silêncio que permite"
    },
    {
      "start": 7.2,
      "end": 11.8,
      "text": "for my mind to run around",
      "translation": "que minha mente vagueie"
    }
  ],
  "full_text": "I wake up to the sounds of the silence that allows for my mind to run around..."
}
```

### Translation Engine Comparison

| Engine            | Speed  | Quality | Languages | Internet Required | Description                 |
| ----------------- | ------ | ------- | --------- | ----------------- | --------------------------- |
| `ai_model`        | Lento  | Alta    | ~15       | Não               | Modelos Helsinki-NLP locais |
| `deep_translator` | Rápido | Alta    | 100+      | Sim               | Google Translate via API    |

### Supported Languages

Common language codes supported by both engines:

- `pt` - Português
- `en` - English
- `es` - Español
- `fr` - Français
- `de` - Deutsch
- `it` - Italiano
- `ru` - Русский
- `ja` - 日本語
- `ko` - 한국어
- `zh` - 中文
- `ar` - العربية
- `hi` - हिन्दी

For full list, check `/transcribe/translation-engines` endpoint.

## ✂️ 4. Audio Cutting & Editing

### Basic Audio Cut

```bash
curl -X POST "http://localhost:8000/cut" \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "temp/converted_20250531_120000_abc123.mp3",
    "start": 30.5,
    "end": 60.0
  }'
```

### Advanced Cut with Fade Effects

```bash
curl -X POST "http://localhost:8000/cut" \
  -H "Content-Type: application/json" \
  -d '{
    "filepath": "temp/audio.mp3",
    "start": 45.2,
    "end": 75.8,
    "fade_in": 0.5,
    "fade_out": 1.0,
    "output_format": "mp3"
  }'
```

### Python Example

```python
import requests

cut_data = {
    "filepath": "temp/audio.mp3",
    "start": 30.0,
    "end": 60.0,
    "fade_in": 0.3,
    "fade_out": 0.3
}

response = requests.post(
    "http://localhost:8000/cut",
    json=cut_data
)

if response.status_code == 200:
    result = response.json()
    print(f"Cut completed: {result['output_filepath']}")
    print(f"Original duration: {result['original_duration']}s")
    print(f"Cut duration: {result['cut_duration']}s")
```

### Response Format

```json
{
  "success": true,
  "output_filepath": "temp/cut_20250531_120000_abc123.mp3",
  "original_filepath": "temp/converted_20250531_120000_abc123.mp3",
  "start": 30.5,
  "end": 60.0,
  "original_duration": 165.5,
  "cut_duration": 29.5,
  "fade_in": 0.5,
  "fade_out": 0.5,
  "format": "mp3",
  "processing_time": 2.1
}
```

## 💚 5. Health Check & Status

### System Health

```bash
curl "http://localhost:8000/health"
```

### Response Format

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "youtube_music": "available",
    "whisper_local": "available",
    "openai_api": "not_configured",
    "ffmpeg": "available",
    "transcription_engines": ["local"]
  },
  "system": {
    "platform": "Windows",
    "python_version": "3.12.3",
    "cpu_usage": 15.2,
    "memory_usage": 67.8,
    "disk_usage": 45.1
  },
  "configuration": {
    "debug": true,
    "temp_dir": "temp",
    "max_file_size_mb": 100,
    "rate_limit": "10/60s"
  }
}
```

## 🔄 6. Complete Workflows

### Workflow 1: Find and Download Music

```python
import requests
import time

# 1. Search for music
search_response = requests.get(
    "http://localhost:8000/search",
    params={"query": "Imagine Dragons Bones", "limit": 1}
)
tracks = search_response.json()['results']
video_id = tracks[0]['video_id']

# 2. Download audio
download_response = requests.post(
    "http://localhost:8000/download",
    json={"video_id": video_id, "format": "mp3"}
)
audio_file = download_response.json()['filepath']

print(f"Downloaded: {audio_file}")
```

### Workflow 2: Complete Short Video Creation

```python
import requests

class ShortTuneClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def search_music(self, query, limit=5):
        """Search for music tracks"""
        response = requests.get(
            f"{self.base_url}/search",
            params={"query": query, "limit": limit}
        )
        return response.json()

    def download_audio(self, video_id, format="mp3"):
        """Download audio from YouTube"""
        response = requests.post(
            f"{self.base_url}/download",
            json={"video_id": video_id, "format": format}
        )
        return response.json()

    def transcribe_audio(self, filepath, provider="local", language="en"):
        """Transcribe audio with timestamps"""
        with open(filepath, "rb") as f:
            files = {"file": f}
            data = {"provider": provider, "language": language}
            response = requests.post(
                f"{self.base_url}/transcribe",
                files=files,
                data=data
            )
        return response.json()

    def cut_audio(self, filepath, start, end, fade_in=0.5, fade_out=0.5):
        """Cut audio segment"""
        response = requests.post(
            f"{self.base_url}/cut",
            json={
                "filepath": filepath,
                "start": start,
                "end": end,
                "fade_in": fade_in,
                "fade_out": fade_out
            }
        )
        return response.json()

# Usage example
client = ShortTuneClient()

# 1. Search for music
results = client.search_music("Imagine Dragons Bones")
selected_track = results['results'][0]
print(f"Selected: {selected_track['title']} by {selected_track['artist']}")

# 2. Download the track
download_result = client.download_audio(selected_track['video_id'])
audio_file = download_result['filepath']
print(f"Downloaded to: {audio_file}")

# 3. Transcribe to get lyrics with timestamps
transcription = client.transcribe_audio(audio_file)
segments = transcription['segments']
print(f"Transcribed {len(segments)} segments")

# 4. Find a good segment for short video (30-60 seconds)
best_segment = None
for i, segment in enumerate(segments):
    start_time = segment['start']

    # Look for 30-second window
    end_time = start_time + 30
    if end_time <= transcription['stats']['audio_duration']:
        # Check if this segment has good text
        segment_text = ' '.join([s['text'] for s in segments[i:i+5]])
        if len(segment_text) > 50:  # Good amount of text
            best_segment = (start_time, end_time, segment_text)
            break

if best_segment:
    start, end, text = best_segment
    print(f"Best segment: {start:.1f}s - {end:.1f}s")
    print(f"Text: {text[:100]}...")

    # 5. Cut the audio
    cut_result = client.cut_audio(audio_file, start, end)
    final_audio = cut_result['output_filepath']
    print(f"Cut audio saved to: {final_audio}")
    print(f"Final duration: {cut_result['cut_duration']}s")
```

### Workflow 3: Batch Processing

```python
import requests
import json
from concurrent.futures import ThreadPoolExecutor
import time

def process_track(track_info):
    """Process a single track"""
    video_id = track_info['video_id']
    title = track_info['title']

    try:
        # Download
        download_response = requests.post(
            "http://localhost:8000/download",
            json={"video_id": video_id, "format": "mp3"},
            timeout=120
        )

        if download_response.status_code != 200:
            return {"error": f"Download failed for {title}"}

        audio_file = download_response.json()['filepath']

        # Transcribe
        with open(audio_file, "rb") as f:
            files = {"file": f}
            data = {"provider": "local", "language": "en"}
            transcribe_response = requests.post(
                "http://localhost:8000/transcribe",
                files=files,
                data=data,
                timeout=300
            )

        if transcribe_response.status_code != 200:
            return {"error": f"Transcription failed for {title}"}

        transcription = transcribe_response.json()

        return {
            "title": title,
            "video_id": video_id,
            "audio_file": audio_file,
            "duration": transcription['stats']['audio_duration'],
            "segments": len(transcription['segments']),
            "text_preview": transcription['text'][:100] + "..."
        }

    except Exception as e:
        return {"error": f"Processing failed for {title}: {str(e)}"}

# Search for multiple tracks
search_query = "Imagine Dragons"
search_response = requests.get(
    "http://localhost:8000/search",
    params={"query": search_query, "limit": 5}
)
tracks = search_response.json()['results']

# Process tracks in parallel
print(f"Processing {len(tracks)} tracks...")
start_time = time.time()

with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(process_track, tracks))

end_time = time.time()
print(f"Batch processing completed in {end_time - start_time:.1f}s")

# Print results
for result in results:
    if 'error' in result:
        print(f"❌ {result['error']}")
    else:
        print(f"✅ {result['title']}: {result['duration']:.1f}s, {result['segments']} segments")
```

## 🐛 7. Error Handling & Troubleshooting

### Common Error Responses

#### Rate Limit Exceeded

```json
{
  "detail": "Rate limit exceeded: 10 per 60 seconds"
}
```

#### File Not Found

```json
{
  "detail": {
    "error": "file_not_found",
    "message": "Audio file not found",
    "filepath": "temp/nonexistent.mp3"
  }
}
```

#### Invalid Video ID

```json
{
  "detail": {
    "error": "download_failed",
    "message": "Failed to download audio",
    "details": "Video not available or private"
  }
}
```

#### Transcription Failed

```json
{
  "detail": {
    "error": "transcription_failed",
    "message": "Failed to transcribe audio",
    "details": "Audio format not supported"
  }
}
```

### Error Handling in Python

```python
import requests
from requests.exceptions import RequestException, Timeout

def safe_api_call(url, method="GET", **kwargs):
    """Make a safe API call with error handling"""
    try:
        if method.upper() == "GET":
            response = requests.get(url, timeout=30, **kwargs)
        elif method.upper() == "POST":
            response = requests.post(url, timeout=120, **kwargs)

        # Check for HTTP errors
        response.raise_for_status()

        return response.json()

    except Timeout:
        return {"error": "Request timed out"}
    except requests.exceptions.ConnectionError:
        return {"error": "Connection failed - is the server running?"}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {"error": "Rate limit exceeded - please wait"}
        elif e.response.status_code == 422:
            return {"error": "Invalid request data", "details": e.response.json()}
        else:
            return {"error": f"HTTP {e.response.status_code}: {e.response.text}"}
    except RequestException as e:
        return {"error": f"Request failed: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}

# Usage
result = safe_api_call(
    "http://localhost:8000/search",
    params={"query": "test"}
)

if "error" in result:
    print(f"Error: {result['error']}")
else:
    print(f"Success: {len(result['results'])} results")
```

## 📊 8. Performance Tips

### Optimization Guidelines

1. **Use appropriate timeout values**:

   - Search: 10-30 seconds
   - Download: 60-120 seconds
   - Transcription: 120-600 seconds

2. **Batch processing**:

   - Use ThreadPoolExecutor for parallel requests
   - Limit concurrent requests to 3-5
   - Implement retry logic for failed requests

3. **File management**:

   - Clean up temporary files after processing
   - Monitor disk space usage
   - Use the `/health` endpoint to check system resources

4. **Rate limiting**:
   - Respect the 10 requests/minute limit
   - Implement exponential backoff for retries
   - Use the rate limit headers in responses

### Monitoring Performance

```python
import requests
import time

def monitor_api_performance():
    """Monitor API response times"""
    endpoints = [
        "/health",
        "/search?query=test",
        "/download/formats",
        "/transcribe/engines"
    ]

    for endpoint in endpoints:
        start_time = time.time()
        response = requests.get(f"http://localhost:8000{endpoint}")
        end_time = time.time()

        print(f"{endpoint}: {response.status_code} ({end_time - start_time:.2f}s)")

monitor_api_performance()
```

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Health Dashboard**: http://localhost:8000/health
- **GitHub Repository**: [Add your repository URL]
- **Issues & Support**: [Add your issues URL]

**Happy coding! 🎵**
