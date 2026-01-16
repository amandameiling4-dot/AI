"""Minimal PEFT training script for code models.

Usage:
    python scripts/train/train_peft.py \\
        --model bigcode/starcoder-base \\
        --data data/sample/manifest.dedup.jsonl \\
        --output models/peft_checkpoint \\
        --epochs 1 \\
        --batch_size 4
"""
import argparse
import json
from pathlib import Path
from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from peft import get_peft_model, LoraConfig, TaskType
from datasets import Dataset


def load_jsonl_dataset(path: str) -> Dataset:
    """Load a JSONL manifest into a Hugging Face Dataset."""
    samples = []
    with open(path, 'r') as fh:
        for line in fh:
            obj = json.loads(line)
            samples.append({
                'text': obj.get('content', ''),
                'id': obj.get('id', ''),
            })
    return Dataset.from_dict({'text': [s['text'] for s in samples], 'id': [s['id'] for s in samples]})


def tokenize_fn(examples, tokenizer, max_len=1024):
    """Tokenize examples for training."""
    return tokenizer(examples['text'], truncation=True, padding='max_length', max_length=max_len)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', default='bigcode/starcoder-base')
    parser.add_argument('--data', default='data/sample/manifest.dedup.jsonl')
    parser.add_argument('--output', default='models/peft_checkpoint')
    parser.add_argument('--epochs', type=int, default=1)
    parser.add_argument('--batch_size', type=int, default=4)
    parser.add_argument('--gradient_accumulation_steps', type=int, default=4)
    parser.add_argument('--learning_rate', type=float, default=2e-4)
    parser.add_argument('--lora_rank', type=int, default=16)
    parser.add_argument('--lora_alpha', type=int, default=32)
    args = parser.parse_args()

    print(f'Loading model: {args.model}')
    tokenizer = AutoTokenizer.from_pretrained(args.model, use_fast=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float16, trust_remote_code=True)

    print('Setting up PEFT (LoRA)...')
    peft_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        inference_mode=False,
        r=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=0.05,
    )
    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    print(f'Loading data from: {args.data}')
    dataset = load_jsonl_dataset(args.data)
    dataset = dataset.map(lambda x: tokenize_fn(x, tokenizer), batched=True, remove_columns=['text'])

    training_args = TrainingArguments(
        output_dir=args.output,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        num_train_epochs=args.epochs,
        learning_rate=args.learning_rate,
        fp16=True,
        logging_steps=10,
        save_total_limit=3,
        save_strategy='epoch',
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
        data_collator=None,  # Use default collator
    )

    print('Starting training...')
    trainer.train()

    print(f'Saving adapter weights to {args.output}/adapter_weights')
    model.save_pretrained(f'{args.output}/adapter_weights')
    print('Done!')


if __name__ == '__main__':
    main()
