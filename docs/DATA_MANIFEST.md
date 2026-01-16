# Dataset Manifest & Ingestion Plan

## Purpose
Document candidate dataset sources, license rules, data format, secrets/PII scrubbing policy, and provenance requirements for training the Cross-App Coding AI.

---

## Candidate data sources
- CodeSearchNet (per-language corpora)
- The Stack (public GitHub dumps — only with license-safe filtering)
- Public coding challenge datasets: HumanEval, MBPP
- Language-specific curated corpora (pypi packages, npm packages) with license checks
- In-house / user-contributed corpora (opt-in, consented)

---

## License & provenance rules
- Only ingest files with permissive licenses (MIT, BSD, Apache 2.0) or explicitly allowed by project owners.
- Maintain provenance metadata for every file: source_url, commit_hash, license, author (if available), ingestion_time.
- Keep a manifest CSV/JSONL with one entry per file and the above metadata.

---

## Secrets & PII scrubbing
- Detect and remove secrets (API keys, private keys, tokens) using regex patterns and heuristics.
- Mask detected secrets (e.g., replace middle characters with `*`) and log detection counts for review.
- Remove files flagged as containing credentials from training pools unless manually approved.
- Apply PII detection (emails, SSNs, phone numbers) and either redact or exclude depending on sensitivity.
- Optionally run an ML-based PII detector (spaCy NER) for improved PERSON/ORG/GPE detection if the optional dependency is available; fall back to regex-based detection otherwise. 

---

## Dataset format
- Store each sample as JSONL with metadata fields:
  - id, source, path, language, license, provenance
  - content (code), score (optional), tags
- Use UTF-8, normalize line endings, and canonicalize encoding.

---

## Sampling & deduplication
- Deduplicate by file checksum and normalized content using a content normalization + SHA256 checksum approach (see `scripts/data/deduplicate.py`).
- Keep a duplicates log for audit and provenance review.
- Sample balancing: avoid over-representing a single repo or author.
- Keep holdout datasets for evaluation with strict provenance.

---

## Retention & deletion
- Honor takedown requests and provide traceable deletion (update manifest and remove occurrences from training sets). 
- Keep logs of deletion events (who requested, timestamp, reason).

---

## Initial tasks & deliverables
1. Create `data/manifest.jsonl` with sample entries.  
2. Implement `scripts/data/scrub_secrets.py` (regex-based scanner + redaction).  
3. Implement `scripts/data/ingest_sample.py` to pull small public datasets for testing.  
4. Add unit tests for scrubbing and deduplication logic.  

---

Next step: implement the basic scrubber and sample ingester (I will add sample scripts and tests now).