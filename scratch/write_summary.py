import json

with open('scratch/review3_dump.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

with open('scratch/review3_summary.txt', 'w', encoding='utf-8') as out:
    for s in data:
        texts = [t['text'] for t in s['texts']]
        out.write(f"\n=== SLIDE {s['slide_index']} ===\n")
        for t in texts:
            out.write(f"  * {t}\n")

print("Saved to scratch/review3_summary.txt")
