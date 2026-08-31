# Master 70k LOC Generator
import os, sys, math, re
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    print(f'[GENERATED] {rel_path:<55} ({loc:>5} LOC)')
    return loc

total_loc = 0
print('Starting Master 70k Codebase Generation...')
