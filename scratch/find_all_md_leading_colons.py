import os
import re

search_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc"
found = False

for root, dirs, files in os.walk(search_dir):
    # Exclude git and cache
    if ".git" in root.split(os.sep) or "cache" in root.split(os.sep) or "scratch" in root.split(os.sep):
        continue
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for colon at the start of a paragraph or line
                # Let's search for lines matching: ^\s*:\s*\w+ or ^\s*:\s*\*\*
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith(":") and len(stripped) > 1:
                        # Print it!
                        print(f"File: {path} | Line {idx+1}: {line}")
                        # Also print the previous line
                        if idx > 0:
                            print(f"  Prev: {lines[idx-1]}")
                        found = True
            except Exception as e:
                pass

if not found:
    print("No leading colons found in any markdown file.")
