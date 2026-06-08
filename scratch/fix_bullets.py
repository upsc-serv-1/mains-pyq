import os
import glob
import re

solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
pw_files = glob.glob(os.path.join(solved_dir, "gs[1-4]", "gs[1-4]_pwonlyias.md"))

for path in pw_files:
    filename = os.path.basename(path)
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.splitlines()
    changed = False
    new_lines = []
    
    for idx, line in enumerate(lines):
        if "●" in line:
            # Safe print using ascii representation
            print(f"{filename} Line {idx+1} (Before): {line.encode('ascii', errors='replace').decode('ascii')}")
            
            # Replace zero or more spaces followed by ● followed by zero or more spaces with ' <br>• '
            # Note: We use \u25cf for matching the character
            new_line = re.sub(r'\s*\u25cf\s*', ' <br>• ', line)
            
            print(f"{filename} Line {idx+1} (After):  {new_line.encode('ascii', errors='replace').decode('ascii')}")
            new_lines.append(new_line)
            changed = True
        else:
            new_lines.append(line)
            
    if changed:
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(new_lines) + "\n")
        print(f"Updated {filename}")
