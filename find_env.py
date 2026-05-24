#!/usr/bin/env python3
import os
from pathlib import Path

# Check all possible .env files
possible_paths = [
    Path(r'g:\nextleap\projects\.env'),
    Path.cwd() / '.env',
    Path.home() / '.env',
]

print("Searching for .env files:")
for p in possible_paths:
    exists = p.exists()
    print(f"\n{p}")
    print(f"  exists: {exists}")
    if exists:
        with open(p, 'rb') as f:
            content = f.read()
        print(f"  size: {len(content)} bytes")
        # Show first few lines
        lines = content.decode('utf-8', errors='replace').split('\n')[:12]
        for i, line in enumerate(lines, 1):
            if 'LLM_BASE_URL' in line or 'LLM_MODEL' in line:
                print(f"  {i}: {line}")
