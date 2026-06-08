import os

filepath = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_pwonlyias.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Find the first and second occurrences of the QID
first_idx = content.find("2025-gs1-q71-pwonlyias")
if first_idx == -1:
    print("Could not find first occurrence.")
    exit(1)

second_idx = content.find("2025-gs1-q71-pwonlyias", first_idx + len("2025-gs1-q71-pwonlyias"))
if second_idx == -1:
    print("Could not find second occurrence.")
    exit(1)

# The question block starts at the first occurrence and ends at the second occurrence (plus its suffix)
end_idx = second_idx + len("2025-gs1-q71-pwonlyias") + 2
question_block = content[first_idx:end_idx]

# Let's perform replacements line-by-line
lines = question_block.splitlines()
new_lines = []
for i, line in enumerate(lines):
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
    line = line.replace(":** demanded", " demanded")
    line = line.replace(":** ,", ",")
    new_lines.append(line)

new_question_block = "\n".join(new_lines)

# Replace in content (handling potential line ending difference)
content_normalized = content.replace("\r\n", "\n")
question_block_normalized = question_block.replace("\r\n", "\n")

if question_block_normalized in content_normalized:
    new_content = content_normalized.replace(question_block_normalized, new_question_block)
    with open(filepath, "w", encoding="utf-8", newline="\n") as f:
        f.write(new_content)
    print("Dynamic replacement v3 successful!")
else:
    print("Normalized question block not found in normalized content.")
