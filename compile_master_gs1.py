import re
import os
import shutil

# Base Directories
syllabus_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1"
solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1"

target_files = [
    "GS1_History_Questions.md",
    "GS1_Society_Questions.md",
    "GS1_Syllabus_Questions_Formatted.md"
]

institute_files = {
    "Civilsdaily": os.path.join(solved_dir, "gs1_civilsdaily.md"),
    "Drishti IAS": os.path.join(solved_dir, "gs1_drishti_ias.md"),
    "PWOnlyIAS": os.path.join(solved_dir, "gs1_pwonlyias.md"),
    "Rau IAS": os.path.join(solved_dir, "gs1_rau_ias.md"),
    "Superkalam": os.path.join(solved_dir, "gs1_superkalam.md"),
    "Unacademy": os.path.join(solved_dir, "gs1_unacademy.md")
}

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r'^(?:q\d+\.?|que\.?|question\s*\d+\.?|answer\s*in\s*\d+\s*words|marks?|words?|\d+\s*marks?|\d+\s*words?)\s*', '', text)
    text = re.sub(r'[^a-z0-9\s]', '', text)
    tokens = set(text.split())
    stop_words = {'the', 'and', 'of', 'to', 'in', 'is', 'that', 'it', 'on', 'with', 'as', 'for', 'was', 'were'}
    return tokens - stop_words

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def parse_institute_files():
    institute_data = {}
    for inst_name, path in institute_files.items():
        if not os.path.exists(path):
            print(f"Warning: Institute file not found: {path}")
            continue
        
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Split by `## Question`
        blocks = re.split(r'\r?\n(?=##\s+Question)', content)
        q_blocks = [b for b in blocks if b.strip().startswith("## Question")]
        
        parsed_qs = []
        for block in q_blocks:
            lines = block.strip().split('\n')
            header_line = lines[0]
            
            year_match = re.search(r'\(Year:\s*(\d{4})', header_line)
            year = year_match.group(1) if year_match else None
            
            qid_match = re.search(r'Question ID:\s*([a-zA-Z0-9_-]+)', block, re.IGNORECASE)
            qid = qid_match.group(1) if qid_match else "Unknown"
            
            # 1. Try to extract from the header line first
            header_match = re.search(r'^##\s+Question\s+\d+\s*\([^)]+\)\s*(.+)$', header_line)
            question_text = ""
            if header_match:
                header_q = header_match.group(1).strip()
                # Clean leading/trailing bold/italic markers
                header_q = re.sub(r'^\*\*+|\*\*+$|^\*+|\*+$', '', header_q).strip()
                if len(header_q) > 5:
                    question_text = header_q
            
            # 2. Fallback to bold matches in the body
            if not question_text:
                bold_matches = re.findall(r'\*\*([^*]+)\*\*', block)
                questions = []
                for m in bold_matches:
                    m_clean = m.strip()
                    if m_clean.startswith("Question ID:") or m_clean.lower().startswith("answer") or m_clean == "Answer" or m_clean == "Answer:":
                        continue
                    if len(m_clean) > 20:
                        questions.append(m_clean)
                
                question_text = questions[0] if questions else ""
                
            # 3. Fallback to lines 1 to 5 starting/ending with bold
            if not question_text:
                for line in lines[1:5]:
                    if line.strip().startswith("**") and line.strip().endswith("**"):
                        question_text = line.strip().replace("**", "")
                        break
            
            answer_split = re.split(r'###\s*Answer(?:\s+\*\*Answer:\*\*)?', block, flags=re.IGNORECASE)
            answer = "### Answer".join(answer_split[1:]).strip() if len(answer_split) > 1 else ""
            
            # Clean up trailing [Question ID: ...] and horizontal rules
            answer_cleaned = re.sub(r'\[Question ID:.*?\]', '', answer, flags=re.IGNORECASE).strip()
            answer_cleaned = re.sub(r'\r?\n---+$', '', answer_cleaned).strip()
            
            parsed_qs.append({
                "qid": qid,
                "year": year,
                "original_text": question_text.strip(),
                "answer": answer_cleaned,
                "tokens": clean_and_tokenize(question_text)
            })
            
        institute_data[inst_name] = parsed_qs
        print(f"Parsed {len(parsed_qs)} questions for {inst_name}")
        
    return institute_data

def clean_answer_headers(text):
    text = text.strip()
    
    # 1. Strip leading Answer headings or Question ID lines
    while True:
        prev = text
        # Remove leading Answer tags
        text = re.sub(r'^(?:#+\s*Answer\s*(?:\*\*Answer:\*\*)?|\*\*Answer:\*\*|\*\*Answer\*\*|Answer:|Answer\*\*)\s*', '', text, flags=re.IGNORECASE).strip()
        # Remove leading Question ID lines
        text = re.sub(r'^(?:\*\*|\*|)?Question ID:\s*[a-zA-Z0-9_-]+(?:\*\*|\*|)?\s*', '', text, flags=re.IGNORECASE).strip()
        # Remove leading horizontal rules or dividers
        text = re.sub(r'^(?:---\r?\n|\s+)+', '', text).strip()
        if text == prev:
            break
            
    # 2. Remove internal duplicate headings (case-insensitive, on their own line)
    text = re.sub(r'\r?\n#+\s*Answer(?:\s+\*\*Answer:\*\*)?\s*(?:\r?\n|$)', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'\r?\n(?:\*\*|\*|)?Answer:?(?:\*\*|\*|)?\s*(?:\r?\n|$)', '\n', text, flags=re.IGNORECASE)
    
    return text.strip()

def format_compiled_card(question_statement, combined_metadata, institute_data):
    # Extract year
    year_match = re.search(r'\[Year:\s*(\d{4})\]', combined_metadata)
    year = year_match.group(1) if year_match else None
    
    clean_statement = re.sub(r'^Q\d+\.\s*', '', question_statement).strip()
    target_tokens = clean_and_tokenize(clean_statement)
    
    explanations = []
    
    # Specified order of institutes
    institutes = [
        ("Civilsdaily", "civilsdaily"),
        ("Drishti IAS", "drishti ias"),
        ("PWOnlyIAS", "pwonlyias"),
        ("Rau IAS", "rau ias"),
        ("Superkalam", "superkalam"),
        ("Unacademy", "unacademy")
    ]
    
    for inst_name, folder_name in institutes:
        if inst_name not in institute_data:
            continue
        
        inst_qs = institute_data[inst_name]
        same_year_qs = [iq for iq in inst_qs if iq['year'] == year]
        
        best_match = None
        best_sim = 0.0
        
        for iq in same_year_qs:
            sim = jaccard_similarity(target_tokens, iq['tokens'])
            if sim > best_sim:
                best_sim = sim
                best_match = iq
                
        # Fallback to search all questions
        if not (best_match and best_sim > 0.35):
            best_match_any = None
            best_sim_any = 0.0
            for iq in inst_qs:
                sim = jaccard_similarity(target_tokens, iq['tokens'])
                if sim > best_sim_any:
                    best_sim_any = sim
                    best_match_any = iq
            if best_match_any and best_sim_any > 0.35:
                best_match = best_match_any
                
        if best_match:
            ans_body = best_match['answer']
            
            # Prepend institute folder name to relative image references
            ans_body = re.sub(r'(?<!/)images/', f'{folder_name}/images/', ans_body)
            
            # Clean duplicate headings and top markers
            ans_body = clean_answer_headers(ans_body)
            
            # Prepend institute folder name to relative images in the source question text
            src_question = best_match['original_text']
            src_question = re.sub(r'(?<!/)images/', f'{folder_name}/images/', src_question)
            
            # Format according to rules
            exp_str = f"1. Explanation_{inst_name}:\nSource Question: {src_question}\n\n{ans_body}"
            explanations.append(exp_str)
            
    # Combine question card
    card = f"{question_statement}\n\n{combined_metadata}"
    if explanations:
        card += "\n\n" + "\n\n".join(explanations)
    return card

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

def compile_master_file(institute_data):
    clean_syllabus_path = os.path.join(syllabus_dir, "GS1_Syllabus_Questions_Formatted.md")
    if not os.path.exists(clean_syllabus_path):
        print(f"Error: Base syllabus file not found: {clean_syllabus_path}")
        return
        
    master_output_path = os.path.join(solved_dir, "master_gs1_solved.md")
    
    # Back up master_gs1_solved.md if it exists
    if os.path.exists(master_output_path):
        backup_path = master_output_path + ".bak"
        shutil.copyfile(master_output_path, backup_path)
        print(f"Created backup of existing master solved file: {backup_path}")
        
    print(f"Compiling clean questions from {clean_syllabus_path} into master file...")
    lines = clean_file_of_explanations(clean_syllabus_path)
        
    output_lines = []
    i = 0
    q_count = 0
    
    while i < len(lines):
        line = lines[i]
        line_strip = line.strip()
        
        # Match question pattern Q1., Q2., etc.
        if re.match(r'^Q\d+\.', line_strip):
            question_statement = line_strip
            
            # Read subsequent lines to find metadata block
            metadata_lines = []
            i += 1
            while i < len(lines):
                next_line = lines[i]
                next_line_strip = next_line.strip()
                if not next_line_strip:
                    i += 1
                    continue
                if next_line_strip.startswith('['):
                    metadata_lines.append(next_line_strip)
                    i += 1
                else:
                    break
                    
            combined_metadata = " ".join(metadata_lines)
            
            compiled_card = format_compiled_card(question_statement, combined_metadata, institute_data)
            output_lines.append(compiled_card + "\n")
            q_count += 1
        else:
            output_lines.append(line)
            i += 1
            
    with open(master_output_path, "w", encoding="utf-8") as f:
        f.writelines(output_lines)
        
    print(f"Successfully compiled and updated {master_output_path} with {q_count} questions.")

def main():
    print("Starting parsing of institute solved papers...")
    institute_data = parse_institute_files()
    
    print("\nStarting compilation of master GS1 paper...")
    compile_master_file(institute_data)
    
    print("\nMaster GS1 compilation complete!")

if __name__ == "__main__":
    main()
