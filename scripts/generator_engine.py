# Enterprise Codebase Generator Engine
import os, sys, math, re
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    return loc

total_loc = 0
file_count = 0
