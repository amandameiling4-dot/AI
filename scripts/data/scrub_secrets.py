"""Secrets & PII scanner and redaction utility.
This module uses regexes plus an optional ML-based detector (spaCy) for better PII coverage.
"""
import re
from typing import Tuple, List

# Optional ML-based PII detector
try:
    from scripts.data.pii_detector import detect_pii
except Exception:
    # If optional dependency not available, provide a noop fallback
    def detect_pii(text: str) -> List[Tuple[str, str]]:
        return []

# Example regexes (expand and refine for production)
SECRET_PATTERNS = {
    'aws_key': re.compile(r'AKIA[0-9A-Z]{16}'),
    'ssh_private_key': re.compile(r'-----BEGIN (?:RSA )?PRIVATE KEY-----'),
    'generic_token': re.compile(r"""(?i)(?:token|secret|apikey)["':\s]*[A-Za-z0-9_\-]{16,}"""),
    'git_token': re.compile(r'ghp_[A-Za-z0-9]{36}'),
    'jwt': re.compile(r"[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+\.[A-Za-z0-9-_]+"),
    'credit_card': re.compile(r"\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13})\b"),
}
PII_PATTERNS = {
    'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    # Match common phone formats requiring separators (avoid matching long numeric tokens):
    # e.g. +1 555-123-4567 or (555) 123-4567
    'phone': re.compile(r"(\+?\d{1,3}[\s\-])?(?:\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4})" )
}

# Heuristic filters to reduce false positives
MIN_SECRET_LENGTH = 8


def find_matches(text: str) -> List[Tuple[str, re.Match]]:
    matches = []
    for name, pat in SECRET_PATTERNS.items():
        for m in pat.finditer(text):
            # heuristic: ignore short matches
            if len(m.group(0)) < MIN_SECRET_LENGTH:
                continue
            matches.append((name, m))
    for name, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            matches.append((name, m))
    return matches


def _mask_snippet(snippet: str) -> str:
    # Keep short prefix & suffix, mask middle; preserve length of mask proportionally
    if len(snippet) <= 4:
        return '****'
    prefix = snippet[:2]
    suffix = snippet[-2:]
    mask_len = max(4, len(snippet) // 2)
    return prefix + ('*' * mask_len) + suffix


def redact_text(text: str, max_context: int = 20) -> Tuple[str, List[Tuple[str, str]]]:
    """Redact secrets/PII found in text. Returns (redacted_text, list of (type, snippet))."""
    redacted = text
    found: List[Tuple[str, str]] = []

    # Regex-based detection
    for name, pat in {**SECRET_PATTERNS, **PII_PATTERNS}.items():
        for m in pat.finditer(text):
            snippet = m.group(0)
            # heuristic: avoid overly short matches
            if len(snippet) < MIN_SECRET_LENGTH and name in SECRET_PATTERNS:
                continue
            found.append((name, snippet))
            masked = _mask_snippet(snippet)
            redacted = redacted.replace(snippet, masked)

    # ML-based PII detection (optional)
    try:
        ml_hits = detect_pii(text)
        for typ, snippet in ml_hits:
            # avoid double-reporting or false positives inside larger secret tokens
            if any(snippet == s or snippet in s or s in snippet for _, s in found):
                continue
            found.append((typ, snippet))
            redacted = redacted.replace(snippet, _mask_snippet(snippet))
    except Exception:
        # If detector fails, ignore and continue
        pass

    return redacted, found


if __name__ == '__main__':
    example = "Here is a token: my_secret_token=ABCDEF1234567890 and an email: alice@example.com"
    redacted, matches = redact_text(example)
    print('Redacted:', redacted)
    print('Matches:', matches)



def find_matches(text: str) -> List[Tuple[str, re.Match]]:
    matches = []
    for name, pat in SECRET_PATTERNS.items():
        for m in pat.finditer(text):
            matches.append((name, m))
    for name, pat in PII_PATTERNS.items():
        for m in pat.finditer(text):
            matches.append((name, m))
    return matches


def redact_text(text: str, max_context: int = 20) -> Tuple[str, List[Tuple[str, str]]]:
    """Redact secrets/PII found in text. Returns (redacted_text, list of (type, snippet))."""
    redacted = text
    found = []
    for name, pat in {**SECRET_PATTERNS, **PII_PATTERNS}.items():
        for m in pat.finditer(text):
            snippet = m.group(0)
            found.append((name, snippet))
            # Simple redaction: keep first and last char and mask the middle (if length > 4)
            if len(snippet) > 6:
                masked = snippet[0:2] + '****' + snippet[-2:]
            else:
                masked = '****'
            redacted = redacted.replace(snippet, masked)
    return redacted, found


if __name__ == '__main__':
    example = "Here is a token: my_secret_token=ABCDEF1234567890 and an email: alice@example.com"
    redacted, matches = redact_text(example)
    print('Redacted:', redacted)
    print('Matches:', matches)
