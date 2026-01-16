from scripts.data.scrub_secrets import redact_text


def test_token_not_flagged_as_phone():
    text = 'Here is token ghp_123456789012345678901234567890123456 and phone +1 555-123-4567'
    redacted, matches = redact_text(text)
    types = [t for t, _ in matches]
    assert 'git_token' in types or 'generic_token' in types
    assert 'phone' in types
    # Ensure no numeric-only false-positive phone matches
    for t, s in matches:
        if t == 'phone':
            assert '+' in s or '-' in s or ' ' in s or '(' in s
