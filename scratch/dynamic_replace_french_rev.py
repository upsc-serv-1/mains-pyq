import os
import re

filepath = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_pwonlyias.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# We look for the French Revolution question block
# It starts around the question and ends before the next question or question ID
# The question ID is 2025-gs1-q71-pwonlyias

# Let's locate the question block.
start_idx = content.find("2025-gs1-q71-pwonlyias")
if start_idx == -1:
    print("Could not find question ID.")
    exit(1)

# Let's find the next "---" or next Question ID which marks the end
end_idx = content.find("---", start_idx + len("2025-gs1-q71-pwonlyias"))

question_block = content[start_idx:end_idx]

# Let's perform replacements on this block:
# 1. Clean up the list items by removing blank lines between list lines.
# We can do this line-by-line.
lines = question_block.splitlines()
new_lines = []
for i, line in enumerate(lines):
    # If it is a blank line, check if the previous line and next line are part of lists
    stripped = line.strip()
    if stripped == "":
        # Look ahead and look behind to see if they are part of a list
        prev_list = False
        next_list = False
        
        # Search backwards for a non-blank line
        for p in range(len(new_lines)-1, -1, -1):
            if new_lines[p].strip() != "":
                if new_lines[p].strip().startswith("-") or new_lines[p].strip().startswith("*"):
                    prev_list = True
                break
        
        # Search forwards for a non-blank line
        for n in range(i+1, len(lines)):
            if lines[n].strip() != "":
                if lines[n].strip().startswith("-") or lines[n].strip().startswith("*"):
                    next_list = True
                break
                
        if prev_list and next_list:
            # Skip this blank line
            continue
            
    # Also clean up the formatting typos
    # ":** demanded" -> " demanded"
    # ":** ," -> ","
    line = line.replace(":** demanded", " demanded")
    line = line.replace(":** ,", ",")
    new_lines.append(line)

new_question_block = "\n".join(new_lines)

# Replace in content
new_content = content.replace(question_block, new_question_block)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(new_content)

print("Dynamic replacement successful!")
