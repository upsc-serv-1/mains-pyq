import os

search_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc"
found = False

for root, dirs, files in os.walk(search_dir):
    for file in files:
        if file.endswith(".md") and not file.endswith(".bak"):
            path = os.path.join(root, file)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "Abolition of Feudal Economy" in content or "Social Relevance" in content:
                    lines = content.splitlines()
                    for idx, line in enumerate(lines):
                        if "Abolition of Feudal Economy" in line or "Social Relevance" in line:
                            print(f"File: {path} | Line {idx+1}: {line}")
                            found = True
            except Exception as e:
                pass

if not found:
    print("Not found.")
