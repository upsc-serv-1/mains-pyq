import os
import glob
import re

pwonlyias_raw_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\pwonlyias"
files = glob.glob(os.path.join(pwonlyias_raw_dir, "*.md"))

for filepath in files:
    if "_test.md" in filepath:
        continue
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    
    printed_file = False
    for idx, line in enumerate(lines):
        if re.search(r'\*{4,}', line):
            if not printed_file:
                print(f"\nFile: {os.path.basename(filepath)}")
                printed_file = True
            print(f"  Line {idx + 1}: {line.strip()}")
