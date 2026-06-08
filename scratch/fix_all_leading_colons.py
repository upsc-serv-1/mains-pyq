import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

def fix_leading_colons(dry_run=True):
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
                        # Match optional space, a colon, optional space
                        # We only match if there is non-whitespace after the colon, or it's just a colon line
                        stripped = line.strip()
                        if stripped.startswith(":") and len(stripped) > 0:
                            # Let's perform the replacement: remove leading colon and optional whitespace/stars formatting
                            # e.g., ": **" -> "**", ":**" -> "**", ": **The" -> "**The", ": text" -> "text"
                            # We can do this with a regex replacement on the line
                            # We match the leading colon and any spaces after it.
                            # Since line starts with optional spaces, then colon, then optional spaces.
                            new_line = re.sub(r"^(\s*):+\s*", r"\1", line)
                            
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
                    print(f"Error reading/writing {path}: {e}")
                    
    print(f"\nDry run: {dry_run} | Total lines matched: {total_fixed}")

# Run dry run first
fix_leading_colons(dry_run=True)
