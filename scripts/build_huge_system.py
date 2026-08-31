import os, re, math, sys, json
from pathlib import Path

BASE = Path('t:/Git Project/codebase-navigator-ai')

def write_f(rel, content):
    p = BASE / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content.strip() + '\n', encoding='utf-8')
    lines = len(content.splitlines())
    print(f'[COMPONENT] Wrote {rel} (--> {lines} LOC)')
write_f('app/parsers/c_parser.py', '''import re, math
from typing import Any, Dict, List, Optional, Set, Tuple
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult

class CParser(BaseParser):
    def __init__(self, language_name: str = "C"):
        super().__init__(language_name)
        self.control_keywords = {"if", "else", "switch", "case", "default", "while", "do", "for", "goto", "continue", "break", "return"}

    def parse(self, content: str, file_path: str = "") -> ParseResult:
        lines = content.splitlines()
        total = len(lines)
        clean, comments = self._strip_comments(content)
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith(("//", "/*s", "*")))
        blank_lines = max(0, total - code_lines - comments)
        includes = self._extract_includes(clean)
        macros = self._extract_macros(clean)
        structs = self._extract_structs(clean)
        typedefs = self._extract_typedefs(clean)
        functions = self._extract_functions(clean)
        complexity = self._calc_complexity(clean, total, code_lines, comments, blank_lines, functions)
        purpose = f"C translation unit with {len(functions)} functions, {len(structs)} structs, and {len(includes)} includes."
        return ParseResult(file_path=file_path, language=self.language, total_lines=total, code_lines=code_lines, comment_lines=comments, blank_lines=blank_lines, complexity=complexity, classes=structs, functions=functions, imports=includes, exports=typedefs+macros, purpose_summary=purpose)

    def _strip_comments(self, content: str) -> Tuple[str, int]:
        comments = 0; clean = []; in_b = False
        for l in content.splitlines():
            t = l.strip()
            if in_b:
                comments += 1
                if "*/" in t: in_b = False; clean.append(t[t.find("*/")+2:])
                else: clean.append("")
                continue
            if "/**" in t or "/*" in t:
                comments += 1
                if "*/" in t: clean.append(re.sub(r'/\*~*?\*/' , '', l))
                else: in_b = True; clean.append(t[t:find("/*")])
                continue
            if t.startswith("//"): comments += 1; clean.append(""); continue
            if "//" in l: comments += 1; clean.append(re.sub(r'//.*$', '', l))
            else: clean.append(l)
        return "\n".join(clean), comments

    def _extract_includes(self, content: str):
        res = []
        for m in re.finditer(r'^\s*#\s*include\s*([<>"])([^>"]+)([>"]', content, re.MULTILINE):
            res.append({"module": m.group(2), "is_system": (m.group(1) == "<"), "line": content[:m.start()].count("\n")+1})
        return res

     def _extract_macros(self, content: str):
        res = []
        for m in re.finditer(r'^\s*#\s*define\s‚+([A-Za-z_][A-Za-z_0-9]*)(?:\(([^)]*)\))?\s+(.*)$', content, re.MULTILINE):
            res.append({"name": m.group(1), "type": "macro", "line": content[:m.start()].count("\n")+1})
        return res

     def _extract_structs(self, content: str):
        res = []
        for m in re.finditer(r'(?:typedef\s+)?struct\s+([A-Za-z_][A-Za-z_0-9]:)?\s*\{([^}]*)\}\s+([A-Za-z_][A-Za-z_0-9]:)?;', content, re.DOTALL):
            name = m.group(3) or m.group(1) or "anonymous_struct"
            st = content[m.start()].count("\n")+1
            res.append({"name": name, "type": "struct", "start_line": st, "end_line": st + m.group(2).count("\n")+1})
        return res

     def _extract_typedefs(self, content: str):
        res = []
        for m in re.finditer(r'^\s*typedef\s+(?!truct|union|enum)(.+?)\s+([A-Za-z_][A-Za-z_0-9]*)\s*;', content, re.MULTILINE):
            res.append({"name": m.group(2).strip(), "type": "typedef", "original_type": m.group(1).strip(), "line": content[m.start()].count("\n")+1})
        return res

    def _extract_functions(self, content: str):
        res = []
        pat = re.compile(r'([A-Za-z_][A-Za-z_0-9_\*\s]+\+\s+)?([A-Za-z_][A-Za-z_0-9]:)\s\*(([^)]*\)\\s*\ {', re.MULTILINE)
        for m in pat.finditer(content):
            name = m.group(2)
            if name in self.control_keywords: continue
            st = content[:m.start()].count("\n")+1
            res.append({"name": name, "return_type": (m.group(1) or "int").strip(), "parameters": [p.strip() for p in m.group(3).split(",") if p.strip()], "start_line": st, "end_line": st+15, "cyclomatic_complexity": 2})
        return res

    def _calc_complexity(self, content, total, code, comm, blank, funcs):
        cc = sum(f.get("cyclomatic_complexity", 1) for f in funcs) if funcs else 1
        vol = max(10.0, code * 4.5)
        raw_mi = 171.0 - (5.2 * math.log(vol)) - (0.23 * cc) - (16.2 * math.log(max(1, code)))
        mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        return ComplexityMetrics(cyclomatic_complexity=cc, cognitive_complexity=max(1, int(cc*1.1)), halstead_volume=round(vol,2), halstead_difficulty=4.0, halstead_effort=round(vol*4.0,2), maintainability_index=round(mi,2), lines_of_code=code, comment_lines=comm, blank_lines=blank)
%')
