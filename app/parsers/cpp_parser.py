import re, math
from typing import Any, Dict, List, Optional, Set, Tuple
from app.parsers.base_parser import BaseParser, ComplexityMetrics, ParseResult, ExtractedFunction, ExtractedClass, ExtractedImport

class CPPParser(BaseParser):
    def __init__(self, language_name: str = "C++"):
        super().__init__(language_name)

    def parse(self, content: str, file_path: str = "") -> ParseResult:
        lines = content.splitlines()
        total = len(lines)
        clean, comments = self._strip_comments(content)
        code_lines = sum(1 for l in lines if l.strip() and not l.strip().startswith(("//", "/*", "*", "#", "--")))
        blank_lines = max(0, total - code_lines - comments)
        imports = self._extract_imports(clean)
        classes = self._extract_classes(clean)
        functions = self._extract_functions(clean)
        complexity = self._calc_complexity(clean, total, code_lines, comments, blank_lines, functions)
        purpose = f"{self.language} translation unit with {len(classes)} declarations, {len(functions)} functions, and {len(imports)} imports."
        return ParseResult(
            file_path=file_path, language=self.language, total_lines=total,
            code_lines=code_lines, comment_lines=comments, blank_lines=blank_lines,
            complexity=complexity, metrics=complexity, classes=classes, functions=functions,
            imports=imports, purpose_summary=purpose
        )

    def _strip_comments(self, content: str) -> Tuple[str, int]:
        comments = 0; clean = []; in_b = False
        for l in content.splitlines():
            t = l.strip()
            if in_b:
                comments += 1
                if "*/" in t: in_b = False; clean.append(t[t.find("*/")+2:])
                else: clean.append("")
                continue
            if "/*" in t:
                comments += 1
                if "*/" in t: clean.append(re.sub(r"/\*.*?\*/", "", l))
                else: in_b = True; clean.append(t[:t.find("/*")])
                continue
            if t.startswith(("//", "#", "--")): comments += 1; clean.append(""); continue
            if "//" in l: comments += 1; clean.append(re.sub(r"//.*$", "", l))
            elif "#" in l and not l.strip().startswith("#!"): comments += 1; clean.append(re.sub(r"#.*$", "", l))
            else: clean.append(l)
        return "\n".join(clean), comments

    def _extract_imports(self, content: str) -> List[ExtractedImport]:
        res = []
        for m in re.finditer(r"^(?:import|using|require|include|use|source|from)\s+([A-Za-z0-9_./<>\"'-]+)", content, re.MULTILINE):
            res.append(ExtractedImport(module_name=m.group(1).strip("<>\"'"), line_number=content[:m.start()].count("\n")+1))
        return res

    def _extract_classes(self, content: str) -> List[ExtractedClass]:
        res = []
        for m in re.finditer(r"\b(?:class|struct|interface|record|trait|actor|type|message|service|resource)\s+([A-Za-z0-9_]+)", content):
            st = content[:m.start()].count("\n")+1
            res.append(ExtractedClass(name=m.group(1), start_line=st, end_line=st+20))
        return res

    def _extract_functions(self, content: str) -> List[ExtractedFunction]:
        res = []
        for m in re.finditer(r"\b(?:def|func|fn|function|fun|rpc|procedure)\s+([A-Za-z0-9_]+)\s*\(([^)]*)\)", content):
            name = m.group(1)
            st = content[:m.start()].count("\n")+1
            params = [p.strip() for p in m.group(2).split(",") if p.strip()]
            res.append(ExtractedFunction(name=name, parameters=params, start_line=st, end_line=st+15, cyclomatic_complexity=2))
        return res

    def _calc_complexity(self, content, total, code, comm, blank, funcs):
        cc = sum(f.cyclomatic_complexity for f in funcs) if funcs else 1
        vol = max(10.0, code * 4.2)
        raw_mi = 171.0 - (5.2 * math.log(vol)) - (0.23 * cc) - (16.2 * math.log(max(1, code)))
        mi = max(0.0, min(100.0, (raw_mi * 100.0) / 171.0))
        return ComplexityMetrics(
            cyclomatic_complexity=cc, cognitive_complexity=max(1, int(cc*1.1)),
            halstead_volume=round(vol,2), halstead_difficulty=4.0,
            halstead_effort=round(vol*4.0,2), maintainability_index=round(mi,2),
            lines_of_code=code, comment_lines=comm, blank_lines=blank
        )
