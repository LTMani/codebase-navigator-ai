# 70k LOC Generator Engine
import os, sys, math, re
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_module(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    print(f'[WROTE] {rel_path:<50} ({loc:>5} LOC)')
    return loc

print('Build Engine Initialized')
