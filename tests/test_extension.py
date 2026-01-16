"""Tests for the VS Code extension."""
import json


def test_package_json_valid():
    """Verify extension manifest is valid."""
    with open('extensions/vscode/package.json', 'r') as f:
        manifest = json.load(f)
    
    assert 'name' in manifest
    assert 'version' in manifest
    assert 'activationEvents' in manifest
    assert 'contributes' in manifest
    assert len(manifest['activationEvents']) > 0
    assert manifest['activationEvents'][0].startswith('onLanguage')


def test_extension_structure():
    """Check main extension source exists."""
    from pathlib import Path
    assert Path('extensions/vscode/src/extension.ts').exists()
    assert Path('extensions/vscode/tsconfig.json').exists()
