import os

search_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc"
found = False

for root, dirs, files in os.walk(search_dir):
    # Skip .git directory
    if ".git" in root.split(os.sep):
        continue
    for file in files:
        if file.endswith((".md", ".json", ".py", ".html", ".js")):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                lines = content.splitlines()
                for idx, line in enumerate(lines):
                    stripped = line.strip()
                    if stripped.startswith(":") and len(stripped) > 1 and not stripped.startswith("::"):
                        # Check if it has letters or markdown bold
                        if any(c.isalpha() for c in stripped):
                            print(f"File: {path} | Line {idx+1}: {line}")
                            found = True
            except Exception as e:
                pass

if not found:
    print("No matching colons found.")
