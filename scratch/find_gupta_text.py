import os

search_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc"
found = False

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".md"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "The Gupta and" in content or "Gupta and" in content:
                    # Find the line containing it
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if "The Gupta and" in line or "Gupta and" in line:
                            print(f"File: {path} | Line {idx+1}: {line}")
                            found = True
            except Exception as e:
                pass

if not found:
    print("Not found.")
