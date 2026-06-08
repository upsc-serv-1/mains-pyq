import re
import os
import glob
import subprocess

# Paths to raw Drishti IAS files
drishti_raw_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\drishti ias"
drishti_files = glob.glob(os.path.join(drishti_raw_dir, "*.md"))

def clean_bold_markdown(text):
    # Split by bold markers
    parts = text.split("**")
    if len(parts) < 3:
        # No matching bold tags or just one raw tag, return cleaned original text
        return re.sub(r'\s+', ' ', text).strip()
        
    cleaned_parts = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            # Inside bold tag: strip spaces from both sides
            cleaned_parts.append(part.strip())
        else:
            # Outside bold tag: normalize spaces
            part_clean = re.sub(r'\s+', ' ', part)
            cleaned_parts.append(part_clean)
            
    # Reconstruct the string with proper spacing around the bold markers
    reconstructed = []
    for i, part in enumerate(cleaned_parts):
        if i == 0:
            reconstructed.append(part)
        elif i % 2 == 1:
            # This is bold text, prepend '**' and append '**'
            prev = reconstructed[-1]
            if prev and not prev.endswith(" ") and not prev.endswith("\n"):
                # Insert space before bold opening if it's not a list bullet or header marker
                if not re.match(r'^[\-#*]+$', prev.strip()):
                    reconstructed[-1] = prev + " "
            reconstructed.append("**" + part + "**")
        else:
            # Non-bold text after a bold tag
            if part:
                if part.startswith(":") or part.startswith(",") or part.startswith(".") or part.startswith(";") or part.startswith("?"):
                    part_formatted = part.lstrip()
                    if part_formatted.startswith(":"):
                        part_formatted = ":" + " " + part_formatted[1:].lstrip()
                    reconstructed.append(part_formatted)
                else:
                    reconstructed.append(" " + part.lstrip())
            else:
                reconstructed.append("")
                
    result = "".join(reconstructed)
    result = re.sub(r' +', ' ', result)
    return result.strip()

def clean_line_v7(line):
    # 0. Split inline subheadings followed by list bullets
    line = re.sub(r'\s*\*\*([^*:]{2,80}:?)\*\*\s*-\s*', r'\n\n**\1**\n\n- ', line)
    
    # 1. Normalize malformed list bullets: -** or *** or - ** or * **
    # Ensure there is a space after the bullet and no space inside the stars
    line = re.sub(r'(^|\s)([\-*])\s*\*\*\s*', r'\1\2 **', line)
    
    # 2. Normalize inline headers
    line = re.sub(r'\s*\*\*(##|###)\*\*\s*', r'\n\1** ', line)
    line = re.sub(r'\s*(##|###)\*\*\s*', r'\n\1** ', line)
    
    sub_lines = line.split('\n')
    cleaned_sub_lines = []
    
    for sub in sub_lines:
        sub_strip = sub.strip()
        if not sub_strip:
            continue
            
        # Keep leading indentation spaces
        leading_spaces = ""
        match_spaces = re.match(r'^(\s+)', sub)
        if match_spaces:
            leading_spaces = match_spaces.group(1)
            
        # Match list item pattern: - ** Title: ** Rest
        list_match = re.match(r'^([\-*])\s*\*\*\s*(.*?)\s*\*\*(.*)$', sub_strip)
        if list_match:
            bullet = list_match.group(1)
            title = list_match.group(2).strip()
            rest = list_match.group(3).strip()
            
            title_clean = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', title).strip()
            
            # Clean up leading colons/hyphens/spaces from rest
            rest_clean = re.sub(r'^[:\-\s]+', '', rest).strip()
            rest_clean = clean_bold_markdown(rest_clean)
            
            cleaned_sub_lines.append(f"{leading_spaces}{bullet} **{title_clean}:** {rest_clean}")
            continue
            
        # Match header pattern
        match = re.match(r'^(##|###)\s*\*\*\s*(.*?)\s*\*\*(.*)$', sub_strip)
        if match:
            level_marker = match.group(1)
            title = match.group(2).strip()
            rest = match.group(3).strip()
            
            title_clean = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', title).strip()
            level = "###"
            
            hdr_line = f"{level} {title_clean}"
            
            if rest:
                rest_clean = re.sub(r'^[:\-\s]+', '', rest).strip()
                rest_clean = clean_bold_markdown(rest_clean)
                cleaned_sub_lines.append(hdr_line)
                cleaned_sub_lines.append(leading_spaces + rest_clean)
            else:
                cleaned_sub_lines.append(hdr_line)
            continue
            
        match_no_close = re.match(r'^(##|###)\s*\*\*\s*(.*?)$', sub_strip)
        if match_no_close:
            level_marker = match_no_close.group(1)
            title = match_no_close.group(2).strip()
            title_clean = re.sub(r'^[:\-\s]+|[:\-\s]+$', '', title).strip()
            cleaned_sub_lines.append(f"### {title_clean}")
            continue
            
        cleaned_sub_lines.append(leading_spaces + clean_bold_markdown(sub_strip))
        
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
                
                before_clean = clean_line_v7(before)
                updated_lines.append(before_clean)
                updated_lines.append(after)
                changes += 1
                continue
        
        # 2. Run our robust header and list cleaning
        cleaned = clean_line_v7(line)
        if cleaned != line:
            updated_lines.append(cleaned)
            changes += 1
        else:
            updated_lines.append(line)
            
    return "\n".join(updated_lines), changes

def main():
    # Step 1 & 2 have been decommissioned. The consolidated files (like solved paper/gs1/gs1_pwonlyias.md)
    # are now the primary source files, preventing manual edits from being overwritten.
    
    print("\nStep 1: Compiling master files from consolidated source files (GS1, GS2, GS3)...")
    # Run compilation scripts
    subprocess.run(["python", "compile_master_gs1.py"], check=True)
    subprocess.run(["python", "compile_master_gs2.py"], check=True)
    subprocess.run(["python", "compile_master_gs3.py"], check=True)
    
    print("\nStep 2: Rebuilding JS databases for viewer app...")
    # Run parse_master_to_js.py
    subprocess.run(["python", "parse_master_to_js.py"], check=True)
    
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()
