import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
for block in blocks:
    block_strip = block.strip()
    if not block_strip.startswith("Q"):
        continue
    statement = block_strip.split('\n')[0].strip()
    if "ppp" in statement.lower() or "public-private" in statement.lower() or "public private" in statement.lower():
        print(f"PPP match: {statement}")
    if "fdi" in statement.lower() or "foreign direct" in statement.lower():
        print(f"FDI match: {statement}")
    if "msp" in statement.lower() or "minimum support" in statement.lower():
        print(f"MSP match: {statement}")
