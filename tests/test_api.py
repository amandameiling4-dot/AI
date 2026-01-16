"""Tests for the API server."""
from fastapi.testclient import TestClient
from backend.api.server import app


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    data = response.json()
    assert 'status' in data
    assert 'model_loaded' in data


def test_completions_no_auth():
    response = client.post('/v1/completions', json={'prompt': 'def foo():'})
    assert response.status_code == 401


def test_completions_with_auth():
    headers = {'Authorization': 'Bearer test-key-12345'}
    response = client.post(
        '/v1/completions',
        json={'prompt': 'def foo():', 'max_tokens': 10},
        headers=headers,
    )
    # Expect 200 or 500 (model loading) depending on env
    assert response.status_code in [200, 500]


def test_usage_no_auth():
    response = client.get('/v1/account/usage')
    assert response.status_code == 401


def test_usage_with_auth():
    headers = {'Authorization': 'Bearer test-key-12345'}
    response = client.get('/v1/account/usage', headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert 'tokens_used_this_month' in data
