import unittest
import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from modules.autonomous_crs.code_scanner import CodeSecurityScanner
from modules.autonomous_crs.reasoning_agent import CyberReasoningAgent
from modules.autonomous_crs.dynamic_sandbox import DynamicSandbox
from modules.autonomous_crs.fuzzing_engine import FuzzingEngine
from modules.autonomous_crs.vulnerability_reproducer import VulnerabilityReproducer
from modules.autonomous_crs.patch_engineer import PatchEngineer
from modules.autonomous_crs.regression_harness import RegressionHarness
from modules.autonomous_crs.verification_engine import FixVerificationEngine
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator


class TestAutonomousCRSEngine(unittest.TestCase):

    def setUp(self):
        self.orchestrator = AutonomousCRSOrchestrator(use_offline_mode=True)
        self.scanner = CodeSecurityScanner()

    def test_01_static_scanner_sqli(self):
        code = '''
def login(user):
    query = f"SELECT * FROM users WHERE username = '{user}'"
    cursor.execute(query)
'''
        res = self.scanner.scan_code_string(code)
        self.assertGreater(res["total_findings"], 0)
        self.assertEqual(res["findings"][0]["cwe"], "CWE-89")

    def test_02_static_scanner_command_injection(self):
        code = '''
import os
def ping(host):
    os.system(f"ping -c 2 {host}")
'''
        res = self.scanner.scan_code_string(code)
        self.assertGreater(res["total_findings"], 0)
        self.assertEqual(res["findings"][0]["cwe"], "CWE-78")

    def test_03_sandbox_execution(self):
        sandbox = DynamicSandbox()
        code = 'print("SANDBOX_TEST_OK")'
        res = sandbox.execute_code(code)
        self.assertTrue(res["success"])
        self.assertIn("SANDBOX_TEST_OK", res["stdout"])

    def test_04_full_pipeline_orchestration(self):
        sample_code = '''
def get_user_data(username):
    query = f"SELECT * FROM accounts WHERE user = '{username}'"
    cursor.execute(query)
'''
        pipeline_res = self.orchestrator.run_pipeline(sample_code, filename="accounts_gateway.py")
        self.assertTrue(pipeline_res["success"])
        self.assertTrue(pipeline_res["has_vulnerabilities"])
        self.assertIn("findings", pipeline_res)
        if not pipeline_res["verification"]["verified"]:
            print("\nDEBUG MATRIX:", pipeline_res["verification"]["matrix"])
            print("DEBUG DIFF:\n", pipeline_res["patch"]["diff"])
        self.assertTrue(pipeline_res["verification"]["verified"], msg=str(pipeline_res["verification"]["matrix"]))
        self.assertIn("FIX VERIFIED", pipeline_res["verification"]["badge_text"])
        self.assertGreater(len(pipeline_res["evidence_zip_bytes"]), 100)


    def test_05_llm_router_policy(self):
        from modules.autonomous_crs.llm_router import llm_router
        self.assertEqual(llm_router.AGENT_ROUTING_POLICY["reasoning"][0], "GROQ")
        self.assertEqual(llm_router.AGENT_ROUTING_POLICY["static_analysis"][0], "GEMINI")
        self.assertEqual(llm_router.AGENT_ROUTING_POLICY["fuzzing"][0], "GROQ")
        
        # Test fallback behavior with dummy offline query
        res = llm_router.query([{"role": "user", "content": "hello"}], task_type="reasoning")
        self.assertIn("provider_used", res)


if __name__ == "__main__":
    unittest.main()
