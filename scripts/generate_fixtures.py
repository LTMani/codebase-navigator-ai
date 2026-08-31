# Polyglot Microservices Fixtures Generator
import os
from pathlib import Path

BASE = Path('fixtures/polyglot_microservices')

def write_f(rel_path, content):
    p = BASE / rel_path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    return len(content.splitlines())

print('Starting microservice fixtures generation...')
