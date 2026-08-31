import hashlib, re
from typing import Any, Dict, List, Optional, Set, Tuple
from dataclasses import dataclass

@dataclass
class CodeClone:
    clone_type: str
    file_a: str
    start_line_a: int
    end_line_a: int
    file_b: str
    start_line_b: int
    end_line_b: int
    similarity: float
    token_count: int

class CloneDetectionEngine:
    """Multi-level code duplication and clone detector utilizing Rabin-Karp AST hashing."""

    def __init__(self, min_chunk_lines: int = 2, min_similarity: float = 0.85):
        self.min_chunk_lines = min_chunk_lines
        self.min_similarity = min_similarity
        self._indexed_files = []

    def normalize_token_stream(self, lines: List[str]) -> str:
        text = " ".join(lines)
        text = re.sub(r'"[^"]*"|\'[^\']*\'', 'STR_LIT', text)
        text = re.sub(r'\b\d+(\.\d+)?\b', 'NUM_LIT', text)
        tokens = []
        for tok in re.split(r'(\W+)', text):
            if tok in ('NUM_LIT', 'STR_LIT'):
                tokens.append(tok)
            elif re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', tok):
                tokens.append('IDENT')
            else:
                tokens.append(tok)
        return "".join(tokens)

    def index_snippet(self, file_path: str, content: str):
        self._indexed_files.append({"file_path": file_path, "content": content})

    def find_clones(self) -> List[Dict[str, Any]]:
        return self.detect_clones(self._indexed_files, min_lines=self.min_chunk_lines, min_similarity=self.min_similarity)

    @classmethod
    def detect_clones(cls, files_data: List[Dict[str, Any]], min_lines: int = 2, min_similarity: float = 0.85) -> List[Dict[str, Any]]:
        clones = []
        blocks = []

        for f in files_data:
            path = f.get('file_path', '')
            content = f.get('content', '')
            lines = [l.strip() for l in content.splitlines()]
            for i in range(len(lines) - min_lines + 1):
                chunk = lines[i:i + min_lines]
                raw_chunk = "\n".join(chunk)
                norm_chunk = cls._normalize_tokens(raw_chunk)
                exact_hash = hashlib.md5(raw_chunk.encode('utf-8')).hexdigest()
                norm_hash = hashlib.md5(norm_chunk.encode('utf-8')).hexdigest()
                blocks.append({
                    'file': path,
                    'start_line': i + 1,
                    'end_line': i + min_lines,
                    'raw': raw_chunk,
                    'norm': norm_chunk,
                    'exact_hash': exact_hash,
                    'norm_hash': norm_hash,
                    'line_count': min_lines
                })

        seen_pairs = set()
        for i in range(len(blocks)):
            for j in range(i + 1, len(blocks)):
                b1, b2 = blocks[i], blocks[j]
                if b1['file'] == b2['file'] and abs(b1['start_line'] - b2['start_line']) < min_lines:
                    continue
                pair_key = (b1['file'], b1['start_line'], b2['file'], b2['start_line'])
                if pair_key in seen_pairs:
                    continue

                if b1['exact_hash'] == b2['exact_hash']:
                    seen_pairs.add(pair_key)
                    clones.append(CodeClone(
                        clone_type='Type-1 (Exact Duplicate)',
                        file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                        file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                        similarity=1.0, token_count=len(b1['raw'].split())
                    ).__dict__)
                elif b1['norm_hash'] == b2['norm_hash']:
                    seen_pairs.add(pair_key)
                    clones.append(CodeClone(
                        clone_type='Type-2 (Renamed Identifiers)',
                        file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                        file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                        similarity=0.95, token_count=len(b1['norm'].split())
                    ).__dict__)
                else:
                    sim = cls._calculate_jaccard_similarity(b1['norm'], b2['norm'])
                    if sim >= min_similarity:
                        seen_pairs.add(pair_key)
                        clones.append(CodeClone(
                            clone_type='Type-3 (Gapped Modification)',
                            file_a=b1['file'], start_line_a=b1['start_line'], end_line_a=b1['end_line'],
                            file_b=b2['file'], start_line_b=b2['start_line'], end_line_b=b2['end_line'],
                            similarity=round(sim, 3), token_count=len(b1['norm'].split())
                        ).__dict__)

        return clones

    @classmethod
    def _normalize_tokens(cls, code: str) -> str:
        norm = re.sub(r'[A-Za-z_][A-Za-z0-9_]*', 'ID', code)
        norm = re.sub(r'\d+(?:\.\d+)?', 'NUM', norm)
        norm = re.sub(r'"[^"]*"|\'[^\']*\'', 'STR', norm)
        return " ".join(norm.split())

    @classmethod
    def _calculate_jaccard_similarity(cls, str1: str, str2: str) -> float:
        set1 = set(str1.split())
        set2 = set(str2.split())
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
