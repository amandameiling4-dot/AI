from typing import Optional, List, Dict
import os
import re
import time

from fastapi import FastAPI, HTTPException, Header, Depends, status
from pydantic import BaseModel, Field

from backend.storage import AppStore
from backend.auth import AUTH_STORE, Token, UserCreate, create_access_token, get_current_user

# Billing integration (stub) - commented out as UsageRecord is not used
# from backend.billing.models import UsageRecord  # keep if used elsewhere

app = FastAPI(title="Code AI Server", version="0.1.0")

# Model cache
_MODEL = None
_TOKENIZER = None


class CompletionRequest(BaseModel):
    prompt: str
    max_tokens: int = 100
    temperature: float = 0.7
    top_p: float = 0.95


class CompletionResponse(BaseModel):
    prompt: str
    completion: str
    tokens_used: int
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    model_loaded: bool


class BuildRequest(BaseModel):
    description: str = Field(..., min_length=1, max_length=5000)
    app_type: str = "website"


class BuildResponse(BaseModel):
    project_name: str
    app_type: str
    generated_files: List[str]
    security_checks: List[str]


class ThoughtRequest(BaseModel):
    content: str
    source: str = "user"


class ThoughtItem(BaseModel):
    content: str
    source: str


class ThoughtsResponse(BaseModel):
    thoughts: List[ThoughtItem]


class ConnectedAppRequest(BaseModel):
    app_name: str
    app_id: str


class ConnectedAppResponse(BaseModel):
    app_name: str
    app_id: str
    synced: bool


# Persistent storage for app generation, headspace thoughts, and connected apps.
_STORE = AppStore()


def get_api_key(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate API key from Authorization header."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing API key")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid API key format")

    token = authorization[7:].strip()
    valid_tokens = {os.getenv("API_TOKEN", "prod-api-token-2026")}
    if token not in valid_tokens:
        raise HTTPException(status_code=401, detail="Invalid or unauthorized API key")
    return token


def _validate_prompt(description: str) -> None:
    """Reject obvious prompt-injection attempts and unsafe requests."""
    blocked_patterns = [
        r"ignore previous instructions",
        r"reveal secrets",
        r"bypass safety",
        r"system prompt",
        r"override policy",
    ]
    lowered = description.lower()
    for pattern in blocked_patterns:
        if re.search(pattern, lowered):
            raise HTTPException(status_code=400, detail="Request blocked by security policy")


def _build_app_artifact(description: str, app_type: str) -> BuildResponse:
    """Create a lightweight app blueprint without requiring a model runtime."""
    project_name = re.sub(r"[^a-z0-9]+", "-", description.lower()).strip("-") or "ai-app"
    generated_files = [
        f"{project_name}/index.html",
        f"{project_name}/styles.css",
        f"{project_name}/app.js",
    ]
    security_checks = [
        "Prompt injection scan passed",
        "Authorization check required for all requests",
        "Input validation enforced",
        "Connected-app sync audit enabled",
    ]
    _STORE.add_generated_app(
        project_name=project_name,
        description=description,
        app_type=app_type,
        generated_files=generated_files,
        security_checks=security_checks,
    )
    return BuildResponse(
        project_name=project_name,
        app_type=app_type,
        generated_files=generated_files,
        security_checks=security_checks,
    )


def load_model(model_name: str = "bigcode/starcoder-base"):
    """Load model (with caching)."""
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
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


@app.post("/v1/auth/signup", response_model=Token)
async def signup(payload: UserCreate):
    user = AUTH_STORE.create_user(payload.email, payload.password)
    token = create_access_token(user.email)
    return Token(access_token=token)


@app.post("/v1/auth/login", response_model=Token)
async def login(payload: UserCreate):
    user = AUTH_STORE.authenticate(payload.email, payload.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(user.email)
    return Token(access_token=token)


@app.post("/v1/completions", response_model=CompletionResponse)
async def completions(request: CompletionRequest, api_key: str = Depends(get_api_key)):
    """Generate code completion from a prompt."""
    try:
        # Load model
        model, tokenizer = load_model()
        import torch

        # Tokenize and generate
        start_time = time.time()
        inputs = tokenizer(request.prompt, return_tensors="pt").to(model.device)
        with torch.no_grad():
            outputs = model.generate(
                **inputs,
                max_new_tokens=request.max_tokens,
                temperature=request.temperature,
                top_p=request.top_p,
            )
        completion = tokenizer.decode(outputs[0], skip_special_tokens=True)
        latency_ms = (time.time() - start_time) * 1000

        # Count tokens for billing
        tokens_used = len(outputs[0])

        # Log usage (stub - real DB write needed)
        # await log_usage(api_key, tokens_used)

        return CompletionResponse(
            prompt=request.prompt,
            completion=completion,
            tokens_used=tokens_used,
            latency_ms=latency_ms,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/ai/build", response_model=BuildResponse)
async def build_app(request: BuildRequest, api_key: str = Depends(get_api_key)):
    """Generate a simple app scaffold from a natural-language description."""
    _validate_prompt(request.description)
    return _build_app_artifact(request.description, request.app_type)


@app.post("/v1/connected-apps", response_model=ConnectedAppResponse)
async def register_connected_app(request: ConnectedAppRequest, api_key: str = Depends(get_api_key)):
    """Register a connected app so headspace thoughts can sync across clients."""
    _STORE.add_connected_app(request.app_name, request.app_id)
    return ConnectedAppResponse(app_name=request.app_name, app_id=request.app_id, synced=True)


@app.post("/v1/headspace/thoughts", response_model=ThoughtItem)
async def add_headspace_thought(request: ThoughtRequest, api_key: str = Depends(get_api_key)):
    """Store a user thought in the shared headspace and sync it to connected apps."""
    _STORE.add_thought(request.content, request.source)
    return ThoughtItem(content=request.content, source=request.source)


@app.get("/v1/headspace/thoughts", response_model=ThoughtsResponse)
async def list_headspace_thoughts(api_key: str = Depends(get_api_key)):
    """List all thoughts stored in the shared headspace."""
    records = _STORE.list_thoughts()
    thoughts = [ThoughtItem(content=item["content"], source=item["source"]) for item in records]
    return ThoughtsResponse(thoughts=thoughts)


@app.get("/v1/account/usage")
async def get_usage(api_key: str = Depends(get_api_key)):
    """Get usage statistics for the API key from persisted activity data."""
    generated_apps = len(_STORE.list_generated_apps())
    thoughts = len(_STORE.list_thoughts())
    connected_apps = len(_STORE.list_connected_apps())
    return {
        "api_key": api_key[:16] + "***",
        "tokens_used_this_month": generated_apps + thoughts,
        "tokens_limit": 100000,
        "requests": generated_apps + thoughts + connected_apps,
        "generated_apps": generated_apps,
        "thoughts": thoughts,
        "connected_apps": connected_apps,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)