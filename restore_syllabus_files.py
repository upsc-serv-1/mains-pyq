import re
import os

syllabus_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1"
target_files = [
    "GS1_History_Questions.md",
    "GS1_Society_Questions.md",
    "GS1_Syllabus_Questions_Formatted.md"
]

def is_syllabus_header(line):
    line_strip = line.strip()
    if not line_strip.startswith('#'):
        return False
    patterns = [
        r'^#\s+Paper:',
        r'^##\s+Subject:',
        r'^###\s+Section Group:',
        r'^####\s+Microtopic:',
        r'^#####\s+Subtopic:'
    ]
    return any(re.match(p, line_strip, re.IGNORECASE) for p in patterns)

def clean_file_of_explanations(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    cleaned_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_strip = line.strip()
        
        if is_syllabus_header(line_strip):
            cleaned_lines.append(line)
            i += 1
        elif not line_strip:
            cleaned_lines.append(line)
            i += 1
        elif re.match(r'^Q\d+\.', line_strip):
            cleaned_lines.append(line)
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_line_strip = next_line.strip()
                if not next_line_strip:
                    cleaned_lines.append(next_line)
                    i += 1
                    continue
                if next_line_strip.startswith('['):
                    cleaned_lines.append(next_line)
                    i += 1
                else:
                    break
            
            while i < len(lines):
                next_line = lines[i]
                next_line_strip = next_line.strip()
                if is_syllabus_header(next_line_strip) or re.match(r'^Q\d+\.', next_line_strip):
                    break
                else:
                    i += 1
        else:
            i += 1
            
    return cleaned_lines

def main():
    for filename in target_files:
        path = os.path.join(syllabus_dir, filename)
        if not os.path.exists(path):
            print(f"File not found: {path}")
            continue
            
        print(f"Cleaning {filename}...")
        cleaned_lines = clean_file_of_explanations(path)
        
        # Write back to original file
        with open(path, "w", encoding="utf-8") as f:
            f.writelines(cleaned_lines)
            
        print(f"Successfully cleaned and restored {filename} to {len(cleaned_lines)} lines.")

if __name__ == "__main__":
    main()
