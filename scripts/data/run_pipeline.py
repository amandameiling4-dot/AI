"""Orchestrator for ingest -> scrub -> dedupe pipeline on sample dataset.
Writes scrubbed manifest and deduped manifest and prints a summary.
"""
import sys
import json
from pathlib import Path
# Ensure project root is on sys.path so 'scripts' package imports work when running directly
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.data.scrub_secrets import redact_text
from scripts.data.deduplicate import deduplicate_manifest

DATA_DIR = Path('data/sample')
INPUT = DATA_DIR / 'manifest.jsonl'
SCRUBBED = DATA_DIR / 'manifest.scrubbed.jsonl'
SCRUB_LOG = DATA_DIR / 'scrub_log.jsonl'
DEDUPED = DATA_DIR / 'manifest.dedup.jsonl'
DUPS_LOG = DATA_DIR / 'duplicates.log'


def run():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not INPUT.exists():
        raise SystemExit(f'Input manifest not found: {INPUT}')

    scrub_count = 0
    match_count = 0

    with INPUT.open('r', encoding='utf-8') as fh_in, SCRUBBED.open('w', encoding='utf-8') as fh_out, SCRUB_LOG.open('w', encoding='utf-8') as fh_log:
        for line in fh_in:
            obj = json.loads(line)
            content = obj.get('content', '')
            redacted, matches = redact_text(content)
            obj['content'] = redacted
            fh_out.write(json.dumps(obj) + '\n')
            scrub_count += 1
            if matches:
                match_count += len(matches)
                fh_log.write(json.dumps({'id': obj.get('id'), 'matches': matches}) + '\n')

    print(f'Scrubbed {scrub_count} samples, total matches found: {match_count}')

    # Run dedupe on scrubbed manifest
    res = deduplicate_manifest(SCRUBBED, DEDUPED, DUPS_LOG)
    print('Deduplication result:', res)

    # Print sample outputs
    print('\nSample scrub log entries:')
    if SCRUB_LOG.exists():
        with SCRUB_LOG.open('r') as fh:
            for i, l in enumerate(fh):
                if i >= 5:
                    break
                print(l.strip())
    else:
        print('No scrub log (no matches)')

    print('\nDeduped manifest preview:')
    with DEDUPED.open('r') as fh:
        for i, l in enumerate(fh):
            if i >= 5:
                break
            print(l.strip())


if __name__ == '__main__':
    run()
