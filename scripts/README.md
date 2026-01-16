# Training scripts

This folder contains minimal example scripts to run PEFT/LoRA experiments.

Quick start:
1. Prepare your dataset as `jsonl` with fields `input` and `output` (instruction-response pairs).
2. Update `configs/peft_config.yaml` for dataset path and model name.
3. Create an Accelerate config (e.g., `accelerate config`) and run:

```bash
python scripts/train_peft_example.py
```

Notes:
- This is a minimal example for experimentation. For production training, add proper dataset loading, sharding, monitoring, eval, and checkpointing logic.