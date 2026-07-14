"""
CyberMind AI - Master Execution Orchestrator
Enterprise Production Version
"""

from __future__ import annotations

import io
import os
import sys
import time
import logging
import traceback

# ── UTF-8 on Windows terminal ──────────────────────────────────────────────
if sys.platform.startswith("win"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# ── Suppress Streamlit bare-mode warnings ──────────────────────────────────
class _NoStreamlitBare(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return (
            "ScriptRunContext" not in msg
            and "Session state does not function" not in msg
        )

for _n in (
    "streamlit.runtime.scriptrunner_utils.script_run_context",
    "streamlit.runtime.state.session_state_proxy",
):
    logging.getLogger(_n).addFilter(_NoStreamlitBare())

# ── Silence noisy INFO logs from all sub-modules while root runs ───────────
logging.getLogger().setLevel(logging.WARNING)


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"
MAGENTA = "\033[95m"

WIDTH  = 72


def banner(title: str, color: str = MAGENTA) -> None:
    print(f"\n{color}{'═' * WIDTH}")
    print(f"  {title}")
    print(f"{'═' * WIDTH}{RESET}")


def section(title: str) -> None:
    print(f"\n{CYAN}{BOLD}── {title} {'─' * (WIDTH - len(title) - 4)}{RESET}")


def ok(label: str, note: str = "Done") -> None:
    print(f"  {GREEN}✔{RESET}  {label:<40} {GREEN}{note}{RESET}")


def fail(label: str, error: str) -> None:
    print(f"  {RED}✘{RESET}  {label:<40} {RED}FAILED{RESET}")
    # Indent each error line
    for line in error.strip().splitlines():
        print(f"       {DIM}{line}{RESET}")


def warn(label: str, note: str) -> None:
    print(f"  {YELLOW}⚠{RESET}  {label:<40} {YELLOW}{note}{RESET}")


def skip(label: str, note: str = "Skipped") -> None:
    print(f"  {DIM}–{RESET}  {label:<40} {DIM}{note}{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 0 — Header
# ══════════════════════════════════════════════════════════════════════════════

banner("🛡️  CyberMind AI  —  Master Orchestrator  🛡️")
print(f"  {DIM}Started at {time.strftime('%Y-%m-%d %H:%M:%S')}{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 1 — Import every *_root module and report individually
# ══════════════════════════════════════════════════════════════════════════════

section("PHASE 1 — Loading All Modules")

_IMPORTS = [
    ("config_root",    "config.config_root",    "config_root"),
    ("core_root",      "core.core_root",         "core_root"),
    ("util_root",      "utils.util_root",        "util_root"),
    ("data_root",      "data.data_root",          "data_root"),
    ("database_root",  "database.database_root",  "database_root"),
    ("schemas_root",   "schemas.schemas_root",    "schemas_root"),
    ("ml_root",        "ml.ml_root",              "ml_root"),
    ("services_root",  "services.services_root",  "services_root"),
    ("modules_root",   "modules.modules_root",    "modules_root"),
    ("apis_root",      "apis.apis_root",          "apis_root"),
    ("tests_root",     "tests.tests_root",        "tests_root"),
]

_loaded   : dict = {}   # name → object
_load_err : dict = {}   # name → error string

for _var, _module, _attr in _IMPORTS:
    _label = f"{_module}"
    try:
        import importlib
        _mod = importlib.import_module(_module)
        _obj = getattr(_mod, _attr)
        _loaded[_var] = _obj
        ok(_label)
    except Exception as _e:
        _tb = traceback.format_exc()
        _load_err[_var] = _tb
        fail(_label, _tb)

if _load_err:
    print(f"\n{RED}{BOLD}  ✘  {len(_load_err)} module(s) failed to load. See errors above.{RESET}")
else:
    print(f"\n{GREEN}{BOLD}  ✔  All {len(_loaded)} modules loaded successfully.{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 2 — Initialize every manager
# ══════════════════════════════════════════════════════════════════════════════

section("PHASE 2 — Initializing All Managers")

# Exclude tests_root from initialization list (it's run in Phase 4)
_MANAGERS = [k for k in _loaded if k != "tests_root"]

_init_err: dict = {}

for _key in _MANAGERS:
    _mgr   = _loaded[_key]
    _label = f"{_key}"
    if not hasattr(_mgr, "initialize"):
        skip(_label, "no initialize()")
        continue
    try:
        _t0 = time.perf_counter()
        _mgr.initialize()
        _ms = int((time.perf_counter() - _t0) * 1000)
        ok(_label, f"Done  ({_ms} ms)")
    except Exception as _e:
        _tb = traceback.format_exc()
        _init_err[_key] = _tb
        fail(_label, _tb)

if _init_err:
    print(f"\n{RED}{BOLD}  ✘  {len(_init_err)} manager(s) failed to initialize.{RESET}")
else:
    print(f"\n{GREEN}{BOLD}  ✔  All managers initialized successfully.{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 3 — Health checks
# ══════════════════════════════════════════════════════════════════════════════

section("PHASE 3 — Health Checks")

_health_results : dict = {}
_health_err     : dict = {}

for _key in _MANAGERS:
    _mgr   = _loaded[_key]
    _label = f"{_key}"
    if not hasattr(_mgr, "health_check"):
        skip(_label, "no health_check()")
        _health_results[_key] = "Unknown"
        continue
    try:
        _h = _mgr.health_check()
        _status = _h.get("status", "Unknown") if isinstance(_h, dict) else str(_h)
        _health_results[_key] = _status
        if _status == "Healthy":
            ok(_label, "Healthy")
        else:
            _detail = str(_h)
            fail(_label, f"Status = {_status}\n{_detail}")
            _health_err[_key] = _detail
    except Exception as _e:
        _tb = traceback.format_exc()
        _health_err[_key] = _tb
        _health_results[_key] = "Error"
        fail(_label, _tb)


# ── Health summary table ───────────────────────────────────────────────────
print(f"\n  {'Module':<30} {'Status':<12} {'Note'}")
print(f"  {'─'*30} {'─'*12} {'─'*20}")
_all_healthy = True
for _key, _status in _health_results.items():
    if _status == "Healthy":
        _icon  = f"{GREEN}✔{RESET}"
        _color = GREEN
    elif _status == "Unknown":
        _icon  = f"{YELLOW}?{RESET}"
        _color = YELLOW
    else:
        _icon  = f"{RED}✘{RESET}"
        _color = RED
        _all_healthy = False
    _err_note = " ← see error above" if _key in _health_err else ""
    print(f"  {_icon}  {_key:<28} {_color}{_status:<12}{RESET}{DIM}{_err_note}{RESET}")

print()
if _all_healthy and not _health_err:
    print(f"{GREEN}{BOLD}  ✔  All components are Healthy.{RESET}")
else:
    print(f"{RED}{BOLD}  ✘  {len(_health_err)} component(s) are unhealthy.{RESET}")


# ══════════════════════════════════════════════════════════════════════════════
#  Early exit if any critical phase failed
# ══════════════════════════════════════════════════════════════════════════════

_critical_failures = {**_load_err, **_init_err, **_health_err}

if _critical_failures:
    banner("⚠  System NOT fully operational — fix errors above", RED)
    print(f"\n{RED}  Failed components ({len(_critical_failures)}):{RESET}")
    for _k in _critical_failures:
        print(f"    {RED}✘  {_k}{RESET}")
    print()
    sys.exit(1)


# ══════════════════════════════════════════════════════════════════════════════
#  PHASE 4 — Run test suite
# ══════════════════════════════════════════════════════════════════════════════

section("PHASE 4 — Running Test Suite")

if "tests_root" not in _loaded:
    print(f"  {YELLOW}⚠  tests_root not loaded — skipping tests.{RESET}")
    _exit_code = 0
else:
    _tr = _loaded["tests_root"]
    try:
        _tr.initialize()
        _exit_code = _tr.run_tests(quiet=False)
    except Exception as _e:
        fail("tests_root.run_tests", traceback.format_exc())
        _exit_code = 1


# ══════════════════════════════════════════════════════════════════════════════
#  Final summary
# ══════════════════════════════════════════════════════════════════════════════

if _exit_code == 0:
    banner("✔  CyberMind AI  —  ALL SYSTEMS OPERATIONAL  [ SUCCESS ]", GREEN)
    print(f"  {GREEN}Modules loaded   : {len(_loaded)}{RESET}")
    print(f"  {GREEN}Managers init'd  : {len(_MANAGERS)}{RESET}")
    print(f"  {GREEN}Health checks    : all Healthy{RESET}")
    print(f"  {GREEN}Tests            : PASSED{RESET}")
else:
    banner("✘  CyberMind AI  —  ORCHESTRATION FAILED  [ FAILURE ]", RED)
    if _load_err:
        print(f"  {RED}Load errors      : {len(_load_err)}{RESET}")
    if _init_err:
        print(f"  {RED}Init errors      : {len(_init_err)}{RESET}")
    if _health_err:
        print(f"  {RED}Health failures  : {len(_health_err)}{RESET}")
    print(f"  {RED}Test exit code   : {_exit_code}{RESET}")

print()
sys.exit(_exit_code)
