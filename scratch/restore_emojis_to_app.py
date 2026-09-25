import difflib
import re
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8")

with open("app.py", "r", encoding="utf-8") as f:
    cur_lines = f.readlines()

orig_text = subprocess.check_output(
    ["git", "show", "HEAD:app.py"], text=True, encoding="utf-8", errors="replace"
)
orig_lines = orig_text.splitlines(keepends=True)

EMOJI_PATTERN = re.compile(
    r"[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff\u2b50\u25cf\u25b6\u25c0\ufe0f\u2713\u2714\u274c]"
)

matcher = difflib.SequenceMatcher(None, orig_lines, cur_lines)
restored_lines = list(cur_lines)
changes_count = 0

for tag, i1, i2, j1, j2 in matcher.get_opcodes():
    if tag == "replace":
        orig_block = orig_lines[i1:i2]
        cur_block = cur_lines[j1:j2]
        
        # Try line by line alignment using SequenceMatcher inside the block
        sub_matcher = difflib.SequenceMatcher(None, [EMOJI_PATTERN.sub('', l).strip() for l in orig_block],
                                                    [EMOJI_PATTERN.sub('', l).strip() for l in cur_block])
        for s_tag, si1, si2, sj1, sj2 in sub_matcher.get_opcodes():
            if s_tag == "equal":
                for off in range(si2 - si1):
                    o_l = orig_block[si1 + off]
                    c_l = cur_block[sj1 + off]
                    o_emojis = EMOJI_PATTERN.findall(o_l)
                    c_emojis = EMOJI_PATTERN.findall(c_l)
                    if o_emojis and len(c_emojis) < len(o_emojis):
                        indent = c_l[:len(c_l) - len(c_l.lstrip())]
                        restored_lines[j1 + sj1 + off] = indent + o_l.lstrip()
                        changes_count += 1

print(f"Total emoji restorations made: {changes_count}")

# Check specific key structures in restored_lines
full_text = "".join(restored_lines)

# Write back to app.py
with open("app.py", "w", encoding="utf-8") as f:
    f.write(full_text)

print("Saved restored app.py!")
