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
    if any(k in statement.lower() for k in ["q112.", "q162.", "q173."]):
        print("="*40)
        print(block_strip)
        print("="*40)
