#m Polyglot Parsers Generator in Python
import os, sys, math, re
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write(path, content):
    full = BASE / path
    full.parent.mkdir(parents=True, exist_ok=True)
    full.write_text(content.strip() + '\n', encoding='utf-8')
    print(f'Written {path} - {len(content.splitlines())} lines')

print('Parsers Builder Minimal Setup Complete')
