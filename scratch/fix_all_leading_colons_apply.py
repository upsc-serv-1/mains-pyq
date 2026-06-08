import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

def fix_leading_colons(dry_run=False):
    total_fixed = 0
    for root, dirs, files in os.walk(solved_paper_dir):
        for file in files:
            if file.endswith(".md") and not file.endswith(".bak"):
                path = os.path.join(root, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    
                    modified = False
                    new_lines = []
                    for idx, line in enumerate(lines):
                        stripped = line.strip()
                        if stripped.startswith(":") and len(stripped) > 0:
                            # Remove leading colon and any whitespace following it, while keeping leading spaces of the line
                            new_line = re.sub(r"^(\s*):+\s*", r"\1", line)
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
                    print(f"Error reading/writing {path}: {e}")
                    
    print(f"\nDry run: {dry_run} | Total lines matched/fixed: {total_fixed}")

# Apply changes
fix_leading_colons(dry_run=False)
