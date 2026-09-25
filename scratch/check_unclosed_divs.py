with open("app.py", "r", encoding="utf-8") as f:
    text = f.read()

import re

# find all st.markdown calls
matches = re.finditer(r'st\.markdown\(\s*(["\']{1,3})(.*?)\1', text, re.DOTALL)
for m in matches:
    content = m.group(2)
    open_c = content.count("<div")
    close_c = content.count("</div")
    if open_c != close_c and open_c > 0:
        # find line number
        line_no = text[:m.start()].count("\n") + 1
        print(f"Line {line_no}: open={open_c}, close={close_c}: {content.strip()[:60]}")
