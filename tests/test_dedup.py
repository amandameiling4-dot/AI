import json
from pathlib import Path
from scripts.data.deduplicate import deduplicate_manifest


def test_deduplicate_basic(tmp_path):
    input_file = tmp_path / 'in.jsonl'
    output_file = tmp_path / 'out.jsonl'
    dup_file = tmp_path / 'dups.log'

    samples = [
        {'id': 'a', 'content': 'def add(a, b):\n    return a + b\n'},
        {'id': 'b', 'content': 'def add(a, b):\n    return a + b\n'},  # duplicate
        {'id': 'c', 'content': 'def sub(a, b):\n    return a - b\n'},
    ]
    with input_file.open('w') as fh:
        for s in samples:
            fh.write(json.dumps(s) + '\n')

    res = deduplicate_manifest(input_file, output_file, dup_file)
    assert res['total'] == 3
    assert res['duplicates'] == 1

    out = [json.loads(l) for l in output_file.read_text().splitlines()]
    ids = [o['id'] for o in out]
    assert ids == ['a', 'c']
    dups = [json.loads(l) for l in dup_file.read_text().splitlines()]
    assert dups[0]['duplicate_of'] == 'a'
