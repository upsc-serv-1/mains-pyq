import os

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
results = []

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
                    # Check if line is just "**" or similar stray markdown bold markers
                    if stripped == "**" or stripped == "":
                        # Let's inspect if it's a stray "**"
                        if stripped == "**":
                            print(f"File: {os.path.basename(path)} | Line {idx+1}: {line.rstrip()}")
                            modified = True
                            # We skip this line to remove it
                            continue
                    new_lines.append(line)
                
                if modified:
                    with open(path, "w", encoding="utf-8") as f:
                        f.writelines(new_lines)
                    print(f"-> Fixed stray '**' in {os.path.basename(path)}")
            except Exception as e:
                print(f"Error in {file}: {e}")
