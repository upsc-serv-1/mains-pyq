import re
import os
import glob

institutes_gs2_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs2"
keywords = ["expectancy", "challenges", "health"]

files = glob.glob(os.path.join(institutes_gs2_dir, "*.md"))
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
        if "expectancy" in block_strip.lower() or ("health" in block_strip.lower() and "challenges" in block_strip.lower() and "2022" in block_strip):
            print(f"File: {os.path.basename(f)}")
            print(f"Block Preview:\n{block_strip[:400]}\n")
