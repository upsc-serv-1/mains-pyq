import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')
headers = []
for i, line in enumerate(lines):
    if line.strip().startswith('#'):
        headers.append((i+1, line.strip()))

# Search for relevant sections in headers
keywords = ["investment", "liberal", "fdi", "subsidy", "farm", "health", "biotech", "technology", "infrastructure"]

print("RELEVANT HEADERS IN GS3 SYLLABUS:")
for idx, h in headers:
    if any(k in h.lower() for k in keywords):
        print(f"Line {idx}: {h}")
