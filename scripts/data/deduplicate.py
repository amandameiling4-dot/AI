"""Deduplicate a manifest.jsonl file of code samples.
Keeps first occurrence and writes out deduped manifest and a duplicates log.
"""
import hashlib
import json
from pathlib import Path
from typing import Dict


def normalize_code(code: str) -> str:
    # Basic normalization: strip trailing/leading whitespace, collapse multiple blank lines
    lines = [l.rstrip() for l in code.splitlines()]
    # Remove consecutive empty lines
    out = []
    prev_empty = False
    for l in lines:
        if l.strip() == '':
            if not prev_empty:
                out.append('')
            prev_empty = True
        else:
            out.append(l)
            prev_empty = False
    return '\n'.join(out).strip() + '\n'


def checksum(content: str) -> str:
    return hashlib.sha256(content.encode('utf-8')).hexdigest()


def deduplicate_manifest(input_path: Path, output_path: Path, dup_log_path: Path) -> Dict[str, int]:
    seen = {}
    total = 0
    duplicates = 0
    with input_path.open('r', encoding='utf-8') as fh_in, output_path.open('w', encoding='utf-8') as fh_out, dup_log_path.open('w', encoding='utf-8') as fh_dup:
        for line in fh_in:
            total += 1
            obj = json.loads(line)
            content = obj.get('content', '')
            norm = normalize_code(content)
            ch = checksum(norm)
            if ch in seen:
                duplicates += 1
                fh_dup.write(json.dumps({'id': obj.get('id'), 'duplicate_of': seen[ch], 'hash': ch}) + '\n')
                continue
            seen[ch] = obj.get('id')
            # Update content to normalized form
            obj['content'] = norm
            fh_out.write(json.dumps(obj) + '\n')
    return {'total': total, 'duplicates': duplicates, 'kept': total - duplicates}


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='data/sample/manifest.jsonl')
    parser.add_argument('--output', default='data/sample/manifest.dedup.jsonl')
    parser.add_argument('--dups', default='data/sample/duplicates.log')
    args = parser.parse_args()

    res = deduplicate_manifest(Path(args.input), Path(args.output), Path(args.dups))
    print('Deduplication result:', res)
