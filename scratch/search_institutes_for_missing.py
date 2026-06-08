import re
import os
import glob

institutes_gs3_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs3"
institutes_gs2_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs2"

missing_queries = [
    ("PPP criticism", ["ppp", "criticism", "pros", "cons"], 3),
    ("FDI multibrand retail", ["fdi", "multibrand", "multi-brand", "retail", "joint venture"], 3),
    ("MSP rescue trap", ["msp", "rescue", "trap", "low income"], 3),
    ("Life expectancy health challenges", ["expectancy", "health", "challenges"], 2),
    ("Energy independence biotechnology 2047", ["energy", "independence", "2047", "biotechnology"], 3)
]

def search_in_file(file_path, keywords):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r'\r?\n(?=##\s+Question)', content)
    matches = []
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("## Question"):
            continue
        # Count how many keywords are present
        count = sum(1 for kw in keywords if kw.lower() in block_strip.lower())
        if count >= len(keywords) - 1: # Allow all or all-but-one keyword match
            matches.append((block_strip[:300], count))
    return matches

for name, keywords, paper in missing_queries:
    print(f"Searching for {name} in GS{paper} institute files...")
    target_dir = institutes_gs2_dir if paper == 2 else institutes_gs3_dir
    files = glob.glob(os.path.join(target_dir, "*.md"))
    for f in files:
        if "master" in os.path.basename(f):
            continue
        matches = search_in_file(f, keywords)
        if matches:
            print(f"  In {os.path.basename(f)}: found {len(matches)} potential matches:")
            for m, c in matches[:3]:
                print(f"    - [Match score: {c}] {m}...")
    print()
