import re
import os
import glob
import subprocess

# Paths to raw PWOnlyIAS files
pwonlyias_raw_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\pwonlyias"
pwonlyias_files = glob.glob(os.path.join(pwonlyias_raw_dir, "*.md"))

def read_and_detect_file(path):
    with open(path, "rb") as f:
        bom = f.read(2)
    if bom == b'\xff\xfe' or bom == b'\xfe\xff':
        encoding = 'utf-16'
    else:
        encoding = 'utf-8'
        
    with open(path, "r", encoding=encoding, errors="replace") as f:
        content = f.read()
    return content, encoding

def clean_text_formatting(content):
    # 1. First, split by lines and do line-based replacements
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        # Replace Body: **** with ### Body (using word boundary \b to not consume preceding **)
        line = re.sub(r'\bBody\s*:\s*\*{4,}(?:\s*\*)*\s*$', '\n\n### Body\n\n', line, flags=re.IGNORECASE)
        line = re.sub(r'\bBody\s*:\s*\*{4,}(?:\s*\*)*\s*', '\n\n### Body\n\n', line, flags=re.IGNORECASE)
        
        # Replace other headers
        line = re.sub(r'\bIntroduction\s*:\s*\*{4,}(?:\s*\*)*\s*', '\n\n### Introduction\n\n', line, flags=re.IGNORECASE)
        line = re.sub(r'\bConclusion\s*:\s*\*{4,}(?:\s*\*)*\s*', '\n\n### Conclusion\n\n', line, flags=re.IGNORECASE)
        
        # Clean table separator lines ending with ****
        line = re.sub(r'\|\s*---\s*\|\s*\*{4,}', '| --- |', line)
        
        # Strip trailing ****
        line = re.sub(r'\s*\*{4,}\s*$', '', line)
        
        # Normalize double bold separators like **** to ** **
        line = line.replace("****", "** **")
        
        # Normalize spaces/corruptions within asterisks using lookahead/lookbehind assertions
        # ** * -> **
        line = re.sub(r'(?<!\*)\*\*(?!\*)\s*(?<!\*)\*(?!\*)', '**', line)
        # * ** -> **
        line = re.sub(r'(?<!\*)\*(?!\*)\s*(?<!\*)\*\*(?!\*)', '**', line)
        # * * -> **
        line = re.sub(r'(?<!\*)\*(?!\*)\s*(?<!\*)\*(?!\*)', '**', line)
        
        # Normalize any sequence of 3 or more asterisks to **
        line = re.sub(r'\*{3,}', '**', line)
        
        processed_lines.append(line)
        
    # 2. Join split lines
    joined_lines = []
    for line in processed_lines:
        line_strip = line.strip()
        if not line_strip:
            joined_lines.append(line)
            continue
            
        if joined_lines:
            prev_idx = len(joined_lines) - 1
            while prev_idx >= 0 and not joined_lines[prev_idx].strip():
                prev_idx -= 1
                
            if prev_idx >= 0:
                prev_line = joined_lines[prev_idx]
                prev_strip = prev_line.strip()
                
                is_prev_bullet = prev_strip.startswith(('- ', '* ', '+ ')) or re.match(r'^\d+\.\s', prev_strip)
                is_curr_special = line_strip.startswith(('- ', '* ', '+ ', '#', '|')) or re.match(r'^\d+\.\s', line_strip) or line_strip == '---'
                
                can_merge = False
                if is_prev_bullet and not is_curr_special:
                    if not prev_strip.endswith(('.', '?', '!', ':', '|')):
                        can_merge = True
                    elif prev_strip.endswith(',') or line_strip.startswith(('like ', 'which ', 'that ', 'and ', 'or ', 'but ', 'to ', 'in ', 'on ', 'for ', 'with ', 'by ', 'as ')):
                        can_merge = True
                    elif line_strip.startswith('**') or (line_strip and line_strip[0].islower()):
                        can_merge = True
                        
                if can_merge:
                    joined_lines = joined_lines[:prev_idx + 1]
                    joined_lines[prev_idx] = prev_line.rstrip() + " " + line.lstrip()
                    continue
                    
        joined_lines.append(line)
        
    # 3. Final cleanup of unmatched bold tags in each line
    final_lines = []
    for line in joined_lines:
        # Strip leading colons and spaces
        line = re.sub(r'^[:\s]+', '', line)
        
        # Count count of **
        if line.count("**") % 2 != 0:
            # If it ends with **, strip it
            if line.rstrip().endswith("**"):
                line = line.rstrip()[:-2]
            # Otherwise, balance it by appending ** at the end of the line
            else:
                line = line.rstrip() + "**"
                
        final_lines.append(line)
        
    return "\n".join(final_lines)

def main():
    print("Step 1: Fixing raw subject-wise PWOnlyIAS files...")
    for path in pwonlyias_files:
        if not os.path.exists(path):
            continue
            
        if "_test.md" in path:
            continue
            
        content, encoding = read_and_detect_file(path)
        new_content = clean_text_formatting(content)
        
        if new_content != content:
            with open(path, "w", encoding=encoding) as f:
                f.write(new_content)
            print(f"  Fixed formatting issues in raw file: {os.path.basename(path)} (Encoding: {encoding})")
        else:
            print(f"  No formatting issues in raw file: {os.path.basename(path)}")
            
    print("\nStep 2: Regenerating consolidated paper files...")
    subprocess.run(["python", "generate_combined_gs_files.py"], check=True)
    
    print("\nStep 3: Compiling master files (GS1, GS2, GS3)...")
    subprocess.run(["python", "compile_master_gs1.py"], check=True)
    subprocess.run(["python", "compile_master_gs2.py"], check=True)
    subprocess.run(["python", "compile_master_gs3.py"], check=True)
    
    print("\nStep 4: Rebuilding JS databases for viewer app...")
    subprocess.run(["python", "parse_master_to_js.py"], check=True)
    
    print("\nAll tasks completed successfully!")

if __name__ == "__main__":
    main()
