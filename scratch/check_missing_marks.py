import re
import os

syllabus_paths = {
    1: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1\GS1_Syllabus_Questions_Formatted.md",
    2: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs2\GS2_Syllabus_Questions_Formatted.md",
    3: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
}

for paper_num, path in syllabus_paths.items():
    if not os.path.exists(path):
        print(f"GS{paper_num}: File not found")
        continue
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
    missing = []
    total = 0
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            continue
        total += 1
        lines = block_strip.split('\n')
        # Check metadata lines (lines starting with [)
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
        if "[Marks:" not in combined_metadata:
            missing.append(lines[0])
            
    print(f"GS{paper_num}: Total questions: {total}, Missing marks tags: {len(missing)}")
    for m in missing[:10]:
        print(f"  - {m}")
    if len(missing) > 10:
        print("  - ...")
