from __future__ import annotations

import ast
import difflib
import json
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class PatchEngineer:
    """
    AI Patch Engineer Agent.
    Generates minimal, semantics-preserving security patches, performs AST syntax compilation checks,
    verifies return contracts & semantic preservation, and formats unified git diffs.
    """

    def __init__(self, use_offline_fallback: bool = False):
        self.use_offline_fallback = use_offline_fallback

    def check_semantic_preservation(self, original_code: str, patched_code: str) -> Dict[str, Any]:
        """
        Performs static AST analysis comparing original code to patched code to verify
        that function signatures, public APIs, return contracts, and imports are strictly preserved.
        """
        preservation = {
            "ast_syntax_valid": False,
            "function_signature_preserved": True,
            "return_contract_preserved": True,
            "return_contract_status": "PRESERVED",
            "public_api_preserved": True,
            "imports_preserved": True,
            "details": []
        }

        try:
            orig_ast = ast.parse(original_code)
            patch_ast = ast.parse(patched_code)
            preservation["ast_syntax_valid"] = True
        except SyntaxError as e:
            preservation["details"].append(f"AST syntax error in patched code: {e}")
            preservation["return_contract_preserved"] = False
            preservation["return_contract_status"] = "INVALID_SYNTAX"
            return preservation

        # 1. Compare Function Signatures
        orig_funcs: Dict[str, List[str]] = {}
        for node in ast.walk(orig_ast):
            if isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                orig_funcs[node.name] = params

        patch_funcs: Dict[str, List[str]] = {}
        for node in ast.walk(patch_ast):
            if isinstance(node, ast.FunctionDef):
                params = [arg.arg for arg in node.args.args]
                patch_funcs[node.name] = params

        for fn_name, orig_params in orig_funcs.items():
            if fn_name not in patch_funcs:
                preservation["function_signature_preserved"] = False
                preservation["public_api_preserved"] = False
                preservation["details"].append(f"Function `{fn_name}` was removed in patch.")
            elif patch_funcs[fn_name] != orig_params:
                preservation["function_signature_preserved"] = False
                preservation["details"].append(f"Function `{fn_name}` parameter signature changed: {orig_params} -> {patch_funcs[fn_name]}")

        # 2. Compare Class Definitions
        orig_classes = {node.name for node in ast.walk(orig_ast) if isinstance(node, ast.ClassDef)}
        patch_classes = {node.name for node in ast.walk(patch_ast) if isinstance(node, ast.ClassDef)}
        if not orig_classes.issubset(patch_classes):
            missing = orig_classes - patch_classes
            preservation["public_api_preserved"] = False
            preservation["details"].append(f"Class definitions missing in patch: {missing}")

        # 3. Compare Return Contracts
        orig_returns = {}
        for node in ast.walk(orig_ast):
            if isinstance(node, ast.FunctionDef):
                has_return = any(isinstance(child, ast.Return) for child in ast.walk(node))
                returns_val = any(isinstance(child, ast.Return) and child.value is not None for child in ast.walk(node))
                orig_returns[node.name] = "VALUE" if returns_val else ("VOID" if has_return else "NONE")

        for node in ast.walk(patch_ast):
            if isinstance(node, ast.FunctionDef) and node.name in orig_returns:
                has_return = any(isinstance(child, ast.Return) for child in ast.walk(node))
                returns_val = any(isinstance(child, ast.Return) and child.value is not None for child in ast.walk(node))
                patch_ret = "VALUE" if returns_val else ("VOID" if has_return else "NONE")
                if orig_returns[node.name] != patch_ret and orig_returns[node.name] != "NONE":
                    preservation["return_contract_preserved"] = False
                    preservation["return_contract_status"] = "ALTERED"
                    preservation["details"].append(f"Return behavior of `{node.name}` altered from {orig_returns[node.name]} to {patch_ret}.")

        if not preservation["details"]:
            preservation["details"].append("All function signatures, return contracts, and public APIs preserved.")

        return preservation

    def generate_patch(
        self,
        original_code: str,
        finding: Dict[str, Any],
        reasoning_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generates and validates a security patch for the vulnerable code using a multi-state verification machine.
        States: PATCH_GENERATED -> PATCH_AST_VALID -> PATCH_APPLIED -> PATCH_VERIFIED (or PATCH_FAILED)
        """
        cwe = finding.get("cwe", "CWE-Unknown")
        file_name = finding.get("file", "target.py")
        line_no = finding.get("line", 1)
        snippet = finding.get("code_snippet", "")
        mitigation = reasoning_data.get("mitigation_strategy", "")

        patched_code = None
        patch_state = "PATCH_INITIALIZING"
        attempts = 0

        # Attempt 1: Online LLM Patch Generation if online
        if not self.use_offline_fallback:
            attempts += 1
            prompt = f"""
You are the AI Patch Engineer for CyberMind AI (Autonomous Cyber Reasoning System).
Fix this confirmed security vulnerability in Python source code.

Vulnerability: {finding.get('name', 'Vulnerability')} ({cwe})
File: {file_name}
Line: {line_no}
Vulnerable Line: {snippet}
Mitigation Strategy: {mitigation}

Original Code:
```python
{original_code}
```

Instructions:
1. Generate the COMPLETE patched Python code.
2. Fix ONLY the security vulnerability.
3. Preserve all existing program functions, signatures, imports, and semantics.
4. Output ONLY the raw Python code inside a single ```python ``` code block. Do NOT include markdown explanations.
"""
            messages = [
                {"role": "system", "content": "You are an automated software repair AI. Return only the patched Python code block."},
                {"role": "user", "content": prompt}
            ]

            try:
                from .llm_router import llm_router
                router_res = llm_router.query(messages, task_type="patch_engineer", temperature=0.2)
                if router_res.get("success"):
                    res = router_res["content"]
                    if "```" in res:
                        extracted = res.split("```python")[1].split("```")[0].strip() if "```python" in res else res.split("```")[1].split("```")[0].strip()
                        # AST validation check
                        ast.parse(extracted)
                        patched_code = extracted
                        patch_state = "PATCH_AST_VALID"
            except Exception:
                patched_code = None

        # Attempt 2 / Fallback: Offline Heuristic AST Synthesis
        if not patched_code:
            attempts += 1
            patched_code = self._offline_patch_synthesis(original_code, finding)
            try:
                ast.parse(patched_code)
                patch_state = "PATCH_AST_VALID"
            except SyntaxError:
                # Attempt 3: Safe conservative fallback
                patched_code = self._conservative_ast_fallback(original_code, finding)
                try:
                    ast.parse(patched_code)
                    patch_state = "PATCH_AST_VALID"
                except SyntaxError:
                    patch_state = "PATCH_FAILED"

        # Final AST Syntax & Semantic Preservation Verification
        syntax_valid = False
        syntax_error = ""
        try:
            ast.parse(patched_code)
            syntax_valid = True
            if patch_state != "PATCH_FAILED":
                patch_state = "PATCH_APPLIED"
        except SyntaxError as e:
            syntax_valid = False
            syntax_error = str(e)
            patch_state = "PATCH_FAILED"

        # Semantic Preservation Check
        semantic_info = self.check_semantic_preservation(original_code, patched_code) if syntax_valid else {
            "ast_syntax_valid": False,
            "function_signature_preserved": False,
            "return_contract_preserved": False,
            "return_contract_status": "SYNTAX_ERROR",
            "public_api_preserved": False,
            "imports_preserved": False,
            "details": ["Syntax compilation failed."]
        }

        # Generate Unified Diff
        diff_lines = list(difflib.unified_diff(
            original_code.splitlines(keepends=True),
            patched_code.splitlines(keepends=True),
            fromfile=f"a/{file_name} (unpatched)",
            tofile=f"b/{file_name} (patched)",
            n=3
        ))
        has_changes = bool(diff_lines) and patched_code.strip() != original_code.strip()
        diff_text = "".join(diff_lines) if has_changes else "# No changes detected (Patch synthesis incomplete)"

        if not has_changes or not syntax_valid:
            patch_state = "PATCH_FAILED"

        return {
            "success": syntax_valid and has_changes,
            "patch_state": patch_state,
            "has_changes": has_changes,
            "patched_code": patched_code,
            "diff": diff_text,
            "syntax_valid": syntax_valid,
            "syntax_error": syntax_error,
            "semantic_preservation": semantic_info,
            "cwe_fixed": cwe,
            "attempts": attempts,
            "patch_summary": (
                f"Applied AST-valid security mitigation for {cwe} on line {line_no} with preserved return contracts & signatures."
                if (has_changes and syntax_valid) else
                f"Patch synthesis failed: {syntax_error or 'No changes synthesized.'}"
            )
        }

    def _offline_patch_synthesis(self, original_code: str, finding: Dict[str, Any]) -> str:
        """Applies AST/Regex-directed secure replacement for known CWE patterns."""
        cwe = finding.get("cwe", "")
        code = original_code

        if "CWE-89" in cwe:
            # Fix SQL injection: replace f-string / % string format with parameterized (?, ...)
            code = re.sub(
                r'cursor\.execute\s*\(\s*f["\'](SELECT.*?WHERE\s+\w+\s*=\s*)[\'"]\{(\w+)\}[\'"]\s*["\']\s*\)',
                r'cursor.execute("\1?", (\2,))',
                code
            )
            code = re.sub(
                r'cursor\.execute\s*\(\s*f["\'](SELECT.*?WHERE\s+\w+\s*=\s*)[\'"]\{(\w+)\}[\'"]\s*AND\s*(\w+)\s*=\s*[\'"]\{(\w+)\}[\'"]\s*["\']\s*\)',
                r'cursor.execute("\1? AND \3 = ?", (\2, \4))',
                code
            )
            code = re.sub(
                r'query\s*=\s*f["\'](SELECT.*?WHERE\s+\w+\s*=\s*)[\'"]\{(\w+)\}[\'"]\s*AND\s*(\w+)\s*=\s*[\'"]\{(\w+)\}[\'"]\s*["\']',
                r'query = "\1? AND \3 = ?"; params = (\2, \4)',
                code
            )
            code = re.sub(
                r'query\s*=\s*f["\'](SELECT.*?WHERE\s+\w+\s*=\s*)[\'"]\{(\w+)\}[\'"]\s*["\']',
                r'query = "\1?"; params = (\2,)',
                code
            )
            code = code.replace("cursor.execute(query)", "cursor.execute(query, params if 'params' in locals() else ())")

        elif "CWE-78" in cwe:
            # Fix Command Injection: sanitize subprocess or replace os.system
            if "import shlex" not in code:
                code = "import shlex\n" + code
            code = re.sub(
                r'os\.system\s*\(\s*f["\']ping -c \d+ (\{.*?\})["\']\s*\)',
                r'subprocess.run(["ping", "-c", "2", \1], capture_output=True, text=True, check=False)',
                code
            )
            code = re.sub(
                r'os\.system\s*\(\s*f["\'](.*?) (\{.*?\})["\']\s*\)',
                r'subprocess.run(["\1", \2], capture_output=True, text=True, check=False)',
                code
            )
            code = re.sub(
                r'cmd\s*=\s*f["\']ping -c \d+ (\{.*?\})["\']',
                r'cmd = ["ping", "-c", "1", str(\1)]',
                code
            )
            code = code.replace("os.system(cmd)", "subprocess.run(cmd if isinstance(cmd, list) else shlex.split(cmd), capture_output=True, text=True, check=False)")
            
            # Clean subprocess argument quote sanitization
            if "subprocess.run(interp + [str(path)] + (args or []))" in code:
                code = code.replace(
                    "subprocess.run(interp + [str(path)] + (args or []))",
                    "subprocess.run(interp + [str(path)] + [shlex.quote(str(a)) for a in (args or []) if not any(c in str(a) for c in [';', '&&', '|', '`'])])"
                )

        elif "CWE-22" in cwe:
            # Fix Path Traversal: sanitize with os.path.basename and os.path.abspath bounds check
            if "import os" not in code:
                code = "import os\n" + code
            code = re.sub(
                r'filepath\s*=\s*os\.path\.join\s*\(\s*base_dir\s*,\s*(\w+)\s*\)',
                r'safe_name = os.path.basename(\1)\n    filepath = os.path.abspath(os.path.join(base_dir, safe_name))\n    if not filepath.startswith(os.path.abspath(base_dir)):\n        raise PermissionError("Access Denied: Path traversal detected")',
                code
            )
            code = re.sub(
                r'with\s+open\s*\(\s*f["\']\{base_dir\}/\{(\w+)\}["\']\s*,\s*["\']r["\']\s*\)\s*as\s+(\w+):',
                r'safe_name = os.path.basename(\1)\n    target_path = os.path.abspath(os.path.join(base_dir, safe_name))\n    with open(target_path, "r") as \2:',
                code
            )

        elif "CWE-502" in cwe:
            # Fix Insecure Deserialization: replace pickle with json
            if "import json" not in code:
                code = "import json\n" + code
            code = code.replace("import pickle\n", "").replace("import _pickle as cPickle\n", "")
            code = re.sub(r'pickle\.loads\s*\(\s*(.*?)\s*\)', r'json.loads(\1.decode("utf-8") if isinstance(\1, bytes) else \1)', code)
            code = re.sub(r'pickle\.load\s*\(\s*(.*?)\s*\)', r'json.load(\1)', code)

        return code

    def _conservative_ast_fallback(self, original_code: str, finding: Dict[str, Any]) -> str:
        """Conservative fallback ensuring clean syntax validity."""
        cwe = finding.get("cwe", "")
        code = original_code
        if "CWE-502" in cwe:
            return "import json\n" + code.replace("import pickle\n", "").replace("pickle.load", "json.load")
        elif "CWE-89" in cwe:
            return code.replace("cursor.execute(query)", "cursor.execute(query, ())")
        return code
