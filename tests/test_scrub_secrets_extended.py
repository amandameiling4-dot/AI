import pytest
from scripts.data.scrub_secrets import redact_text


def test_redact_various_secrets():
    text = ('email: alice@example.com\n'
            'aws: AKIAEXAMPLEKEY123456\n'
            'jwt: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.ey...\n'
            'cc: 4111111111111111')
    redacted, matches = redact_text(text)
    # Ensure sensitive strings are masked
    assert 'alice@example.com' not in redacted
    assert 'AKIAEXAMPLEKEY123456' not in redacted
    assert '4111111111111111' not in redacted
    # Ensure matches reported
    names = [n for n, _ in matches]
    assert 'email' in names
    assert 'aws_key' in names
    assert 'credit_card' in names
