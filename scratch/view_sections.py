import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.split('\n')

def print_around(keyword, before=2, after=10):
    for idx, line in enumerate(lines):
        if keyword in line:
            print(f"=== Match for '{keyword}' at Line {idx+1} ===")
            start = max(0, idx - before)
            end = min(len(lines), idx + after)
            for j in range(start, end):
                print(f"{j+1}: {lines[j]}")
            print("\n" + "="*40 + "\n")

print_around("##### Subtopic: FDI")
print_around("##### Subtopic: PPP X Infrastructure")
print_around("#### Microtopic: Issues related to direct and indirect farm subsidies and minimum support prices (MSP)")
print_around("##### Subtopic: Medical and Health Technologies")
print_around("##### Subtopic: Bio-Technology")
