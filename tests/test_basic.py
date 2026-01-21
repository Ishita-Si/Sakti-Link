"""
Sample tests for Sakti-Link Edge Server
"""

import pytest
from httpx import AsyncClient
from edge_server.main import app
import base64


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Sakti-Link Edge Server"


@pytest.mark.asyncio
async def test_supported_languages():
    """Test supported languages endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/voice/languages")
        assert response.status_code == 200
        data = response.json()
        assert "languages" in data
        assert len(data["languages"]) > 0
        
        # Check Hindi is supported
        hindi = next((lang for lang in data["languages"] if lang["code"] == "hi"), None)
        assert hindi is not None


@pytest.mark.asyncio
async def test_system_status():
    """Test system status endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/system/status")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        assert "supported_languages" in data


# Note: More comprehensive tests would require:
# 1. Test database setup
# 2. Mock AI models
# 3. Sample audio files
# 4. User session management

# Example test structure for voice processing (requires setup):
"""
@pytest.mark.asyncio
async def test_voice_processing():
    # Create sample audio
    sample_audio = create_sample_audio()
    audio_base64 = base64.b64encode(sample_audio).decode()
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/v1/voice/process",
            json={
                "audio_base64": audio_base64,
                "language": "hi",
                "device_fingerprint": "test_device_123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["success"] == True
        assert "transcript" in data
        assert "intent" in data
        assert "response_text" in data
"""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
