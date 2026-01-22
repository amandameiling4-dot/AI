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

def redact_text(text, patterns):
    """
    Replace any matches in the text with '[REDACTED]'.
    :param text: The text where matches will be redacted.
    :param patterns: List of regex patterns for matching.
    :return: Redacted text.
    """
    for pattern in patterns:
        text = re.sub(pattern, '[REDACTED]', text)
    return text

# Example usage
if __name__ == '__main__':
    sample_text = "This is a secret message with sensitive information."
    patterns = [r'secret', r'sensitive']
    matches = find_matches(sample_text, patterns)
    print(f'Matches found: {matches}')
    redacted = redact_text(sample_text, patterns)
    print(f'Redacted text: {redacted}')