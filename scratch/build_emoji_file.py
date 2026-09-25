import os, sys, unicodedata
from collections import defaultdict

def is_emoji(char):
    code = ord(char)
    if code < 0x2000:
        return False
    # Exclude box drawings like ─ and ═ so only real icons/emojis are listed
    if 0x2500 <= code <= 0x257F: # Box drawings
        return False
    cat = unicodedata.category(char)
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

ignore_dirs = {'.git', '.gemini', '__pycache__', 'venv', 'env', '.idea', '.vscode', 'scratch', 'node_modules', 'data', 'reports', 'ml/models'}
code_exts = {'.py', '.html', '.css', '.js', '.json', '.md', '.txt', '.env', '.yaml', '.yml'}

emoji_data = defaultdict(lambda: {'name': '', 'occurrences': defaultdict(list)})

for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]
    for file in files:
        if file in ('emoji.txt', 'emoji_scan_summary.txt'):
            continue
        ext = os.path.splitext(file)[1].lower()
        if ext not in code_exts:
            continue
        filepath = os.path.normpath(os.path.join(root, file))
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line_no, line in enumerate(f, 1):
                    stripped_line = line.strip()
                    for char in line:
                        if is_emoji(char):
                            if not emoji_data[char]['name']:
                                emoji_data[char]['name'] = unicodedata.name(char, 'UNKNOWN')
                            # Keep sample snippet (truncated)
                            if len(emoji_data[char]['occurrences'][filepath]) < 5:
                                emoji_data[char]['occurrences'][filepath].append(line_no)
        except Exception:
            pass

# Default change suggestions / replacement ideas for each emoji
change_suggestions = {
    '🛡': 'Keep (Primary Security Shield brand icon) / Lucide Shield',
    '📊': 'Keep (Analytics & metrics) / Lucide BarChart',
    '✅': 'Keep (Success check indicator) / Lucide CheckCircle',
    '⚠': 'Keep (Warning indicator) / Lucide AlertTriangle',
    '🔴': 'Keep (Critical / Offline indicator) / Red status dot',
    '🟢': 'Keep (Safe / Online indicator) / Green status dot',
    '🟡': 'Keep (Warning / Degraded indicator) / Yellow status dot',
    '⚪': 'Keep (Neutral status) / White status dot',
    '●': 'Keep (Bullet dot / indicator)',
    '🌐': 'Keep (Network / URL scanner) / Lucide Globe',
    '📄': 'Keep (Document / Report / Subject) / Lucide FileText',
    '🔍': 'Keep (Search / Scan tool) / Lucide Search',
    '✔': 'Can standardize with ✅ or Lucide Check',
    '⏳': 'Can standardize with ⏱️ or 🕐',
    '🌍': 'Can standardize with 🌐',
    '📧': 'Can standardize with ✉️ or Lucide Mail',
    '🔗': 'Keep (Link / Follow-up pill) / Lucide Link',
    '⚙': 'Keep (Settings / Gear) / Lucide Settings',
    '🖥': 'Keep (Desktop / System check) / Lucide Monitor',
    '🤖': 'Keep (AI Assistant robot) / Lucide Bot',
    '💬': 'Keep (Chat / Speech bubble) / Lucide MessageSquare',
    '💡': 'Keep (Tip / Idea / Suggestion) / Lucide Lightbulb',
    '⚡': 'Keep (Fast / Instant action) / Lucide Zap',
    '✘': 'Can standardize with ❌ or ✖',
    '🔳': 'Can standardize with modern button icon',
    '📱': 'Keep (Mobile / Phone intelligence) / Lucide Smartphone',
    '👤': 'Keep (User / Profile icon) / Lucide User',
    '🚀': 'Keep (Getting started / Launch / Speed) / Lucide Rocket',
    '🎯': 'Keep (Target / Direct hit / Precision) / Lucide Target',
    '🕐': 'Keep (Time / Clock) / Lucide Clock',
    '📈': 'Keep (Trend / Growth) / Lucide TrendingUp',
    '🔑': 'Keep (API Keys / Credentials) / Lucide Key',
    '📦': 'Keep (Package / Dataset / Bundle) / Lucide Package',
    '🔊': 'Keep (Audio / Sound on) / Lucide Volume2',
    '🔇': 'Keep (Audio / Mute) / Lucide VolumeX',
    '🧠': 'Keep (CyberMind brain / Neural engine) / Lucide Brain',
    '❌': 'Keep (Failed / Error indicator) / Lucide XCircle',
    '🔄': 'Keep (Refresh / Retry / Reload) / Lucide RefreshCw',
    '🔒': 'Keep (Lock / Security / Privacy) / Lucide Lock',
    '👥': 'Keep (Team / Users / Social) / Lucide Users',
    '📅': 'Keep (Date / Calendar / Timestamp) / Lucide Calendar',
    '✉': 'Keep (Mail / Email support) / Lucide Mail',
    '📶': 'Keep (Signal / Connection bars)',
    '💻': 'Keep (Computer / Terminal)',
    '🏷': 'Keep (Tag / Label)',
    '🕵': 'Keep (Spy / Threat investigation)',
    '📝': 'Keep (Notes / Description / Memo)',
    '📡': 'Keep (Antenna / Broadcast)',
    '🚨': 'Keep (Alert / Emergency siren)',
    '👁': 'Keep (Eye / Visual scanner)',
    '📞': 'Keep (Phone / Contact call)',
    '🗄': 'Keep (Database / Archive cabinet)',
    '📑': 'Keep (Documentation / Tabs)',
    '🔧': 'Keep (Maintenance / Troubleshooting tool)',
    '👉': 'Keep (Pointer indicator)',
    '📁': 'Keep (Folder / Directory)',
    '📂': 'Keep (Open Folder)',
    '🔐': 'Keep (Encrypted / Secured lock)',
    '🎥': 'Keep (Video / Camera check)',
    '👍': 'Keep (Thumbs up / Helpful)',
    '👎': 'Keep (Thumbs down / Not helpful)',
    '🛠': 'Keep (Tools / Utilities)',
    '🔮': 'Keep (Prediction / Threat forecast)',
    '📋': 'Keep (Clipboard / Copy)',
    '🎓': 'Keep (Education / Tutorial)',
    '📚': 'Keep (Knowledge base / Books)',
    '⏱': 'Keep (SLA / Stopwatch / Timer)',
    '🏠': 'Keep (Home / Dashboard)',
    '❔': 'Keep (Question / Help mark)',
    '🚫': 'Keep (Blocked / Forbidden)',
    '🗑': 'Keep (Delete / Clear history)',
    '📢': 'Keep (Announcement / Notice)',
    '🎵': 'Keep (Music / Audio file)',
    '🧬': 'Keep (DNA / Heuristics signature)',
    '🔎': 'Can standardize with 🔍',
    '🔔': 'Keep (Notification bell)',
    '🐙': 'GitHub Mascot (Social/Brand)',
    '🐦': 'Twitter/X (Social/Brand)',
    '▶': 'Play/YouTube (Social/Brand)',
}

# Regional flags (country codes)
flag_mapping = {
    '🇧': 'Flag / Regional B',
    '🇳': 'Flag / Regional N',
    '🇬': 'Flag / Regional G',
    '🇮': 'Flag / Regional I',
    '🇪': 'Flag / Regional E',
    '🇸': 'Flag / Regional S',
    '🇷': 'Flag / Regional R',
    '🇺': 'Flag / Regional U',
    '🇦': 'Flag / Regional A',
    '🇩': 'Flag / Regional D',
    '🇫': 'Flag / Regional F',
    '🇨': 'Flag / Regional C',
    '🇵': 'Flag / Regional P',
}

# Build Markdown/Text Table
lines = []
lines.append("=" * 125)
lines.append("CYBERMIND AI - COMPLETE PROJECT EMOJI INVENTORY")
lines.append("=" * 125)
lines.append(f"Total Unique Emojis / Symbols Detected: {len(emoji_data)}")
lines.append("Columns: [Emoji] | [Name] | [Project Usage Location(s)] | [Change / Suggestion Column]")
lines.append("-" * 125)
lines.append(f"{'Emoji':<6} | {'Unicode / Standard Name':<38} | {'Where Used in Project (File & Line No)':<50} | {'Change / Suggestion':<35}")
lines.append("-" * 125)

# Sort by count of occurrences
sorted_emojis = sorted(emoji_data.items(), key=lambda x: sum(len(lines) for lines in x[1]['occurrences'].values()), reverse=True)

for emo, data in sorted_emojis:
    name = data['name']
    all_locs = []
    for fpath, lnums in sorted(data['occurrences'].items()):
        f_basename = os.path.basename(fpath)
        ln_str = ",".join(str(n) for n in lnums[:3])
        if len(lnums) > 3:
            ln_str += f"+{len(lnums)-3}more"
        all_locs.append(f"{fpath} (L:{ln_str})")
    
    loc_str = "; ".join(all_locs[:3])
    if len(all_locs) > 3:
        loc_str += f" [and {len(all_locs)-3} more files]"
    
    change_col = change_suggestions.get(emo, flag_mapping.get(emo, "Can customize or replace with custom SVG"))
    
    lines.append(f"{emo:<6} | {name:<38} | {loc_str:<50} | {change_col:<35}")

lines.append("=" * 125)

with open('emoji.txt', 'w', encoding='utf-8') as f:
    f.write("\n".join(lines) + "\n")

print("Generated emoji.txt successfully! Total entries:", len(sorted_emojis))
