"""
Load testing script for ShortTune API using Locust
Run with: locust -f load_test.py --host=http://localhost:8000
"""

from locust import HttpUser, task, between
import json

class ShortTuneUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Called when user starts"""
        # Test health endpoint first
        response = self.client.get("/health")
        if response.status_code != 200:
            print("API not healthy!")
    
    @task(3)
    def search_music(self):
        """Test music search endpoint"""
        response = self.client.get("/search?query=imagine dragons&limit=5")
        if response.status_code == 200:
            data = response.json()
            if data.get("results"):
                # Store first result for download test
                self.video_id = data["results"][0]["videoId"]
    
    @task(1)
    def download_audio(self):
        """Test audio download endpoint"""
        if hasattr(self, 'video_id'):
            payload = {
                "video_id": self.video_id,
                "output_format": "mp3",
                "quality": "128k"
            }
            with self.client.post(
                "/download", 
                json=payload,
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    response.success()
                elif response.status_code == 429:  # Rate limit
                    response.success()  # Expected behavior
                else:
                    response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def health_check(self):
        """Test health endpoint"""
        self.client.get("/health")

if __name__ == "__main__":
    # Direct test run
    import requests
    import time
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing ShortTune API Performance...")
    
    # Health check
    response = requests.get(f"{base_url}/health")
    print(f"Health: {response.status_code}")
    
    # Search test
    start_time = time.time()
    response = requests.get(f"{base_url}/search?query=test&limit=3")
    search_time = time.time() - start_time
    print(f"Search: {response.status_code} ({search_time:.2f}s)")
    
    print("✅ Basic performance test completed")
