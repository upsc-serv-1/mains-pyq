import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

for path in target_files:
    if not os.path.exists(path):
        continue
    print(f"\nScanning {os.path.basename(path)} for single-space bullets:")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    count = 0
    for idx, line in enumerate(lines):
        # Match lines that start with exactly ONE space, then a hyphen/asterisk, then space
        if re.match(r"^ [-\*] ", line):
            print(f"Line {idx+1}: {line.rstrip()}")
            count += 1
            if count >= 20:
                print("... (truncated)")
                break
