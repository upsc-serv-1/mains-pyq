import os
import glob
import re

def clean_double_headings_in_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by the standard block separator
    blocks = re.split(r'\n\s*(?:(?:-\s*){3,}|(?:\*\s*){3,})\n', content)
    
    new_blocks = []
    file_header = ""
    changed = False
    
    for block in blocks:
        bs = block.strip()
        if not bs:
            continue
        if bs.startswith("# ") or "This file contains" in bs:
            file_header = bs
            continue
            
        # Check if this block contains multiple questions
        q_count = len(re.findall(r'^##\s+Question', bs, re.MULTILINE))
        if q_count > 1:
            sub_blocks = re.split(r'\n(?=##\s+Question)', bs)
            for sb in sub_blocks:
                sb_strip = sb.strip()
                # Clean multiple answers inside the sub-block
                sub_ans_count = len(re.findall(r'###\s*Answer', sb_strip, re.IGNORECASE))
                if sub_ans_count > 1:
                    parts = re.split(r'###\s*Answer', sb_strip, flags=re.IGNORECASE)
                    sb_strip = f"{parts[0].strip()}\n\n### Answer\n\n" + "\n\n".join(p.strip() for p in parts[1:])
                new_blocks.append(sb_strip.strip())
            changed = True
            continue
            
        # Check if the block has multiple `### Answer` headings
        ans_count = len(re.findall(r'###\s*Answer', bs, re.IGNORECASE))
        if ans_count > 1:
            parts = re.split(r'###\s*Answer', bs, flags=re.IGNORECASE)
            cleaned_block = f"{parts[0].strip()}\n\n### Answer\n\n" + "\n\n".join(p.strip() for p in parts[1:])
            new_blocks.append(cleaned_block.strip())
            changed = True
        else:
            new_blocks.append(bs)
            
    if changed:
        new_content = ""
        if file_header:
            new_content += file_header + "\n\n---\n\n"
        new_content += "\n\n---\n\n".join(new_blocks)
        new_content += "\n\n---\n"
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"  [CLEANED HEADINGS] Updated {os.path.basename(path)}")
        return True
    else:
        print(f"  [OK] {os.path.basename(path)} has no double headings")
        return False

def main():
    solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
    consolidated_files = glob.glob(os.path.join(solved_dir, "gs[1-4]", "gs[1-4]_*.md"))
    
    print(f"Found {len(consolidated_files)} consolidated coaching files to scan.")
    
    total_cleaned = 0
    for path in consolidated_files:
        if clean_double_headings_in_file(path):
            total_cleaned += 1
            
    print(f"\nDone! Cleaned double headings in {total_cleaned} files.")

if __name__ == "__main__":
    main()
