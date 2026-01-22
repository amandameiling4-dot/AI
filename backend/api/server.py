from typing import Optional
import os
import time
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel

# Billing integration (stub)
from backend.billing.models import UsageRecord  # keep if used elsewhere

app = FastAPI(title="Code AI Server", version="0.1.0")

# Model cache
_MODEL = None
_TOKENIZER = None


class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.95
    stop: list[str] = []


class CompletionResponse(BaseModel):
    prompt: str
    completion: str
    tokens_used: int
    latency_ms: float
    stop_reason: str


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


def get_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate API key from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key format")
    return authorization[7:]


def load_model(model_name: str = "bigcode/starcoder-base"):
    """Load model (with caching)."""
    global _MODEL, _TOKENIZER
    if _MODEL is None:
        _TOKENIZER = AutoTokenizer.from_pretrained(model_name, use_fast=True)
        _MODEL = AutoModelForCausalLM.from_pretrained(
            model_name, torch_dtype=torch.float16, trust_remote_code=True, device_map="auto"
        )
    return _MODEL, _TOKENIZER


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="ok", model_loaded=_MODEL is not None)


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest, api_key: str = Depends(get_api_key)):
    """Generate code completion from a prompt."""
    try:
        # Load model
        model, tokenizer = load_model()

        # Tokenize and generate
        start_time = time.time()
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
        
        # Prepare generation kwargs
        generation_kwargs = {
            "max_new_tokens": request.max_tokens,
            "temperature": request.temperature,
            "top_p": request.top_p,
        }
        
        # Add stop sequences if provided
        if request.stop:
            # Encode stop sequences as additional eos tokens
            stop_token_ids = []
            for stop_seq in request.stop:
                stop_tokens = tokenizer.encode(stop_seq, add_special_tokens=False)
                if stop_tokens:
                    stop_token_ids.extend(stop_tokens)
            if stop_token_ids:
                # Add to existing eos_token_id
                eos_token_id = tokenizer.eos_token_id
                if isinstance(eos_token_id, int):
                    eos_token_id = [eos_token_id]
                elif eos_token_id is None:
                    eos_token_id = []
                generation_kwargs["eos_token_id"] = list(set(eos_token_id + stop_token_ids))
        
        with torch.no_grad():
            outputs = model.generate(**inputs, **generation_kwargs)
        
        # Decode only the generated tokens (excluding the prompt)
        generated_tokens = outputs[0][len(inputs[0]):]
        completion = tokenizer.decode(generated_tokens, skip_special_tokens=True)
        latency_ms = (time.time() - start_time) * 1000

        # Count only generated tokens for billing
        tokens_used = len(generated_tokens)
        
        # Determine stop reason (check EOS first, then stop sequences)
        stop_reason = "length"
        # Check if EOS token was hit before max_tokens
        if tokenizer.eos_token_id and tokenizer.eos_token_id in generated_tokens:
            if len(generated_tokens) < request.max_tokens:
                stop_reason = "eos"
        # Check if completion ends with any stop sequence
        if stop_reason == "length" and request.stop:
            for stop_seq in request.stop:
                if completion.endswith(stop_seq):
                    stop_reason = "stop_token"
                    break

        # Log usage (stub - real DB write needed)
        # await log_usage(api_key, tokens_used)

        return CompletionResponse(
            prompt=request.prompt,
            completion=completion,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
            stop_reason=stop_reason,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/v1/account/usage")
async def get_usage(api_key: str = Depends(get_api_key)):
    """Get usage statistics for the API key."""
    # Stub: return placeholder
    return {
        "api_key": api_key[:16] + "***",
        "tokens_used_this_month": 10000,
        "tokens_limit": 100000,
        "requests": 150,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)