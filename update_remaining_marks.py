import os
import re

syllabus_paths = {
    1: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1\GS1_Syllabus_Questions_Formatted.md",
    2: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs2\GS2_Syllabus_Questions_Formatted.md",
    3: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
}

# Mapping of specific question identifiers to their marks
remaining_marks = {
    1: {
        "Q112.": "10",  # Chandella artform
        "Q162.": "15",  # India's consolidation
        "Q173.": "15"   # French Revolution
    },
    2: {
        "Q56.": "15",   # Delhi Lt. Governor vs Govt
        "Q204.": "15",  # Inequality and poverty
        "Q238.": "15",  # Energy security West Asia
        "Q249.": "10"   # Indian diaspora in West
    },
    3: {
        "Q102.": "10",  # e-Technology help farmers
        "Q192.": "15"   # Depleting groundwater
    }
}

def update_marks_for_paper(paper_num):
    path = syllabus_paths[paper_num]
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
    updated_blocks = []
    updated_count = 0
    
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            updated_blocks.append(block)
            continue
            
        lines = block_strip.split('\n')
        statement = lines[0].strip()
        
        # Check if this statement matches any of our remaining question prefixes
        match_prefix = None
        for prefix in remaining_marks[paper_num].keys():
            if statement.startswith(prefix):
                match_prefix = prefix
                break
                
        if match_prefix:
            # Reconstruct metadata to insert [Marks: X]
            metadata_lines = []
            i = 1
            while i < len(lines):
                line_strip = lines[i].strip()
                if not line_strip:
                    i += 1
                    continue
                if line_strip.startswith('['):
                    metadata_lines.append(line_strip)
                    i += 1
                else:
                    break
                    
            combined_metadata = " ".join(metadata_lines)
            
            if "[Marks:" not in combined_metadata:
                marks_val = remaining_marks[paper_num][match_prefix]
                new_meta = re.sub(r'(\[Year:\s*\d{4}\])', r'\1 [Marks: ' + marks_val + ']', combined_metadata)
                
                block_reconstructed = statement + "\n\n" + new_meta + "\n" + "\n".join(lines[i:])
                updated_blocks.append(block_reconstructed)
                updated_count += 1
            else:
                updated_blocks.append(block)
        else:
            updated_blocks.append(block)
            
    if updated_count > 0:
        updated_content = "\n".join(updated_blocks)
        with open(path, "w", encoding="utf-8") as f:
            f.write(updated_content)
        print(f"GS{paper_num}: Successfully updated {updated_count} remaining questions with Marks tags.")
    else:
        print(f"GS{paper_num}: No remaining questions needed manual marks updates.")

def main():
    print("Updating remaining missing marks tags manually in syllabus files...")
    for p in [1, 2, 3]:
        update_marks_for_paper(p)
    print("Manual update complete!")

if __name__ == "__main__":
    main()
