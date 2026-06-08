import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

def fix_leading_double_stars(dry_run=True):
    total_fixed = 0
    for path in target_files:
        if not os.path.exists(path):
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            modified = False
            new_lines = []
            for idx, line in enumerate(lines):
                # Check if line starts with optional spaces, two asterisks, then one or more spaces
                if re.match(r"^\s*\*\*\s+", line):
                    # Replace the leading "**" and subsequent spaces with empty string
                    new_line = re.sub(r"^(\s*)\*\*\s+", r"\1", line)
                    print(f"File: {os.path.basename(path)} | Line {idx+1}:")
                    print(f"  Orig: {line.rstrip()}")
                    print(f"  New : {new_line.rstrip()}")
                    modified = True
                    total_fixed += 1
                    new_lines.append(new_line)
                else:
                    new_lines.append(line)
            
            if modified and not dry_run:
                with open(path, "w", encoding="utf-8") as f:
                    f.writelines(new_lines)
                print(f"-> Saved changes to {os.path.basename(path)}")
        except Exception as e:
            print(f"Error: {e}")
            
    print(f"\nDry run: {dry_run} | Total fixed: {total_fixed}")

# Run dry run
fix_leading_double_stars(dry_run=True)
