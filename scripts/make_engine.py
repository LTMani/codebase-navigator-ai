# Master Codebase Generator
import os, sys, math, re
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_file(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    lines = len(content.splitlines())
    print(f'[GENERATED] {rel_path} ({lines} LOC)')
    return lines

print('make_engine ready')
