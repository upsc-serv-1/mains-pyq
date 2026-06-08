import re
import os

syllabus_paths = {
    1: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1\GS1_Syllabus_Questions_Formatted.md",
    2: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs2\GS2_Syllabus_Questions_Formatted.md",
    3: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
}

# The unmatched questions reported by the audit script:
# GS1:
# - Chandella artform
# - India's consolidation
# - French Revolution
# GS2:
# - Civil Society Organizations
# - Inequality and resource ownership
# - Indian Diaspora in SE Asia / Western benefits
# GS3:
# - PPP model criticism
# - FDI in multi-brand retail
# - e-Technology help farmers
# - MSP rescue farmers
# - depleting groundwater

def search_questions(paper_num, keyword):
    path = syllabus_paths[paper_num]
    if not os.path.exists(path):
        return
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
    matches = []
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            continue
        lines = block_strip.split('\n')
        statement = lines[0].strip()
        if keyword.lower() in statement.lower():
            # Get metadata block
            metadata_lines = []
            for line in lines[1:]:
                line_strip = line.strip()
                if not line_strip:
                    continue
                if line_strip.startswith('['):
                    metadata_lines.append(line_strip)
                else:
                    break
            combined_metadata = " ".join(metadata_lines)
            matches.append((statement, combined_metadata))
    
    print(f"--- Search in GS{paper_num} for '{keyword}' ---")
    for st, met in matches:
        print(f"Statement: {st}")
        print(f"Metadata:  {met}\n")

# Run some test searches
search_questions(1, "Chandella")
search_questions(1, "consolidation")
search_questions(1, "French")

search_questions(2, "CSO")
search_questions(2, "Civil Society")
search_questions(2, "Inequality")
search_questions(2, "Diaspora")

search_questions(3, "PPP")
search_questions(3, "FDI")
search_questions(3, "e-Technology")
search_questions(3, "Minimum Support")
search_questions(3, "groundwater")
