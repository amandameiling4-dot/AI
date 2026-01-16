# Training & scripts quick-start

## Setup
```bash
pip install -r requirements-train.txt
# For PEFT + LoRA:
pip install -r requirements-dev.txt  # (optional ML detectors)
```

## Training a code model
```bash
python scripts/train/train_peft.py \
    --model bigcode/starcoder-base \
    --data data/sample/manifest.dedup.jsonl \
    --output models/peft_checkpoint \
    --epochs 1 \
    --batch_size 4
```

## Running inference with adapter
```bash
python scripts/train/infer.py
```

## Evaluation
```bash
python scripts/eval/evaluate.py
```

See `docs/MODEL_CHOICES.md` for hyperparameter guidance.
