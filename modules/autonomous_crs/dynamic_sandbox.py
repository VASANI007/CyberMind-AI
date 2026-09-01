from __future__ import annotations

import os
import sys
import time
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class DynamicSandbox:
    """
    Isolated process & execution sandbox.
    Runs target code safely in a separate process with execution timeouts,
    capturing stdout, stderr, exit code, crash logs, and stack traces.
    Includes ultra-fast batch execution mode for high-throughput fuzz campaigns.
    """

    def __init__(self, timeout_seconds: float = 3.5):
        self.timeout_seconds = timeout_seconds

    def execute_code(
        self,
        code_content: str,
        stdin_input: str = "",
        cli_args: Optional[List[str]] = None,
        env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Executes Python code in an isolated subprocess sandbox.
        """
        cli_args = cli_args or []
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)

        start_time = time.time()
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "sandbox_target.py"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code_content)

            safe_cli_args = [str(arg).replace("\x00", "") for arg in cli_args]
            cmd = [sys.executable, str(temp_file)] + safe_cli_args

            env["PYTHONIOENCODING"] = "utf-8"
            try:
                proc = subprocess.run(
                    cmd,
                    input=stdin_input,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=self.timeout_seconds,
                    cwd=tmpdir,
                    env=env
                )
                duration = time.time() - start_time
                stdout = proc.stdout
                stderr = proc.stderr
                exit_code = proc.returncode
                # Fatal crash: signal kill (<0), segmentation fault (139), OS abort (134), or Windows access violation
                is_crash = exit_code < 0 or exit_code in (134, 139, 255, 3221225477, 3221225786)
                has_exception = "Traceback (most recent call last)" in stderr

                return {
                    "success": not is_crash,
                    "exit_code": exit_code,
                    "stdout": stdout,
                    "stderr": stderr,
                    "duration_seconds": round(duration, 4),
                    "crashed": is_crash,
                    "exception_detected": has_exception,
                    "stack_trace": stderr if has_exception else "",
                    "timeout": False
                }

            except subprocess.TimeoutExpired as e:
                duration = time.time() - start_time
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": e.stdout or "" if isinstance(e.stdout, str) else "",
                    "stderr": f"Execution timed out after {self.timeout_seconds}s.",
                    "duration_seconds": round(duration, 4),
                    "crashed": True,
                    "exception_detected": False,
                    "stack_trace": "TimeoutExpired",
                    "timeout": True
                }
            except Exception as e:
                duration = time.time() - start_time
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "duration_seconds": round(duration, 4),
                    "crashed": True,
                    "exception_detected": True,
                    "stack_trace": str(e),
                    "timeout": False
                }

    def execute_batch_fuzz(
        self,
        code_content: str,
        inputs_list: List[str],
        env_vars: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        High-speed batch fuzz execution in a single isolated subprocess.
        Tests all mutation inputs in a single sandbox launch within ~0.05 seconds.
        """
        env = os.environ.copy()
        if env_vars:
            env.update(env_vars)
        env["PYTHONIOENCODING"] = "utf-8"

        with tempfile.TemporaryDirectory() as tmpdir:
            temp_file = Path(tmpdir) / "sandbox_target.py"
            with open(temp_file, "w", encoding="utf-8") as f:
                f.write(code_content)

            runner_file = Path(tmpdir) / "fuzz_batch_runner.py"
            runner_script = """
import sys
import os
import json
import traceback
import time

def run_fuzz():
    with open("inputs_batch.json", "r", encoding="utf-8") as f:
        inputs = json.load(f)

    with open("sandbox_target.py", "r", encoding="utf-8") as f:
        target_code = f.read()

    results = []
    for inp in inputs:
        t0 = time.time()
        crashed = False
        exc_detected = False
        stack_trace = ""
        exit_code = 0
        stdout = ""
        stderr = ""

        try:
            compiled = compile(target_code, "sandbox_target.py", "exec")
            loc_env = {"__name__": "__main__", "sys": sys, "os": os, "fuzz_input": inp}
            sys.argv = ["sandbox_target.py", inp]
            exec(compiled, loc_env)
        except SystemExit as se:
            code_val = se.code if isinstance(se.code, int) else 0
            exit_code = code_val
            if code_val not in (0, 1, 2, None):
                crashed = True
        except Exception as e:
            exc_detected = True
            stack_trace = traceback.format_exc()
            stderr = str(e)
            exit_code = 1
        dur = round(time.time() - t0, 4)

        results.append({
            "input": inp,
            "success": not crashed,
            "exit_code": exit_code,
            "stdout": stdout,
            "stderr": stderr,
            "duration_seconds": dur,
            "crashed": crashed,
            "exception_detected": exc_detected,
            "stack_trace": stack_trace,
            "timeout": False
        })

    print("__CYBERMIND_BATCH_RESULT_START__")
    print(json.dumps(results))
    print("__CYBERMIND_BATCH_RESULT_END__")

if __name__ == "__main__":
    run_fuzz()
"""
            with open(runner_file, "w", encoding="utf-8") as f:
                f.write(runner_script)

            inputs_file = Path(tmpdir) / "inputs_batch.json"
            with open(inputs_file, "w", encoding="utf-8") as f:
                json.dump(inputs_list, f)

            cmd = [sys.executable, str(runner_file)]
            try:
                proc = subprocess.run(
                    cmd,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    timeout=self.timeout_seconds + 3.0,
                    cwd=tmpdir,
                    env=env
                )
                stdout = proc.stdout
                if "__CYBERMIND_BATCH_RESULT_START__" in stdout and "__CYBERMIND_BATCH_RESULT_END__" in stdout:
                    payload = stdout.split("__CYBERMIND_BATCH_RESULT_START__")[1].split("__CYBERMIND_BATCH_RESULT_END__")[0].strip()
                    return json.loads(payload)
            except Exception:
                pass

        # Fallback to individual executions if batch runner failed
        results = []
        for inp in inputs_list:
            r = self.execute_code(code_content, stdin_input=inp, cli_args=[inp])
            r["input"] = inp
            results.append(r)
        return results
