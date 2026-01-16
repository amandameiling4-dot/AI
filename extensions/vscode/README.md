# VS Code Extension for Code AI

IntelliSense-powered code completions for Python, JavaScript, and TypeScript.

## Setup

```bash
cd extensions/vscode
npm install
npm run compile
```

## Development

```bash
npm run watch  # Rebuild on changes
# Then open in VS Code and press F5 to launch debugger
```

## Configuration

In VS Code settings (`settings.json`):

```json
{
  "codeAI.apiKey": "your-api-key",
  "codeAI.apiEndpoint": "http://localhost:8000",
  "codeAI.enableCompletion": true,
  "codeAI.maxTokens": 100
}
```

## Usage

1. Set API key: Run `Code AI: Set API Key` command
2. Start getting completions as you type
3. Check usage: Run `Code AI: Show Usage` command

## Features

- Inline code completions (Python, JavaScript, TypeScript)
- API key management (stored securely in VS Code secrets)
- Usage tracking and display
- Configurable endpoint and token limits

## Future

- LSP server for richer features (hover, go-to-definition)
- Streaming completions
- Context-aware suggestions with RAG
- Refactor and docstring generation commands
