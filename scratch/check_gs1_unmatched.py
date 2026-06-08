import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1\GS1_Syllabus_Questions_Formatted.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
for block in blocks:
    block_strip = block.strip()
    if not block_strip.startswith("Q"):
        continue
    statement = block_strip.split('\n')[0].strip()
    if any(k in statement.lower() for k in ["chandella", "consolidation", "french revolution"]):
        print(statement)
        # print metadata
        lines = block_strip.split('\n')
        for line in lines[1:]:
            if line.strip().startswith('['):
                print(line.strip())
            else:
                break
        print()
