import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

def fix_unmatched_bold(dry_run=False):
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
                stripped = line.strip()
                # Check if it starts with "**" and has exactly one "**"
                # Exclude lines that only contain asterisks and spaces (like "*** *")
                if stripped.startswith("**") and stripped.count("**") == 1 and stripped.replace("*", "").strip() != "":
                    # Determine replacement
                    if stripped.endswith("|"):
                        # E.g. "**Conclude... |" -> "**Conclude...** |"
                        # We insert "**" before the final "|"
                        content = line.rstrip()
                        pipe_idx = content.rfind("|")
                        if pipe_idx != -1:
                            new_line = content[:pipe_idx].rstrip() + "** |" + content[pipe_idx+1:] + "\n"
                        else:
                            new_line = content + "**\n"
                    elif line.rstrip().endswith(":"):
                        # E.g. "**Evolution of the slogan:" -> "**Evolution of the slogan:**"
                        new_line = line.rstrip()[:-1] + ":**\n"
                    else:
                        new_line = line.rstrip() + "**\n"
                    
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

# Run apply
fix_unmatched_bold(dry_run=False)
