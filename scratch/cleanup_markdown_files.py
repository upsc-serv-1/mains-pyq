import os
import re

folders = ["civilsdaily"]
base_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

def balance_bold_tags(line):
    count = line.count("**")
    if count % 2 == 0:
        return line
    # If odd, drop the last "**" to keep it balanced
    parts = line.split("**")
    return "**".join(parts[:-1]) + parts[-1]

def clean_content(content, folder_name):
    # 1. Standardize bullets (specifically for superkalam)
    content = re.sub(r'^[ \t]*•\s+', '- ', content, flags=re.MULTILINE)
    content = re.sub(r'^[ \t]*○\s+', '  - ', content, flags=re.MULTILINE)
    
    # 2. Fix empty bold tags
    content = content.replace("****", "")
    
    # 3. Fix mashed bold headers (e.g., **Example:****AMRUT** or **Example:****Dholavira**)
    content = re.sub(r'\*\*([^\*]+):\*\*\*\*([^\*]+)\*\*', r'**\1:** **\2**', content)
    content = re.sub(r'\*\*([^\*]+)\*\*\*\*([^\*]+)\*\*', r'**\1** **\2**', content)
    
    # 4. Clean spacing inside bold tags: ** text ** -> **text**
    content = re.sub(r'\*\*\s+([^\*]+?)\s+\*\*', r' **\1** ', content)
    content = re.sub(r'\*\*\s+([^\*]+?)\*\*', r' **\1**', content)
    content = re.sub(r'\*\*([^\*]+?)\s+\*\*', r'**\1** ', content)
    
    # 5. Fix smart quote / apostrophe corruptions
    # Generic replacement of letters like "Women?s" or "officer?s" to "Women's"
    content = re.sub(r'([a-zA-Z]+)\?[sS]', r"\1's", content)
    content = re.sub(r'([a-zA-Z]+)\?[tT]', r"\1't", content)
    content = re.sub(r'([a-zA-Z]+)\?[dD]', r"\1'd", content)
    content = re.sub(r'([a-zA-Z]+)\?ve', r"\1've", content)
    content = re.sub(r'([a-zA-Z]+)\?re', r"\1're", content)
    content = re.sub(r'([a-zA-Z]+)\?ll', r"\1'll", content)
    
    # Specific known names with question marks or corruption
    names = ["Vikas", "Subhash", "Vijay", "Sneha", "Ashok", "Rohit", "Manoj", "Rawls", "France", 
             "Ambedkar", "Kudumbashree", "Vivekananda", "Bose", "Thiruvalluvar", "Mahavir", 
             "Clausewitz", "Aristotle", "Kant", "Rawls", "Bentham", "Mill", "Kautilya", "Weber", 
             "Gouges", "Yudhishthira"]
    for name in names:
        content = re.sub(rf'\b{name}\?[sS]?', f"{name}'s", content)
        content = re.sub(rf'\b{name}\b\?', f"{name}'", content)
        
    # Replace corruption unicode characters (\ufffd or others) in common words
    content = re.sub(r'([a-zA-Z]+)\ufffds', r"\1's", content)
    content = re.sub(r'([a-zA-Z]+)\ufffd([a-zA-Z]+)', r"\1'\2", content)
    
    # Clean up multiple spaces
    content = re.sub(r' +', ' ', content)
    
    # Clean up empty lines around markdown syntax
    content = re.sub(r'\n{3,}', '\n\n', content)
    
    # 6. Parse and fix line-by-line split issues
    lines = content.split("\n")
    processed_lines = []
    
    idx = 0
    while idx < len(lines):
        line = lines[idx]
        line_strip = line.strip()
        
        # Check if this line is split and needs to be merged with the next
        if idx < len(lines) - 1:
            next_line = lines[idx+1]
            next_strip = next_line.strip()
            
            # Condition A: Merge consecutive short bold segments (like **Krishna-Godavari (KG)** and **Basin.**)
            if (line_strip.startswith("**") and line_strip.endswith("**") and 
                next_strip.startswith("**") and next_strip.endswith("**")):
                
                inner1 = line_strip[2:-2].strip()
                inner2 = next_strip[2:-2].strip()
                
                # Check if first part does not end with sentence terminator and second part is short
                if (not inner1.endswith((".", "?", "!", ":")) and len(inner2) < 60 and 
                    not any(h in inner1.lower() for h in ["introduction", "conclusion", "body", "way forward", "significance", "challenges"])):
                    # Merge them
                    merged = f"**{inner1} {inner2}**"
                    lines[idx+1] = merged
                    idx += 1
                    continue
            
            # Condition B: Merge split lowercase words or punctuation back to paragraph (e.g. slopes. or and unpredictable rainfall.)
            if line_strip and next_strip:
                clean_curr = line_strip.replace("**", "").strip()
                clean_next = next_strip.replace("**", "").strip()
                
                # If next line starts with lowercase or continuation punctuation, and current doesn't end with a terminator
                is_continuation = (
                    re.match(r'^[a-z]', clean_next) or 
                    clean_next.startswith((",", ")", ";", ".")) or
                    (clean_next.split() and clean_next.split()[0].lower() in ["and", "or", "of", "to", "for", "in", "on", "with", "by", "from", "at", "but"])
                )
                
                if is_continuation and not clean_curr.endswith((".", "?", "!", ":")):
                    # Check if next is bold, merge accordingly
                    if next_strip.startswith("**") and next_strip.endswith("**"):
                        # Append the bold text content
                        inner_next = next_strip[2:-2].strip()
                        if line_strip.endswith("**"):
                            # Combine bold text
                            merged = line_strip[:-2] + " " + inner_next + "**"
                        else:
                            merged = line_strip + " **" + inner_next + "**"
                    else:
                        merged = line_strip + " " + next_strip
                        
                    lines[idx+1] = merged
                    idx += 1
                    continue
                    
        # Apply bold tag balancing on the final line
        balanced_line = balance_bold_tags(line)
        processed_lines.append(balanced_line)
        idx += 1
        
    return "\n".join(processed_lines)

print("Starting Markdown Cleanup...")
for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        continue
        
    print(f"Processing folder: {folder}")
    files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    for f in files:
        filepath = os.path.join(folder_path, f)
        
        # Read content
        with open(filepath, "r", encoding="utf-8", errors="replace") as file_in:
            raw_content = file_in.read()
            
        # Clean content
        cleaned = clean_content(raw_content, folder)
        
        # Write back
        with open(filepath, "w", encoding="utf-8") as file_out:
            file_out.write(cleaned)
            
    print(f"  Completed folder {folder} successfully.")
    
print("All Solved Paper markdown files cleaned and repaired!")
