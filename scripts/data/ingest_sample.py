"""Sample ingester: pulls small datasets for development/testing.
This script doesn't download large corpora; it demonstrates the workflow and metadata capture.
"""
import json
from pathlib import Path

OUT = Path('data/sample')
OUT.mkdir(parents=True, exist_ok=True)

SAMPLE = [
    {
        'id': 'sample_1',
        'source': 'local_example',
        'path': 'examples/foo.py',
        'language': 'python',
        'license': 'MIT',
        'content': 'def add(a, b):\n    return a + b\n',
    },
    {
        'id': 'sample_2',
        'source': 'local_example',
        'path': 'examples/bar.js',
        'language': 'javascript',
        'license': 'MIT',
        'content': 'function add(a, b) { return a + b }\n',
    }
]

with open(OUT / 'manifest.jsonl', 'w') as fh:
    for s in SAMPLE:
        fh.write(json.dumps(s) + '\n')

print('Wrote', OUT / 'manifest.jsonl')
