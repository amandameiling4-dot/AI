import pytest
from scripts.data.scrub_secrets import redact_text


def test_redact_email_and_token():
    text = 'Contact me at alice@example.com and token=ABCDEF1234567890'
    redacted, matches = redact_text(text)
    assert 'alice@' not in redacted
    assert 'ABCDEF1234567890' not in redacted
    assert any(m[0] == 'email' for m in matches)
    assert any('token' in m[1].lower() or len(m[1]) >= 10 for m in matches)
