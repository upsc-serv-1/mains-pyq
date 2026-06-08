import re
import os

path = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\pwonlyias\modern_history.md"

with open(path, "r", encoding="utf-8") as f:
    content = f.read()

def clean_text_formatting(content):
    # 1. First, split by lines and do line-based replacements
    lines = content.split('\n')
    processed_lines = []
    
    for line in lines:
        line_strip = line.strip()
        
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

new_content = clean_text_formatting(content)

# Count remaining **** or odd bold tags in the new content
print("Before vs After:")
print(f"Original content length: {len(content)}")
print(f"New content length: {len(new_content)}")

# Count ****
orig_four_stars = len(re.findall(r'\*{4,}', content))
new_four_stars = len(re.findall(r'\*{4,}', new_content))
print(f"Original 4+ stars count: {orig_four_stars}")
print(f"New 4+ stars count: {new_four_stars}")

# Check lines with odd number of **
orig_odd_lines = [line.strip() for line in content.split('\n') if line.count("**") % 2 != 0 and not line.strip().startswith("```")]
new_odd_lines = [line.strip() for line in new_content.split('\n') if line.count("**") % 2 != 0 and not line.strip().startswith("```")]

print(f"Original odd bold count: {len(orig_odd_lines)}")
print(f"New odd bold count: {len(new_odd_lines)}")

print("\nFirst 20 new odd lines:")
for line in new_odd_lines[:20]:
    print(f"  {line}")

