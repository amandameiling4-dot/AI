# Model Choices & Training Strategy

## Purpose
This document lists candidate open-source models for the Cross-App Coding AI MVP, recommends a default for the prototype, and outlines a starter training strategy using PEFT (LoRA) and Accelerate.

---

## Recommended default (prototype)
- **StarCoder-7B** (or the latest StarCoder small/medium variant)
  - Pros: code-specialized, strong baseline for completions and code tasks, active community
  - Cons: check licensing and dataset provenance
  - Use-case: fast prototype with LoRA adapters for instruction and task-specific tuning

## Alternative candidates
- **CodeGen (6B)**
  - Good for text-to-code generation, multiple sizes available
- **WizardCoder / Instruct-tuned StarCoder**
  - Already instruction-tuned for code-related tasks, good for explanations and doc generation
- **Llama-family (7B/13B)**
  - Good infra compatibility; needs more code-focused fine-tuning
- **Small/edge models (3B)**
  - For local/private deployment with quantization (GPTQ)

---

## Size strategy
- Prototype: 3–7B + LoRA (cheap, fast iterations)
- MVP: 7–13B + PEFT + RAG (better quality with reasonable cost)
- Production: 70B+ or model ensembles for greater code understanding (higher infra cost)

---

## Training approach (starter)
- Use **PEFT/LoRA** adapters for fast, low-cost fine-tuning
- Use **Accelerate** (Hugging Face) or **DeepSpeed** when scaling to multi-GPU
- Use instruction-style data and repo-context pairs for enabling docstrings, explanations, and tests
- Add RAG vector store (FAISS/Milvus) to provide repo-aware context during inference

---

## Evaluation metrics
- HumanEval / MBPP pass rates (for Python)
- Custom repo-specific unit tests
- Linter/static analysis pass rates
- Latency & cost-per-call

---

## Starter hyperparameters (recommended)
- Batch size: 128–512 tokens per GPU (use gradient accumulation as needed)
- Learning rate: 1e-4 – 3e-4 (LoRA only) with warmup
- LoRA rank: 8–32 depending on model size
- Eval: run unit tests + static checks on validation set per epoch

---

## Notes & compliance
- Always verify dataset licenses and remove secrets/PII before fine-tuning
- Keep the base model weights intact and ship only adapter weights for easier audits and smaller artifacts

---

Next: scaffold a sample training script and a minimal config to run a PEFT experiment.