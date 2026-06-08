import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

patterns = [
    r"\.\*\*\*\s*[a-zA-Z]",    # .*** followed by letter
    r"\w\*\s+\w",               # letter* space letter
    r"\.\*\s+[a-zA-Z]\*",       # .* space letter*
]

output_file = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\scratch\split_bold_errors.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for path in target_files:
        if not os.path.exists(path):
            continue
        out.write(f"\n=================== {os.path.basename(path)} ===================\n")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for idx, line in enumerate(lines):
            for p in patterns:
                if re.search(p, line):
                    out.write(f"Line {idx+1}: {line}")
                    break

print("Done scanning split bold errors!")
