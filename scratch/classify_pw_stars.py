import os
import glob
import re
from collections import Counter

pwonlyias_raw_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\pwonlyias"
files = glob.glob(os.path.join(pwonlyias_raw_dir, "*.md"))

patterns = Counter()
for filepath in files:
    if "_test.md" in filepath:
        continue
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    for line in lines:
        match = re.search(r'(\*{4,})', line)
        if match:
            # Extract pattern context
            # We want to see what is around the asterisks
            line_strip = line.strip()
            # Replace the actual asterisks with 'STARS' to group them
            pattern_str = re.sub(r'\*{4,}', 'STARS', line_strip)
            # Shorten if too long
            if len(pattern_str) > 100:
                pattern_str = pattern_str[-80:]
            patterns[pattern_str] += 1

print("Top patterns with 4+ asterisks:")
for p, count in patterns.most_common(50):
    print(f"  Count: {count} | Pattern: {p}")
