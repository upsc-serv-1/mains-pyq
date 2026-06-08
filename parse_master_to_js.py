import re
import os
import json

solved_base_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
output_web_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\viewer_app\data"

os.makedirs(output_web_dir, exist_ok=True)

def parse_master_file(paper_num):
    file_path = os.path.join(solved_base_dir, f"gs{paper_num}", f"master_gs{paper_num}_solved.md")
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return []
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Split by Q\d+. at the start of a line
    # We want to keep the matched Q\d+. text, so we use parentheses
    blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
    
    # If the first block doesn't start with Q1., it's likely header introduction text, skip or parse
    parsed_questions = []
    
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            continue
            
        lines = block_strip.split('\n')
        statement = lines[0].strip()
        
        # Parse metadata (lines starting with [)
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
        
        # Extract Subject and Year from metadata
        subject_match = re.search(r'\[Subject:\s*([^\]]+)\]', combined_metadata, re.IGNORECASE)
        subject = subject_match.group(1).strip() if subject_match else "Unknown"
        
        year_match = re.search(r'\[Year:\s*(\d{4})\]', combined_metadata)
        year = year_match.group(1) if year_match else "Unknown"
        
        marks_match = re.search(r'\[Marks:\s*([^\]]+)\]', combined_metadata, re.IGNORECASE)
        marks = marks_match.group(1).strip() if marks_match else "N/A"
        
        # Get the rest of the text for answers
        remaining_content = "\n".join(lines[i:])
        
        # Split remaining content by explanation blocks
        # e.g., 1. Explanation_Civilsdaily:
        exp_splits = re.split(r'\r?\n(?=1\.\s+Explanation_)', remaining_content)
        
        answers = {}
        for split in exp_splits:
            split_strip = split.strip()
            if not split_strip.startswith("1. Explanation_"):
                continue
                
            split_lines = split_strip.split('\n')
            header = split_lines[0].strip()
            
            # Extract institute name
            inst_match = re.match(r'^1\.\s+Explanation_([^:]+):', header)
            inst_name = inst_match.group(1).strip() if inst_match else "Unknown"
            
            # Extract source question and answer body
            source_q = ""
            body_lines = []
            
            body_start_idx = 1
            if len(split_lines) > 1 and split_lines[1].strip().startswith("Source Question:"):
                source_q = split_lines[1].strip().replace("Source Question:", "").strip()
                body_start_idx = 2
                
            body_text = "\n".join(split_lines[body_start_idx:]).strip()
            
            answers[inst_name] = {
                "source": source_q,
                "body": body_text
            }
            
        # Extract ID (e.g. Q1)
        qid_match = re.match(r'^(Q\d+)\.', statement)
        qid = qid_match.group(1) if qid_match else "Unknown"
        
        parsed_questions.append({
            "id": qid,
            "statement": statement,
            "year": year,
            "subject": subject,
            "marks": marks,
            "metadata": combined_metadata,
            "answers": answers
        })
        
    print(f"Parsed {len(parsed_questions)} questions from GS{paper_num} master file.")
    return parsed_questions

def main():
    for p in [1, 2, 3]:
        data = parse_master_file(p)
        output_js_path = os.path.join(output_web_dir, f"gs{p}_data.js")
        
        # Write as JS variable assignment
        with open(output_js_path, "w", encoding="utf-8") as f:
            f.write(f"window.GS{p}_DATA = ")
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write(";\n")
            
        print(f"Saved parsed JS data to {output_js_path}")

if __name__ == "__main__":
    main()
