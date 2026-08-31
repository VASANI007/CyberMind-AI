from __future__ import annotations

import os
import sys
import time
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class DynamicSandbox:
    """
    Isolated process & execution sandbox.
    Runs target code safely in a separate process with execution timeouts,
    capturing stdout, stderr, exit code, crash logs, and stack traces.
    """

    def __init__(self, timeout_seconds: float = 4.0):
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

            cmd = [sys.executable, str(temp_file)] + cli_args

            try:
                proc = subprocess.run(
                    cmd,
                    input=stdin_input,
                    text=True,
                    capture_output=True,
                    timeout=self.timeout_seconds,
                    cwd=tmpdir,
                    env=env
                )
                duration = time.time() - start_time
                stdout = proc.stdout
                stderr = proc.stderr
                exit_code = proc.returncode

                is_crash = exit_code != 0
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
