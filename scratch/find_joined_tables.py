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
    
    for i in range(1, len(lines)):
        line = lines[i].strip()
        prev_line = lines[i-1].strip()
        
        # If this line starts a table row, but the previous line is a paragraph and does not end or start a table row
        if line.startswith('|') and not prev_line.startswith('|') and prev_line:
            # Also exclude the divider row e.g. |---|
            if '---' not in line:
                joined_tables.append((i+1, prev_line, line))
                
    if joined_tables:
        print(f"File: {os.path.basename(path)}")
        print(f"Found {len(joined_tables)} tables not preceded by blank lines:")
        for line_num, prev, curr in joined_tables[:3]:
            print(f"  Line {line_num}:")
            print(f"    Prev: {prev[:100]}...")
            print(f"    Curr: {curr[:100]}...")
        if len(joined_tables) > 3:
            print(f"    ... and {len(joined_tables)-3} more.")
        print()
