"""Integration test: API server with SDK."""
from sdk.python.client import CodeAIClient
from backend.api.server import app
from fastapi.testclient import TestClient


def test_sdk_integration():
    """Test SDK against local test client."""
    # Use TestClient for in-process testing
    import httpx
    
    # Mock httpx to use TestClient
    original_client = httpx.Client
    
    class MockClient(original_client):
        def __init__(self, *args, **kwargs):
            self.test_client = TestClient(app)
            kwargs.pop('headers', None)  # Remove headers from parent init
            super().__init__(*args, **kwargs)
        
        def post(self, url, **kwargs):
            path = url.replace('http://localhost:8000', '')
            return self.test_client.post(path, **kwargs)
        
        def get(self, url, **kwargs):
            path = url.replace('http://localhost:8000', '')
            return self.test_client.get(path, **kwargs)
    
    # Create client with mocked httpx
    client = CodeAIClient(api_key='test-key')
    
    # Replace the internal client
    client.client = TestClient(app)
    client.client.headers = {'Authorization': 'Bearer test-key'}
    
    # Test health
    response = client.health()
    assert response['status'] == 'ok'
