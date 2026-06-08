import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\drishti ias\geography.md"

def clean_line_v4(line):
    # Normalize inline headers like **##** or **###** by placing them on new lines
    line = re.sub(r'\s*\*\*(##|###)\*\*\s*', r'\n\1** ', line)
    line = re.sub(r'\s*(##|###)\*\*\s*', r'\n\1** ', line)
    
    # If the line was split, process each sub-line
    sub_lines = line.split('\n')
    cleaned_sub_lines = []
    
    for sub in sub_lines:
        sub_strip = sub.strip()
        if not sub_strip:
            continue
            
        # Match a header pattern: starts with ## or ###, followed by stars, title, stars, and optional trailing text
        # Pattern: ^(##|###)\*\*\s*(.*?)\s*\*\*(.*)$
        match = re.match(r'^(##|###)\*\*\s*(.*?)\s*\*\*(.*)$', sub_strip)
        if match:
            level_marker = match.group(1)
            title = match.group(2).strip()
            rest = match.group(3).strip()
            
            # Clean up the title: remove trailing colons, spaces, hyphens
            title_clean = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', title).strip()
            
            level = "###"
            hdr_line = f"{level} {title_clean}"
            
            # Clean up rest of the line
            if rest:
                rest_clean = re.sub(r'^[:\-\s]+', '', rest).strip()
                # Clean up leading spaces inside bold tags if any, e.g. "** Distribution" -> "**Distribution"
                rest_clean = re.sub(r'^\*\*\s+', '**', rest_clean)
                rest_clean = re.sub(r'^\*\s+', '*', rest_clean)
                if rest_clean:
                    cleaned_sub_lines.append(hdr_line)
                    cleaned_sub_lines.append(rest_clean)
                else:
                    cleaned_sub_lines.append(hdr_line)
            else:
                cleaned_sub_lines.append(hdr_line)
        else:
            # Check if it is a header without closing stars, e.g. "##** Body : "
            match_no_close = re.match(r'^(##|###)\*\*\s*(.*?)$', sub_strip)
            if match_no_close:
                level_marker = match_no_close.group(1)
                title = match_no_close.group(2).strip()
                title_clean = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', title).strip()
                cleaned_sub_lines.append(f"### {title_clean}")
            else:
                cleaned_sub_lines.append(sub)
                
    return "\n\n".join(cleaned_sub_lines)

def fix_content(content):
    lines = content.split('\n')
    updated_lines = []
    changes = 0
    
    for i, line in enumerate(lines):
        line_strip = line.strip()
        
        # 1. Fix joined tables / approach blocks (contains >= 2 pipes, but does not start with pipe)
        if line_strip.count('|') >= 2 and not line_strip.startswith('|'):
            pipe_idx = line.find('|')
            if pipe_idx != -1:
                before = line[:pipe_idx].rstrip()
                after = line[pipe_idx:]
                
                # Clean before if it contains malformed header
                before_clean = clean_line_v4(before)
                updated_lines.append(before_clean)
                updated_lines.append(after)
                changes += 1
                continue
        
        # 2. Run our robust header cleaning
        cleaned = clean_line_v4(line)
        if cleaned != line:
            updated_lines.append(cleaned)
            changes += 1
        else:
            updated_lines.append(line)
            
    return "\n".join(updated_lines), changes

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

new_content, changes = fix_content(content)
print(f"Total changes in geography.md: {changes}")

# Print around line 255 to see if Ganga Basin header got fixed
lines = new_content.split('\n')
for i, l in enumerate(lines):
    if "Ganga River Basin covers about" in l:
        print("=== Context after fix ===")
        for idx in range(max(0, i-4), min(len(lines), i+6)):
            print(f"{idx+1}: {lines[idx]}")
