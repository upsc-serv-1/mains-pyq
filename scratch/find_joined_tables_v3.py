import re
import os
import glob

drishti_files = glob.glob(r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\**\*_drishti_ias.md", recursive=True)

for path in drishti_files:
    if "master" in os.path.basename(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    lines = content.split('\n')
    joined_tables = []
    
    for i, line in enumerate(lines):
        line_strip = line.strip()
        # If the line contains at least two pipes, but does not start with a pipe
        if line_strip.count('|') >= 2 and not line_strip.startswith('|'):
            joined_tables.append((i+1, line_strip))
                
    if joined_tables:
        print(f"File: {os.path.basename(path)}")
        print(f"Found {len(joined_tables)} lines with pipes not starting with pipe:")
        for line_num, text in joined_tables:
            print(f"  Line {line_num}: {text[:150]}...")
        print()
