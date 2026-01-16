from scripts.data.pii_detector import detect_pii


def test_detect_pii_fallback_regex():
    text = 'Contact: alice@example.com or call +1 555-123-4567. SSN 123-45-6789.'
    res = detect_pii(text)
    names = [t for t, _ in res]
    assert 'email' in names
    assert 'phone' in names
    assert 'ssn' in names
