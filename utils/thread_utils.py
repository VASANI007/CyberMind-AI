"""
CyberMind AI

Thread & Concurrency Utilities
Ensures safe Windows COM cleanup and attaches Streamlit ScriptRunContext to worker threads.
"""

from __future__ import annotations

import gc
import threading
from typing import Any, Callable


def get_current_st_context():
    """
    Safely retrieves the active Streamlit ScriptRunContext if running inside Streamlit.
    """
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        return get_script_run_ctx()
    except Exception:
        return None


def wrap_thread_task(fn: Callable[..., Any], ctx: Any = None) -> Callable[..., Any]:
    """
    Wraps a callable for execution in ThreadPoolExecutor or threading.Thread:
    1. Attaches Streamlit ScriptRunContext to avoid missing context warnings.
    2. Initializes and uninitializes Windows COM (CoInitialize/CoUninitialize) to
       prevent "Win32 exception occurred releasing IUnknown" errors upon thread exit.
    3. Runs explicit garbage collection before COM uninitialization.
    """
    def _wrapped(*args: Any, **kwargs: Any) -> Any:
        if ctx is not None:
            try:
                from streamlit.runtime.scriptrunner import add_script_run_ctx
                add_script_run_ctx(threading.current_thread(), ctx)
            except Exception:
                pass

        has_com = False
        try:
            import pythoncom
            pythoncom.CoInitialize()
            has_com = True
        except Exception:
            pass

        try:
            return fn(*args, **kwargs)
        finally:
            if has_com:
                try:
                    gc.collect()
                    import pythoncom
                    pythoncom.CoUninitialize()
                except Exception:
                    pass

    return _wrapped
