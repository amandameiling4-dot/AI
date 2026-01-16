"""Example: Fine-tune a code model with PEFT (LoRA) + Hugging Face Accelerate

Notes:
- This is a minimal, proof-of-concept script. Adapt paths, tokenizer/model names, and dataset ingestion to your needs.
- Requires: transformers, datasets, accelerate, peft, bitsandbytes (optional for quantization)
"""

from transformers import AutoTokenizer, AutoModelForCausalLM
from datasets import load_dataset
from peft import get_peft_model, LoraConfig, TaskType
from transformers import Trainer, TrainingArguments

MODEL_NAME = "bigcode/starcoder-base"  # replace with chosen model
TRAIN_DATA = "path/to/your/train.jsonl"  # suggested: instruction-style JSONL

# Load tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_fast=True)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, trust_remote_code=True)

# Example LoRA config
peft_config = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    inference_mode=False,
    r=16,
    lora_alpha=32,
    lora_dropout=0.05,
)
model = get_peft_model(model, peft_config)

# Minimal dataset loading (assumes jsonl with fields: "input" and "output")
raw = load_dataset("json", data_files={"train": TRAIN_DATA})

def tokenize_fn(examples):
    inputs = [f"<S>{i['input']}\n{ i['output']}" for i in examples]
    return tokenizer(inputs, truncation=True, padding="max_length", max_length=1024)

tokenized = raw['train'].map(lambda x: tokenizer(x['input'] + "\n" + x['output'], truncation=True, padding='max_length', max_length=1024), batched=True)

# Training args
training_args = TrainingArguments(
    output_dir="outputs/peft_test",
    per_device_train_batch_size=1,
    gradient_accumulation_steps=16,
    num_train_epochs=1,
    fp16=True,
    logging_steps=50,
    save_total_limit=3,
)

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized,
)

trainer.train()

# Save only adapter weights
model.save_pretrained("outputs/peft_test/adapters")
print("Saved adapter weights to outputs/peft_test/adapters")