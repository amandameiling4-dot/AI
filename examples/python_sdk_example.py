"""
Example: Using CodeAI Python SDK

This example demonstrates how to:
1. Initialize the CodeAI client
2. Generate code completions
3. Track usage and billing
4. Handle errors gracefully
"""

from sdk.python.client import CodeAIClient
import json

# Initialize client
client = CodeAIClient(
    api_key="test_key_12345",  # Get from API key endpoint
    base_url="http://localhost:8000"  # Or production URL
)

# Example 1: Basic code completion
print("=" * 60)
print("Example 1: Basic Code Completion")
print("=" * 60)

prompt = """def fibonacci(n):
    \"\"\"Calculate the nth Fibonacci number.\"\"\"
    """

try:
    response = client.complete(
        prompt=prompt,
        max_tokens=50,
        temperature=0.5
    )
    
    print(f"Prompt:\n{prompt}")
    print(f"\nCompletion:\n{response['completion']}")
    print(f"Tokens used: {response['tokens_used']}")
    print(f"Latency: {response['latency_ms']:.2f}ms")
except Exception as e:
    print(f"Error: {e}")

# Example 2: More creative completions (higher temperature)
print("\n" + "=" * 60)
print("Example 2: Creative Completions (Higher Temperature)")
print("=" * 60)

prompt = "def hello_world():"

response = client.complete(
    prompt=prompt,
    max_tokens=30,
    temperature=0.9  # Higher = more creative
)

print(f"Prompt: {prompt}")
print(f"Completion: {response['completion']}")

# Example 3: Check usage and billing
print("\n" + "=" * 60)
print("Example 3: Account Usage")
print("=" * 60)

usage = client.get_usage()
print(json.dumps(usage, indent=2))

# Example 4: Error handling
print("\n" + "=" * 60)
print("Example 4: Error Handling")
print("=" * 60)

# Try with invalid token
try:
    bad_client = CodeAIClient(
        api_key="invalid_key",
        base_url="http://localhost:8000"
    )
    response = bad_client.complete(prompt="def test():")
except Exception as e:
    print(f"Caught error (expected): {e}")

# Example 5: Batch completions
print("\n" + "=" * 60)
print("Example 5: Batch Completions")
print("=" * 60)

prompts = [
    "def sum_list(",
    "def sort_",
    "class DataFr",
]

completions = []
for prompt in prompts:
    response = client.complete(prompt=prompt, max_tokens=20)
    completions.append({
        "prompt": prompt,
        "completion": response['completion'],
        "tokens": response['tokens_used']
    })

for i, item in enumerate(completions, 1):
    print(f"\n{i}. Prompt: {item['prompt']}")
    print(f"   Completion: {item['completion']}")
    print(f"   Tokens: {item['tokens']}")

# Example 6: Health check
print("\n" + "=" * 60)
print("Example 6: Server Health Check")
print("=" * 60)

health = client.health()
print(f"Server status: {health['status']}")

print("\n" + "=" * 60)
print("Examples completed!")
print("=" * 60)
