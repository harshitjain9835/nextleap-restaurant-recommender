from __future__ import annotations

from pathlib import Path
import os

print(f"CWD: {Path.cwd()}", flush=True)
print(f".env exists: {Path('.env').exists()}", flush=True)
if Path('.env').exists():
    with open('.env', 'r') as f:
        content = f.read()
    print(f".env content (first 500 chars):\n{content[:500]}", flush=True)

print(f"\nEnvironment variables loaded by Python:", flush=True)
print(f"LLM_BASE_URL={os.environ.get('LLM_BASE_URL', 'NOT SET')}", flush=True)
print(f"LLM_API_KEY={os.environ.get('LLM_API_KEY', 'NOT SET')}", flush=True)

# Now load settings
from app.config import Settings
settings = Settings()
print(f"\nSettings loaded:", flush=True)
print(f"  llm_base_url={settings.llm_base_url}", flush=True)
print(f"  llm_api_key={'<SET>' if settings.llm_api_key else 'NOT SET'}", flush=True)
