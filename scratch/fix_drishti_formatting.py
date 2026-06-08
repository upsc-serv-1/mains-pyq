import re
import os
import glob

drishti_files = glob.glob(r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\**\*_drishti_ias.md", recursive=True)

def fix_content(content):
    lines = content.split('\n')
    updated_lines = []
    changes = 0
    
    for i, line in enumerate(lines):
        line_strip = line.strip()
        
        # 1. Fix joined tables / approach blocks (contains >= 2 pipes, but does not start with pipe)
        if line_strip.count('|') >= 2 and not line_strip.startswith('|'):
            # Find the index of the first pipe in the original line
            pipe_idx = line.find('|')
            if pipe_idx != -1:
                # Split the line before the pipe and insert double newline
                before = line[:pipe_idx].rstrip()
                after = line[pipe_idx:]
                new_line = before + "\n\n" + after
                updated_lines.append(new_line)
                changes += 1
                continue
                
        # 2. Fix joined headers like "### Body** ..." or "### Conclusion** ..."
        # e.g., "### Body** Role of local bodies" -> "### Body\n\n** Role of local bodies"
        header_join_match = re.match(r'^(###?\s*Body|###?\s*Conclusion|###?\s*Introduction)\*\*(.*)$', line_strip, re.IGNORECASE)
        if header_join_match:
            hdr = header_join_match.group(1).strip()
            rest = header_join_match.group(2).strip()
            # Standardize header to H3
            hdr_clean = re.sub(r'^##?', '###', hdr)
            new_line = f"{hdr_clean}\n\n**{rest}"
            updated_lines.append(new_line)
            changes += 1
            continue
            
        # 3. Fix malformed headers of type "##** Text **" or "## **Text**"
        # We target headers like Body, Conclusion, Introduction, Key Differences
        header_match = re.match(r'^(##|###)\s*\*\*\s*([^*]+?)\s*\*\*$', line_strip)
        if header_match:
            level = header_match.group(1)
            title = header_match.group(2).strip()
            # Clean title
            title_clean = title.strip(':').strip()
            new_line = f"### {title_clean}"
            updated_lines.append(new_line)
            changes += 1
            continue
            
        # 4. Also handle "##** Text" (without closing stars)
        header_no_close = re.match(r'^##\*\*([^*]+)$', line_strip)
        if header_no_close:
            title = header_no_close.group(1).strip()
            title_clean = title.strip(':').strip()
            new_line = f"### {title_clean}"
            updated_lines.append(new_line)
            changes += 1
            continue
            
        updated_lines.append(line)
        
    return "\n".join(updated_lines), changes

for path in drishti_files:
    if "master" in os.path.basename(path):
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    new_content, changes = fix_content(content)
    if changes > 0:
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Fixed {changes} formatting issues in: {os.path.basename(path)}")
    else:
        print(f"No formatting issues found in: {os.path.basename(path)}")
