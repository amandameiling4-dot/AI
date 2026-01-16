"""
Example: Using CodeAI with curl and shell scripts

This example demonstrates how to:
1. Query the API directly with curl
2. Parse JSON responses
3. Automate completions in bash
4. Monitor usage via shell
"""

#!/bin/bash

# Configuration
API_KEY="test_key_12345"
API_URL="http://localhost:8000"

echo "=========================================="
echo "CodeAI Shell Script Examples"
echo "=========================================="

# Example 1: Health Check
echo -e "\n=== Example 1: Health Check ==="
curl -s "$API_URL/health" | jq .

# Example 2: Simple Completion
echo -e "\n=== Example 2: Generate Completion ==="
curl -s -X POST "$API_URL/v1/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def hello_world(",
    "max_tokens": 30,
    "temperature": 0.5
  }' | jq .

# Example 3: Extract just the completion text
echo -e "\n=== Example 3: Extract Completion Text ==="
COMPLETION=$(curl -s -X POST "$API_URL/v1/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def add(",
    "max_tokens": 20
  }' | jq -r '.completion')

echo "Generated completion:"
echo "def add($COMPLETION"

# Example 4: Check usage
echo -e "\n=== Example 4: Check Account Usage ==="
curl -s -H "Authorization: Bearer $API_KEY" \
  "$API_URL/v1/account/usage" | jq '.total_tokens, .cost_this_month_cents'

# Example 5: Batch completions from a file
echo -e "\n=== Example 5: Batch Completions ==="
cat > /tmp/prompts.txt << EOF
def fibonacci(
def factorial(
class User:
EOF

while IFS= read -r prompt; do
  echo "Prompt: $prompt"
  curl -s -X POST "$API_URL/v1/completions" \
    -H "Authorization: Bearer $API_KEY" \
    -H "Content-Type: application/json" \
    -d "{\"prompt\": \"$prompt\", \"max_tokens\": 20}" | \
    jq -r '.completion'
  echo ""
done < /tmp/prompts.txt

# Example 6: Save results to file
echo -e "\n=== Example 6: Save Results to JSON ==="
curl -s -X POST "$API_URL/v1/completions" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "def merge_lists(",
    "max_tokens": 40
  }' | jq . > /tmp/completion_result.json

echo "Result saved to /tmp/completion_result.json"
cat /tmp/completion_result.json

echo -e "\n=========================================="
echo "Shell script examples completed!"
echo "=========================================="
