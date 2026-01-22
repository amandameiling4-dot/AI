import re

def find_matches(text, patterns):
    """
    Find and return a list of matches in the given text.
    :param text: The text to search through.
    :param patterns: List of regex patterns to match.
    :return: List of matches.
    """
    matches = []
    for pattern in patterns:
        matches.extend(re.findall(pattern, text))
    return matches

def redact_text(text, patterns=None):
    """
    Replace any matches in the text with '[REDACTED]' and return matches with types.
    :param text: The text where matches will be redacted.
    :param patterns: Optional list of regex patterns for matching. If None, uses default patterns.
    :return: Tuple of (redacted_text, matches) where matches is a list of (secret_type, matched_value) tuples.
    """
    # Default patterns with secret types
    default_patterns = [
        ('email', r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        ('git_token', r'\b(gh[ps]_[A-Za-z0-9]{36,})\b'),
        ('aws_key', r'\b(AKIA[A-Z0-9]{16})\b'),
        ('jwt', r'\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+'),
        ('credit_card', r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b|\b\d{13,16}\b'),
        ('phone', r'(\+\d{1,3}[\s-]?\d{1,4}[\s-]?\d{1,4}[\s-]?\d{1,4}|\(\d{3}\)[\s-]?\d{3}[\s-]?\d{4}|\d{3}[\s-]\d{3}[\s-]\d{4})'),
        ('generic_token', r'\b[A-Za-z0-9]{16,}\b'),
    ]
    
    # Use provided patterns or defaults
    if patterns is not None:
        # If patterns is a simple list of regex strings, use them without types
        pattern_list = [('pattern', p) for p in patterns]
    else:
        pattern_list = default_patterns
    
    # Find all matches with their types
    matches = []
    for secret_type, pattern in pattern_list:
        found = re.findall(pattern, text)
        for match in found:
            matches.append((secret_type, match))
    
    # Redact text using all patterns
    redacted = text
    for secret_type, pattern in pattern_list:
        redacted = re.sub(pattern, '[REDACTED]', redacted)
    
    return redacted, matches

# Example usage
if __name__ == '__main__':
    sample_text = "This is a secret message with sensitive information."
    patterns = [r'secret', r'sensitive']
    matches = find_matches(sample_text, patterns)
    print(f'Matches found: {matches}')
    redacted, detected = redact_text(sample_text, patterns)
    print(f'Redacted text: {redacted}')
    print(f'Detected secrets: {detected}')