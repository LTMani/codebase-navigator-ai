import os
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')
total_loc = 0
file_count = 0

def write_f(rel_path, content):
    global total_loc, file_count
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    loc = len(content.splitlines())
    total_loc += loc
    file_count += 1
    print(f'[+] {rel_path:<60} ({loc:>5} LOC)')
    return loc

print('Starting all modules builder...')
