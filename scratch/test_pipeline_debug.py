import os
import sys
sys.path.insert(0, os.getcwd())
from modules.autonomous_crs.orchestrator import AutonomousCRSOrchestrator

sample_code = '''
def get_user_data(username):
    query = f"SELECT * FROM accounts WHERE user = '{username}'"
    cursor.execute(query)
'''

orch = AutonomousCRSOrchestrator(use_offline_mode=True)
pipeline_res = orch.run_pipeline(sample_code, filename="accounts_gateway.py")
print("Verified:", pipeline_res["verification"]["verified"])
print("Matrix:", pipeline_res["verification"]["matrix"])
print("Regression Sandbox Output:", pipeline_res["regression"]["sandbox_output"])
print("Refuzz crashes:", pipeline_res["regression"]["refuzz_crashes"])
