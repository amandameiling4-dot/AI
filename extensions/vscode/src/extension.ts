import * as vscode from 'vscode';
import * as fetch from 'node-fetch';

let apiKey: string;
let apiEndpoint: string;

export function activate(context: vscode.ExtensionContext) {
    console.log('Code AI extension activated');

    // Register commands
    const setApiKeyCmd = vscode.commands.registerCommand('codeAI.setApiKey', async () => {
        const key = await vscode.window.showInputBox({
            prompt: 'Enter your Code AI API key',
            password: true,
            ignoreFocusOut: true,
        });
        if (key) {
            await context.secrets.store('codeAI.apiKey', key);
            vscode.window.showInformationMessage('API key saved');
        }
    });

    const getUsageCmd = vscode.commands.registerCommand('codeAI.getUsage', async () => {
        try {
            const apiKey = await context.secrets.get('codeAI.apiKey');
            const endpoint = vscode.workspace.getConfiguration('codeAI').get<string>('apiEndpoint', 'http://localhost:8000');
            
            const response = await fetch(`${endpoint}/v1/account/usage`, {
                headers: { 'Authorization': `Bearer ${apiKey}` },
            });
            const usage = await response.json();
            vscode.window.showInformationMessage(
                `Tokens: ${usage.tokens_used_this_month}/${usage.tokens_limit}`
            );
        } catch (e) {
            vscode.window.showErrorMessage(`Error fetching usage: ${e}`);
        }
    });

    context.subscriptions.push(setApiKeyCmd, getUsageCmd);

    // Register completion provider
    const completionProvider = vscode.languages.registerCompletionItemProvider(
        { scheme: 'file', language: 'python' },
        new CodeAICompletionProvider(context),
        '\n', ' '
    );
    context.subscriptions.push(completionProvider);

    // Load config
    loadConfig(context);
}

function loadConfig(context: vscode.ExtensionContext) {
    const config = vscode.workspace.getConfiguration('codeAI');
    apiEndpoint = config.get<string>('apiEndpoint', 'http://localhost:8000');
}

class CodeAICompletionProvider implements vscode.CompletionItemProvider {
    constructor(private context: vscode.ExtensionContext) {}

    async provideCompletionItems(
        document: vscode.TextDocument,
        position: vscode.Position,
        token: vscode.CancellationToken,
        context: vscode.CompletionContext
    ): Promise<vscode.CompletionItem[]> {
        try {
            const apiKey = await this.context.secrets.get('codeAI.apiKey');
            if (!apiKey) {
                return [];
            }

            // Get current line and create prompt
            const lineText = document.lineAt(position.line).text;
            const prompt = document.getText(new vscode.Range(0, 0, position.line, position.character));

            const config = vscode.workspace.getConfiguration('codeAI');
            const maxTokens = config.get<number>('maxTokens', 100);

            // Call API
            const response = await fetch(`${apiEndpoint}/v1/completions`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${apiKey}`,
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    prompt,
                    max_tokens: maxTokens,
                    temperature: 0.7,
                }),
            });

            if (response.status !== 200) {
                console.error(`API error: ${response.status}`);
                return [];
            }

            const data = await response.json();
            const completion = data.completion || '';

            // Extract the generated part (after the prompt)
            const generated = completion.substring(prompt.length).trim();

            if (generated.length === 0) {
                return [];
            }

            const item = new vscode.CompletionItem(generated, vscode.CompletionItemKind.Snippet);
            item.insertText = generated;
            item.sortText = '00'; // High priority

            return [item];
        } catch (e) {
            console.error(`Completion error: ${e}`);
            return [];
        }
    }
}

export function deactivate() {}
