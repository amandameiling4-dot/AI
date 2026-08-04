from fastapi.testclient import TestClient
from backend.billing.routes import app

client = TestClient(app)


def test_subscribe_returns_checkout_and_receipt():
    response = client.post(
        '/billing/subscribe',
        json={'price_id': 'price_123', 'customer_email': 'user@example.com'},
    )
    assert response.status_code == 200
    data = response.json()
    assert 'checkout_url' in data
    assert 'session_id' in data
    assert data['receipt']['status'] == 'pending'


def test_payment_status_records_receipt():
    response = client.post(
        '/billing/payment-status',
        json={'session_id': 'sess_123', 'payment_status': 'paid', 'receipt_id': 'rcpt_123'},
    )
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'paid'
    assert data['receipt']['receipt_id'] == 'rcpt_123'
