import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
results = []

for root, dirs, files in os.walk(solved_paper_dir):
    for file in files:
        if file.endswith(".md") and not file.endswith(".bak"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                for idx, line in enumerate(lines):
                    # Check if line starts with "** " or " ** "
                    # (optional whitespace, then exactly two asterisks, then a space)
                    if re.match(r"^\s*\*\*\s+", line):
                        # Let's check if there's a matching "**" at the end.
                        # Sometimes it might be "**bold text**" which is valid.
                        # But if it starts with "** " (two asterisks followed by a space), it's likely invalid.
                        # Also, if it has " ** " followed by text.
                        # Let's print them out
                        results.append((path, idx + 1, line))
            except Exception as e:
                pass

print(f"Found {len(results)} occurrences of leading '** ':")
for path, line_num, text in results:
    print(f"{os.path.basename(path)} (Line {line_num}): {text.rstrip()}")
