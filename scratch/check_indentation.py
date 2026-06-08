with open(r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_pwonlyias.md", "r", encoding="utf-8") as f:
    lines = f.readlines()

for idx, line in enumerate(lines[:1000]):
    if line.startswith(" ") and (line.strip().startswith("-") or line.strip().startswith("*")):
        # Count leading spaces
        spaces = len(line) - len(line.lstrip(' '))
        print(f"Line {idx+1}: {spaces} spaces indentation -> {line.strip()[:60]}")
        # Show just a few examples
        if idx > 100:
            break
