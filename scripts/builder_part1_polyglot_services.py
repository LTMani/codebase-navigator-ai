# Part 1: Go, Rust, Java, C# Microservices
import os
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    return loc

print('Generating Part 1: Go, Rust, Java, C# Microservices...')
