import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

patterns = [
    r"\*\*\*",                  # Triple asterisks
    r"\.\*\*\*\s*[a-zA-Z]",    # .*** followed by letter
    r"\w\*\s+\w",               # letter* space letter
    r"\.\*\s+[a-zA-Z]\*",       # .* space letter*
]

for path in target_files:
    if not os.path.exists(path):
        continue
    print(f"\nScanning {os.path.basename(path)}:")
    with open(path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    
    for idx, line in enumerate(lines):
        for p in patterns:
            if re.search(p, line):
                print(f"Line {idx+1}: {line.rstrip()}")
                break
