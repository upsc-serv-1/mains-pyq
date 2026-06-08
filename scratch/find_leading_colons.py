import os
import re

search_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
files = [
    os.path.join(search_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(search_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(search_dir, "gs3", "gs3_pwonlyias.md"),
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"File not found: {filepath}")
        continue
    
    print(f"\nScanning {os.path.basename(filepath)}:")
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Let's find matches where a line starts with a colon (possibly with some whitespace or markdown syntax)
    # or starts with a colon immediately after double newlines.
    # Let's print out lines containing a colon at the beginning of a line or paragraph
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if line.strip().startswith(":"):
            # print surrounding lines
            start = max(0, idx - 2)
            end = min(len(lines), idx + 3)
            print(f"--- Line {idx + 1} ---")
            for i in range(start, end):
                marker = "-> " if i == idx else "   "
                print(f"{marker}{lines[i]}")
