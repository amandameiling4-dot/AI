"""Python SDK for the Code AI API."""
from typing import Optional
import httpx


class CodeAIClient:
    """Client for Code AI API."""

    def __init__(self, api_key: str, base_url: str = 'http://localhost:8000'):
        self.api_key = api_key
        self.base_url = base_url
        self.client = httpx.Client(headers={'Authorization': f'Bearer {api_key}'})

    def complete(self, prompt: str, max_tokens: int = 100, temperature: float = 0.7) -> dict:
        """Request code completion."""
        response = self.client.post(
            f'{self.base_url}/v1/completions',
            json={'prompt': prompt, 'max_tokens': max_tokens, 'temperature': temperature},
        )
        response.raise_for_status()
        return response.json()

    def get_usage(self) -> dict:
        """Get API usage stats."""
        response = self.client.get(f'{self.base_url}/v1/account/usage')
        response.raise_for_status()
        return response.json()

    def health(self) -> dict:
        """Check API health."""
        response = self.client.get(f'{self.base_url}/health')
        response.raise_for_status()
        return response.json()

    def close(self):
        """Close the client."""
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# Example usage
if __name__ == '__main__':
    with CodeAIClient(api_key='test-key-12345') as client:
        try:
            result = client.health()
            print('Health:', result)

            completion = client.complete(prompt='def add(a, b):', max_tokens=50)
            print('Completion:', completion)

            usage = client.get_usage()
            print('Usage:', usage)
        except Exception as e:
            print(f'Error: {e}')
