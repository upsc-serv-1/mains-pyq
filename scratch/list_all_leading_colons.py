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
                    content = f.read()
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    stripped = line.strip()
                    # Pattern for leading colon (allowing spaces, optional asterisks before it, etc., or just starting with colon)
                    # Let's match line that starts with optional spaces, a colon, and then a space or markdown bold
                    if re.match(r"^\s*:\s*\w+", stripped) or re.match(r"^\s*:\s*\*\*", stripped):
                        results.append((path, idx + 1, line))
            except Exception as e:
                pass

print(f"Found {len(results)} occurrences:")
for path, line_num, text in results:
    print(f"{os.path.relpath(path, solved_paper_dir)} (Line {line_num}): {text}")
