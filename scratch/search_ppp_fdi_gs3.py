import re
import os
import glob

institutes_gs3_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs3"

files = glob.glob(os.path.join(institutes_gs3_dir, "*.md"))
for f in files:
    if "master" in os.path.basename(f):
        continue
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()
    
    blocks = re.split(r'\r?\n(?=##\s+Question)', content)
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("## Question"):
            continue
        
        # PPP 2013
        if "ppp" in block_strip.lower() and "criticism" in block_strip.lower() and "2013" in block_strip:
            print(f"PPP 2013 Match - File: {os.path.basename(f)}")
            print(f"Preview: {block_strip[:300]}\n")
            
        # FDI 2013
        if "fdi" in block_strip.lower() and "retail" in block_strip.lower() and "2013" in block_strip:
            print(f"FDI 2013 Match - File: {os.path.basename(f)}")
            print(f"Preview: {block_strip[:300]}\n")
