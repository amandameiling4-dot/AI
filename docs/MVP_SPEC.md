# MVP Specification — Cross-App Coding AI

## Overview
Create a lightweight, high-quality coding assistant optimized for editor integrations (starting with VS Code) that provides contextual code completion, explanations, and refactor suggestions for common programming languages.

## Goals
- Provide reliable, low-latency completions and inline explanations.
- Be easy to integrate via an SDK and VS Code extension (LSP).
- Prioritize correctness, safety, and privacy (local hosting options).

## Core MVP Features
- Contextual multi-line code completion
- Code explanation and docstring generation
- Unit test generation for functions
- Basic refactor suggestions and quick-fixes
- Editor integration: VS Code via LSP/extension
- Support languages: Python, JavaScript, TypeScript

## Success Metrics
- HumanEval/MBPP pass rate target for supported languages
- Latency: < 200ms per completion (target depends on infra)
- Quality: >= 80% of generated snippets pass linters and basic tests
- Safety: no sensitive data leakage in evaluations

## Evaluation and Benchmarking
- Use existing benchmarks (HumanEval, MBPP) plus a custom suite on real repos
- Periodic regression tests: functionality, latency, and safety

## Timeline (High-level)
- Prototype (2-6 weeks): proof-of-concept fine-tune on small model
- MVP (2-3 months): multi-language support, VS Code extension, RAG for repo context

## Deliverables
- docs/MVP_SPEC.md (this file)
- docs/ARCHITECTURE.md
- Basic VS Code extension skeleton (LSP)
- Training/eval scripts and initial dataset manifest

---

Next steps: finalize model candidates and dataset plan, then prototype with adapter-based fine-tuning.