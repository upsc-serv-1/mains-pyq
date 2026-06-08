import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

def fix_subbullets(dry_run=True):
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
                # If a line starts with exactly one space and a bullet marker (- or * or digit.)
                # E.g., " - " or " * "
                if re.match(r"^ [-\*] ", line):
                    # Replace single space with two spaces
                    new_line = " " + line
                    modified = True
                    total_fixed += 1
                    new_lines.append(new_line)
                elif re.match(r"^ \d+\. ", line):
                    # For numbered list like " 1. "
                    new_line = " " + line
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
            
    print(f"\nDry run: {dry_run} | Total sub-bullets fixed: {total_fixed}")

# Run dry run
fix_subbullets(dry_run=True)
