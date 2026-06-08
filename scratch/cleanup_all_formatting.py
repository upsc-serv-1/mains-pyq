import re
import os
import glob

def clean_markdown_formatting(text):
    # 1. Clean bullet point spacing at start of line
    text = re.sub(r'^(\s*[\-*])\s*\*\*', r'\1 **', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*_\-\s*\*\*', r'- **', text, flags=re.MULTILINE)
    
    # 2. Fix the bold-italic spacing bug where single/double stars got separated
    text = re.sub(r'\*\*\s+\*(?!\*)(\w)', r'*** \1', text)
    text = re.sub(r'\*\*\s+\*(?!\*)', r'***', text)
    text = re.sub(r'(\w)\*\s+\*\*(?!\*)', r'\1 ***', text)
    text = re.sub(r'(\S)\*\s+\*\*(?!\*)', r'\1***', text)
    
    # Helper to process blocks of a given pattern
    def process_blocks(text, pattern, tag):
        parts = re.split(pattern, text)
        result = []
        for i, part in enumerate(parts):
            if i % 2 == 1:
                # This is a matched block (e.g. **content**)
                content = part[len(tag):-len(tag)].strip()
                block_text = f'{tag}{content}{tag}'
                
                # Adjust spacing before the block
                if result and result[-1]:
                    prev = result[-1]
                    if re.search(r'\w$', prev):
                        result[-1] = prev + ' '
                
                result.append(block_text)
            else:
                # This is a non-matched block
                if i > 0 and part:
                    # Adjust spacing after the block
                    if re.match(r'^\w', part):
                        part = ' ' + part
                result.append(part)
        return ''.join(result)

    # 3. Process bold-italic (***) without crossing line boundaries
    text = process_blocks(text, r'(\*\*\*[^*\r\n]+?\*\*\*)', '***')
    # 4. Process bold (**) without crossing line boundaries
    text = process_blocks(text, r'(\*\*(?:[^*\r\n]+?)\*\*)', '**')
    # 5. Process italic (*) without crossing line boundaries
    text = process_blocks(text, r'((?<!\*)\*(?:[^*\r\n]+?)\*(?!\*))', '*')
    
    return text

def main():
    solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
    # Find all 20 consolidated files
    consolidated_files = glob.glob(os.path.join(solved_dir, "gs[1-4]", "gs[1-4]_*.md"))
    
    print(f"Found {len(consolidated_files)} consolidated coaching files to process.")
    
    total_files_changed = 0
    for path in consolidated_files:
        filename = os.path.basename(path)
        with open(path, "r", encoding="utf-8") as f:
            original_content = f.read()
            
        cleaned_content = clean_markdown_formatting(original_content)
        
        if cleaned_content != original_content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(cleaned_content)
            print(f"  [FIXED] Formatting cleaned in {filename}")
            total_files_changed += 1
        else:
            print(f"  [CLEAN] No issues found in {filename}")
            
    print(f"\nCompleted! Cleaned formatting in {total_files_changed} files.")

if __name__ == "__main__":
    main()
