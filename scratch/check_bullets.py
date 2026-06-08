import os
import glob
import re

solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
pw_files = glob.glob(os.path.join(solved_dir, "gs[1-4]", "gs[1-4]_pwonlyias.md"))

for path in pw_files:
    print(f"File: {os.path.basename(path)}")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.splitlines()
    for idx, line in enumerate(lines):
        if "●" in line:
            print(f"  Line {idx+1}: {line}")
