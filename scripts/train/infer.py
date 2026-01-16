"""Minimal inference script for LoRA-adapted code models."""
import torch
from pathlib import Path
from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import PeftModel


def load_model_with_adapter(base_model: str, adapter_path: str):
    """Load a base model and attach a LoRA adapter."""
    tokenizer = AutoTokenizer.from_pretrained(base_model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(base_model, torch_dtype=torch.float16, trust_remote_code=True, device_map='auto')
    model = PeftModel.from_pretrained(model, adapter_path)
    return model, tokenizer


def generate_completion(model, tokenizer, prompt: str, max_new_tokens: int = 100) -> str:
    """Generate a code completion from a prompt."""
    inputs = tokenizer(prompt, return_tensors='pt').to(model.device)
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.95,
        )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


if __name__ == '__main__':
    # Example usage (requires trained adapter)
    base_model = 'bigcode/starcoder-base'
    adapter_path = 'models/peft_checkpoint/adapter_weights'

    try:
        model, tokenizer = load_model_with_adapter(base_model, adapter_path)
        prompt = 'def add(a, b):'
        result = generate_completion(model, tokenizer, prompt)
        print(f'Prompt: {prompt}')
        print(f'Generated: {result}')
    except Exception as e:
        print(f'Error (expected if no adapter trained yet): {e}')
