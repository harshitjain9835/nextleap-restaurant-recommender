#!/usr/bin/env python3
import os
from pathlib import Path

print("Before dotenv load:")
print(f"  LLM_BASE_URL={os.environ.get('LLM_BASE_URL', 'NOT SET')}")

from dotenv import load_dotenv
env_file = Path(r'g:\nextleap\projects\.env')
print(f"\nLoading from: {env_file}")
print(f"File exists: {env_file.exists()}")

result = load_dotenv(env_file, override=True)
print(f"load_dotenv returned: {result}")

print("\nAfter dotenv load:")
print(f"  LLM_BASE_URL={os.environ.get('LLM_BASE_URL', 'NOT SET')}")
print(f"  LLM_API_KEY={'<SET>' if os.environ.get('LLM_API_KEY') else 'NOT SET'}")

# Read file content
with open(env_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()
    print(f"\nFile content ({len(lines)} lines):")
    for i, line in enumerate(lines[:10], 1):
        print(f"  {i}: {line.rstrip()}")
