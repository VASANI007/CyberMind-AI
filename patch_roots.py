"""Patch all *_root.py files to add sys.path fix for direct execution."""
import os
import re

files = [
    r"apis\apis_root.py",
    r"data\data_root.py",
    r"ml\ml_root.py",
    r"modules\modules_root.py",
    r"schemas\schemas_root.py",
    r"services\services_root.py",
    r"tests\tests_root.py",
    r"utils\util_root.py",
]

patch = '''
import sys
import os

# Ensure the project root is on sys.path when running this file directly
_project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)
'''

for rel_path in files:
    with open(rel_path, "r", encoding="utf-8") as f:
        content = f.read()

    if "_project_root" in content:
        print(f"SKIP (already patched): {rel_path}")
        continue

    # Insert after 'from __future__ import annotations'
    new_content = re.sub(
        r"(from __future__ import annotations\s*\n)",
        r"\1" + patch + "\n",
        content,
        count=1
    )

    with open(rel_path, "w", encoding="utf-8") as f:
        f.write(new_content)

    print(f"PATCHED: {rel_path}")

print("Done.")
