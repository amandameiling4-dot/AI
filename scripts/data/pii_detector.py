"""Optional ML-backed PII detector (spaCy) with a lightweight regex fallback.

Functions:
- detect_pii(text) -> List[Tuple[type, snippet]]

Behavior:
- If spaCy is installed & model available, uses NER to detect PERSON/ORG/GPE etc.
- Otherwise, falls back to simple regex-based detection for emails/phones/ssn.
"""
from typing import List, Tuple

# Keep imports local to avoid heavy requirements when not needed
try:
    import spacy  # type: ignore
    _HAS_SPACY = True
except Exception:
    _HAS_SPACY = False

import re

# Lightweight regex fallbacks
PII_FALLBACK = {
    'email': re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'),
    'ssn': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
    # Accept common phone formats requiring separators (avoid matching long numeric tokens inside tokens)
    'phone': re.compile(r"(\+?\d{1,3}[\s\-])?(?:\(?\d{3}\)?[\s\-]\d{3}[\s\-]\d{4})"),
}


def detect_pii(text: str) -> List[Tuple[str, str]]:
    """Return list of detected PII items as (type, snippet)."""
    results: List[Tuple[str, str]] = []

    if _HAS_SPACY:
        try:
            nlp = spacy.load('en_core_web_sm')
        except Exception:
            # Model not available; fall back to regex
            for name, pat in PII_FALLBACK.items():
                for m in pat.finditer(text):
                    results.append((name, m.group(0)))
            return results

        doc = nlp(text)
        for ent in doc.ents:
            if ent.label_ in {'PERSON', 'ORG', 'GPE', 'LOC'}:
                results.append((ent.label_.lower(), ent.text))
        # Also capture emails/phones by regex
        for name, pat in PII_FALLBACK.items():
            for m in pat.finditer(text):
                results.append((name, m.group(0)))
        return results

    # Default fallback
    for name, pat in PII_FALLBACK.items():
        for m in pat.finditer(text):
            results.append((name, m.group(0)))
    return results
