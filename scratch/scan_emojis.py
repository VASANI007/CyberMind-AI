import os, sys, unicodedata

def is_emoji(char):
    code = ord(char)
    if code < 0x2000:
        return False
    cat = unicodedata.category(char)
    # Exclude common punctuation/math/arrows if desired, but keep emojis and symbols used in UI
    if (0x1F300 <= code <= 0x1FAFF or 
        0x2600 <= code <= 0x27BF or 
        0x2300 <= code <= 0x23FF or 
        0x2B50 <= code <= 0x2B55 or 
        0x203C <= code <= 0x2049 or 
        0x25AA <= code <= 0x25FE or
        0x1F1E6 <= code <= 0x1F1FF or
        0x1F600 <= code <= 0x1F64F or
        0x1F680 <= code <= 0x1F6FF):
        return True
    if cat == 'So' and code > 0x2000:
        return True
    return False

ignore_dirs = {'.git', '.gemini', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'scratch', 'node_modules'}
code_exts = {'.py', '.html', '.css', '.js', '.json', '.md', '.txt', '.env', '.yaml', '.yml'}

results = {}

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
    for file in files:
        if file in ('emoji.txt',):
            continue
        ext = os.path.splitext(file)[1].lower()
        if ext not in code_exts:
            continue
        filepath = os.path.normpath(os.path.join(root, file))
        # Skip datasets or large cache txts in data/
        if filepath.startswith('data\\') or filepath.startswith('data/'):
            continue
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_no, line in enumerate(f, 1):
                    for char in line:
                        if is_emoji(char):
                            name = unicodedata.name(char, 'UNKNOWN')
                            if char not in results:
                                results[char] = {'name': name, 'occurrences': []}
                            results[char]['occurrences'].append((filepath, line_no, line.strip()))
        except Exception:
            pass

print(f'Total unique emojis found: {len(results)}')
with open('scratch/emoji_scan_summary.txt', 'w', encoding='utf-8') as out:
    for emo, info in sorted(results.items(), key=lambda x: len(x[1]['occurrences']), reverse=True):
        files = sorted(set(f for f, _, _ in info['occurrences']))
        out.write(f"{emo} | {info['name']} | Count: {len(info['occurrences'])} | Files: {', '.join(files[:5])}\n")

print("Done scanning. Written to scratch/emoji_scan_summary.txt")
