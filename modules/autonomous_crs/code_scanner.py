from __future__ import annotations

import ast
import os
import re
import zipfile
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class CodeSecurityScanner:
    """
    Static Application Security Testing (SAST) & AST-based vulnerability scanner.
    Analyzes Python source code, extracts syntax trees, and pinpoints vulnerabilities
    with line numbers, code snippets, CWE, and OWASP mappings.
    """

    def __init__(self):
        self.rules = self._load_rules()

    def _load_rules(self) -> List[Dict[str, Any]]:
        return [
            {
                "id": "CWE-89",
                "name": "SQL Injection",
                "cwe": "CWE-89",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "confidence": 0.95,
                "description": "User input concatenated directly into SQL query without parameterization.",
                "mitre": "T1190 - Exploit Public-Facing Application"
            },
            {
                "id": "CWE-78",
                "name": "Command Injection",
                "cwe": "CWE-78",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "confidence": 0.94,
                "description": "Execution of dynamic shell command using user-supplied input.",
                "mitre": "T1059 - Command and Scripting Interpreter"
            },
            {
                "id": "CWE-22",
                "name": "Path Traversal (Arbitrary File Read/Write)",
                "cwe": "CWE-22",
                "owasp": "A01:2021-Broken Access Control",
                "severity": "HIGH",
                "confidence": 0.90,
                "description": "File access path constructed directly from unvalidated user input.",
                "mitre": "T1005 - Data from Local System"
            },
            {
                "id": "CWE-502",
                "name": "Insecure Deserialization",
                "cwe": "CWE-502",
                "owasp": "A08:2021-Software and Data Integrity Failures",
                "severity": "CRITICAL",
                "confidence": 0.96,
                "description": "Deserializing untrusted data with pickle or unsafe yaml loader.",
                "mitre": "T1203 - Exploitation for Client Execution"
            },
            {
                "id": "CWE-95",
                "name": "Improper Neutralization of Directives in Dynamically Evaluated Code (Eval Injection)",
                "cwe": "CWE-95",
                "owasp": "A03:2021-Injection",
                "severity": "CRITICAL",
                "confidence": 0.93,
                "description": "Dynamic execution using eval() or exec() with untrusted inputs.",
                "mitre": "T1059 - Command Execution"
            },
            {
                "id": "CWE-798",
                "name": "Hardcoded Credentials / API Keys",
                "cwe": "CWE-798",
                "owasp": "A07:2021-Identification and Authentication Failures",
                "severity": "MEDIUM",
                "confidence": 0.88,
                "description": "Hardcoded secret, password or private key in source code.",
                "mitre": "T1552 - Unsecured Credentials"
            },
            {
                "id": "CWE-327",
                "name": "Use of Broken or Risky Cryptographic Algorithm",
                "cwe": "CWE-327",
                "owasp": "A02:2021-Cryptographic Failures",
                "severity": "LOW",
                "confidence": 0.91,
                "description": "Use of obsolete or cryptographically broken hash algorithms (MD5/SHA1).",
                "mitre": "T1600 - Weaken Encryption"
            },
        ]

    def scan_code_string(self, code: str, filename: str = "target_code.py") -> Dict[str, Any]:
        """Scans a raw Python code string and returns detailed findings."""
        findings = []
        lines = code.splitlines()

        try:
            tree = ast.parse(code, filename=filename)
            findings.extend(self._ast_scan(tree, lines, filename))
        except SyntaxError as e:
            findings.append({
                "id": "SYNTAX-ERROR",
                "name": "Python Syntax Error",
                "cwe": "CWE-N/A",
                "owasp": "N/A",
                "severity": "INFO",
                "confidence": 1.0,
                "file": filename,
                "line": e.lineno or 1,
                "code_snippet": lines[e.lineno - 1] if e.lineno and e.lineno <= len(lines) else "",
                "description": f"Syntax error preventing full AST parse: {e.msg}",
                "mitre": "N/A",
                "rule_id": "SYNTAX-01"
            })

        # Regex fallback / supplementary checks (e.g. hardcoded secrets, SQL keywords in strings)
        findings.extend(self._regex_scan(code, lines, filename))

        # Deduplicate findings by (file, line, cwe)
        unique_findings = []
        seen = set()
        for f in findings:
            key = (f["file"], f["line"], f["cwe"])
            if key not in seen:
                seen.add(key)
                unique_findings.append(f)

        # Sort findings by severity
        severity_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        unique_findings.sort(key=lambda x: severity_weight.get(x["severity"], 0), reverse=True)

        summary = {
            "total_findings": len(unique_findings),
            "critical": sum(1 for f in unique_findings if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in unique_findings if f["severity"] == "HIGH"),
            "medium": sum(1 for f in unique_findings if f["severity"] == "MEDIUM"),
            "low": sum(1 for f in unique_findings if f["severity"] == "LOW"),
            "target": filename,
            "findings": unique_findings,
            "code_lines_count": len(lines)
        }
        return summary

    def _ast_scan(self, tree: ast.AST, lines: List[str], filename: str) -> List[Dict[str, Any]]:
        findings = []
        # Track variables assigned dynamic SQL or command strings
        tainted_vars = {}

        for node in ast.walk(tree):
            # Track variable assignments with SQL strings
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        # Check if assigned value is an f-string or % or + with SQL terms
                        is_dynamic = isinstance(node.value, (ast.JoinedStr, ast.BinOp))
                        val_repr = ast.unparse(node.value).upper() if hasattr(ast, "unparse") else ""
                        has_sql_kw = any(kw in val_repr for kw in ["SELECT ", "INSERT ", "UPDATE ", "DELETE ", "FROM ", "WHERE "])
                        if is_dynamic and has_sql_kw:
                            tainted_vars[var_name] = getattr(node, "lineno", 1)

            # 1. Detect os.system, subprocess calls, execute calls
            if isinstance(node, ast.Call):
                func_name = self._get_call_func_name(node.func)
                
                # Command Injection
                if func_name in ("os.system", "os.popen", "subprocess.call", "subprocess.Popen", "subprocess.run"):
                    is_shell_true = any(
                        kw.arg == "shell" and getattr(kw.value, "value", None) is True
                        for kw in node.keywords
                    )
                    has_format_or_binop = any(
                        isinstance(arg, (ast.BinOp, ast.JoinedStr)) for arg in node.args
                    )
                    has_tainted_arg = any(
                        isinstance(arg, ast.Name) and arg.id in tainted_vars for arg in node.args
                    )
                    if is_shell_true or has_format_or_binop or has_tainted_arg or func_name in ("os.system", "os.popen"):
                        lineno = getattr(node, "lineno", 1)
                        snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                        findings.append({
                            "id": "CWE-78",
                            "name": "Command Injection Vulnerability",
                            "cwe": "CWE-78",
                            "owasp": "A03:2021-Injection",
                            "severity": "CRITICAL",
                            "confidence": 0.96,
                            "file": filename,
                            "line": lineno,
                            "code_snippet": snippet.strip(),
                            "description": f"Dangerous command execution via `{func_name}` with dynamically composed command string.",
                            "mitre": "T1059 - Command and Scripting Interpreter",
                            "rule_id": "BANDIT-B602"
                        })

                # SQL Injection (cursor.execute with formatting or tainted variable)
                elif func_name.endswith(".execute") or func_name.endswith(".executemany") or func_name == "execute":
                    if node.args:
                        first_arg = node.args[0]
                        is_dynamic_first = isinstance(first_arg, (ast.JoinedStr, ast.BinOp))
                        is_tainted_var = isinstance(first_arg, ast.Name) and first_arg.id in tainted_vars
                        if is_dynamic_first or is_tainted_var:
                            lineno = tainted_vars.get(first_arg.id) if is_tainted_var else getattr(node, "lineno", 1)
                            snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                            findings.append({
                                "id": "CWE-89",
                                "name": "SQL Injection (Unparameterized Query)",
                                "cwe": "CWE-89",
                                "owasp": "A03:2021-Injection",
                                "severity": "CRITICAL",
                                "confidence": 0.97,
                                "file": filename,
                                "line": lineno,
                                "code_snippet": snippet.strip(),
                                "description": f"SQL query constructed dynamically via string formatting in `{func_name}()`. Use parameterized queries.",
                                "mitre": "T1190 - Exploit Public-Facing Application",
                                "rule_id": "SEMGREP-PY-SQLI"
                            })

                # Insecure Deserialization (pickle.loads, pickle.load)
                elif func_name in ("pickle.loads", "pickle.load", "_pickle.loads", "_pickle.load"):
                    lineno = getattr(node, "lineno", 1)
                    snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                    findings.append({
                        "id": "CWE-502",
                        "name": "Insecure Deserialization (Pickle)",
                        "cwe": "CWE-502",
                        "owasp": "A08:2021-Software and Data Integrity Failures",
                        "severity": "CRITICAL",
                        "confidence": 0.98,
                        "file": filename,
                        "line": lineno,
                        "code_snippet": snippet.strip(),
                        "description": f"Untrusted data deserialized using `{func_name}` allows arbitrary code execution.",
                        "mitre": "T1203 - Exploitation for Client Execution",
                        "rule_id": "BANDIT-B301"
                    })

                # Code Injection (eval, exec)
                elif func_name in ("eval", "exec"):
                    lineno = getattr(node, "lineno", 1)
                    snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                    findings.append({
                        "id": "CWE-95",
                        "name": "Code Injection (eval/exec)",
                        "cwe": "CWE-95",
                        "owasp": "A03:2021-Injection",
                        "severity": "CRITICAL",
                        "confidence": 0.94,
                        "file": filename,
                        "line": lineno,
                        "code_snippet": snippet.strip(),
                        "description": f"Direct invocation of `{func_name}()` evaluates arbitrary strings as Python code.",
                        "mitre": "T1059 - Command Execution",
                        "rule_id": "BANDIT-B102"
                    })

                # Insecure Crypto
                elif func_name in ("hashlib.md5", "hashlib.sha1", "Crypto.Hash.MD5"):
                    lineno = getattr(node, "lineno", 1)
                    snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                    findings.append({
                        "id": "CWE-327",
                        "name": "Broken Cryptographic Hash Algorithm",
                        "cwe": "CWE-327",
                        "owasp": "A02:2021-Cryptographic Failures",
                        "severity": "LOW",
                        "confidence": 0.90,
                        "file": filename,
                        "line": lineno,
                        "code_snippet": snippet.strip(),
                        "description": f"Weak hash algorithm `{func_name}` is vulnerable to collision attacks.",
                        "mitre": "T1600 - Weaken Encryption",
                        "rule_id": "BANDIT-B303"
                    })

                # Path Traversal in open()
                elif func_name in ("open", "io.open", "os.open"):
                    if node.args and isinstance(node.args[0], (ast.JoinedStr, ast.BinOp)):
                        lineno = getattr(node, "lineno", 1)
                        snippet = lines[lineno - 1] if lineno <= len(lines) else ""
                        findings.append({
                            "id": "CWE-22",
                            "name": "Path Traversal in File Access",
                            "cwe": "CWE-22",
                            "owasp": "A01:2021-Broken Access Control",
                            "severity": "HIGH",
                            "confidence": 0.89,
                            "file": filename,
                            "line": lineno,
                            "code_snippet": snippet.strip(),
                            "description": "Dynamic file path constructed without sanitization or path canonicalization.",
                            "mitre": "T1005 - Data from Local System",
                            "rule_id": "SEMGREP-PY-PATH-TRAVERSAL"
                        })

        return findings

    def _regex_scan(self, code: str, lines: List[str], filename: str) -> List[Dict[str, Any]]:
        findings = []

        # Hardcoded secrets regex
        secret_patterns = [
            (r'(?i)(api[_-]?key|secret|password|auth[_-]?token)\s*=\s*["\']([A-Za-z0-9_\-]{16,})["\']', "CWE-798", "Hardcoded API Key/Secret", "MEDIUM"),
            (r'-----BEGIN (RSA|EC|OPENSSH|DSA) PRIVATE KEY-----', "CWE-798", "Hardcoded Private Key", "HIGH"),
            (r'(?i)AWS_SECRET_ACCESS_KEY\s*=\s*["\'][A-Za-z0-9/+=]{40}["\']', "CWE-798", "Hardcoded AWS Secret Key", "HIGH")
        ]

        for pattern, cwe, name, severity in secret_patterns:
            for idx, line in enumerate(lines, 1):
                if re.search(pattern, line):
                    findings.append({
                        "id": cwe,
                        "name": name,
                        "cwe": cwe,
                        "owasp": "A07:2021-Identification and Authentication Failures",
                        "severity": severity,
                        "confidence": 0.92,
                        "file": filename,
                        "line": idx,
                        "code_snippet": line.strip(),
                        "description": f"Potential sensitive token or secret discovered in line {idx}.",
                        "mitre": "T1552 - Unsecured Credentials",
                        "rule_id": "RULE-SECRET-SCAN"
                    })

        return findings

    def _get_call_func_name(self, node: ast.AST) -> str:
        """Helper to extract dotted call function names (e.g. os.system, subprocess.Popen)"""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            val_name = self._get_call_func_name(node.value)
            if val_name:
                return f"{val_name}.{node.attr}"
            return node.attr
        return ""

    def scan_directory(self, dir_path: str) -> Dict[str, Any]:
        """Scans all Python files in a directory recursively."""
        path = Path(dir_path)
        all_findings = []
        scanned_files = 0

        for root, _, files in os.walk(path):
            for f in files:
                if f.endswith(".py"):
                    full_p = Path(root) / f
                    rel_p = str(full_p.relative_to(path))
                    try:
                        with open(full_p, "r", encoding="utf-8", errors="ignore") as file_handle:
                            code = file_handle.read()
                        res = self.scan_code_string(code, filename=rel_p)
                        all_findings.extend(res["findings"])
                        scanned_files += 1
                    except Exception:
                        pass

        severity_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        all_findings.sort(key=lambda x: severity_weight.get(x["severity"], 0), reverse=True)

        return {
            "total_findings": len(all_findings),
            "files_scanned": scanned_files,
            "critical": sum(1 for f in all_findings if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in all_findings if f["severity"] == "HIGH"),
            "medium": sum(1 for f in all_findings if f["severity"] == "MEDIUM"),
            "low": sum(1 for f in all_findings if f["severity"] == "LOW"),
            "findings": all_findings,
            "target": str(dir_path)
        }

    def scan_zip(self, zip_bytes: bytes) -> Dict[str, Any]:
        """Unpacks ZIP in a temporary directory and scans all Python files."""
        files_dict = {}
        all_findings = []
        scanned_files = 0

        with tempfile.TemporaryDirectory() as tmpdir:
            zip_path = Path(tmpdir) / "uploaded.zip"
            with open(zip_path, "wb") as f:
                f.write(zip_bytes)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(tmpdir)

            for root, _, files in os.walk(tmpdir):
                for f in files:
                    if f.endswith(".py"):
                        full_p = Path(root) / f
                        rel_p = str(full_p.relative_to(tmpdir)).replace("\\", "/")
                        try:
                            with open(full_p, "r", encoding="utf-8", errors="ignore") as file_handle:
                                code = file_handle.read()
                            files_dict[rel_p] = code
                            res = self.scan_code_string(code, filename=rel_p)
                            all_findings.extend(res["findings"])
                            scanned_files += 1
                        except Exception:
                            pass

        severity_weight = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1, "INFO": 0}
        all_findings.sort(key=lambda x: severity_weight.get(x["severity"], 0), reverse=True)

        return {
            "total_findings": len(all_findings),
            "files_scanned": scanned_files,
            "critical": sum(1 for f in all_findings if f["severity"] == "CRITICAL"),
            "high": sum(1 for f in all_findings if f["severity"] == "HIGH"),
            "medium": sum(1 for f in all_findings if f["severity"] == "MEDIUM"),
            "low": sum(1 for f in all_findings if f["severity"] == "LOW"),
            "findings": all_findings,
            "files_dict": files_dict,
            "target": "Uploaded Project Archive (.zip)"
        }

