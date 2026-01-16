# Architecture Overview — Cross-App Coding AI

## High-level components
- **Model**: Foundation code LLM (open-source candidate) with adapter-based fine-tuning for rapid iteration.
- **Data Pipeline**: Ingest, filter, and preprocess code corpora with license tagging and secrets scrubbing.
- **Retrieval (RAG)**: Vector DB (FAISS/Milvus) for repository-aware context augmentation.
- **API / Inference**: Model server offering REST/streaming endpoints; supports quantized and CPU/GPU deployments.
- **Editor Integrations**: LSP-based VS Code extension for completions, diagnostics, and code actions.
- **Evaluation & Monitoring**: Automated test suites, metrics dashboards for latency, correctness, and safety.

## Data flow (summary)
1. Raw sources (public corpora, curated datasets) →
2. Preprocessing: dedupe, license filter, normalize →
3. Vectorization for RAG + model fine-tuning datasets →
4. Training/fine-tuning → Model →
5. Serving + RAG retrieval → Editor / SDK clients

## Tech choices (initial)
- Models: StarCoder, CodeGen, or other permissively licensed code LLMs
- Fine-tuning: Hugging Face Transformers + PEFT (LoRA) + Accelerate/DeepSpeed
- Vector DB: FAISS (local) / Milvus (managed) depending on scale
- Serving: containerized API (FastAPI or Triton/KServe for production)
- Editor: VS Code extension via LSP (Language Server Protocol)

## Security & Privacy
- Secrets and PII detection during ingestion
- Option for on-prem/private-hosted inference
- Audit logs and provenance metadata for all training data

## Deployment options
- Local desktop: quantized model with local inference for privacy
- Cloud-managed: autoscaled GPU clusters with monitoring and logging

## Next steps
- Choose initial model candidates and hardware targets
- Draft dataset manifest and filtering rules
- Prototype a small LSP-based extension and an inference API
