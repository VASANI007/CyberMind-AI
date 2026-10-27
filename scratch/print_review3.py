import json

with open('scratch/review3_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data:
    texts = [t['text'] for t in s['texts']]
    print(f"=== SLIDE {s['slide_index']} ===")
    for t in texts[:6]:
        print("  *", t[:90])
