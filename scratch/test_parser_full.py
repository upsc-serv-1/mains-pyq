import pdfplumber
import re
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy\unacademy mains solved paper.pdf"

# Append path to import scrape_unacademy
sys.path.append(r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc")
from scrape_unacademy import extract_smart_layout, join_paragraph_lines, parse_question_num, is_question_start

with pdfplumber.open(pdf_path) as pdf:
    # Page 404
    page = pdf.pages[403]
    image_counter = [0]
    page_lines = extract_smart_layout(page, image_counter, "scratch_images")
    
    print("--- Page Lines ---")
    for idx, l in enumerate(page_lines):
        print(f"{idx}: {l}")
        
    print("\n--- After Page-level join_paragraph_lines ---")
    joined_page_lines = join_paragraph_lines(page_lines)
    for idx, l in enumerate(joined_page_lines):
        print(f"{idx}: {l}")
        
    # Let's see how they are split into question and answer
    # We will simulate the year processing
    text_blocks = ["\n".join(joined_page_lines)]
    full_text = "\n".join(text_blocks)
    lines = full_text.split("\n")
    cleaned_lines = []
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        cleaned_lines.append(line)
        
    # Simulate question parsing
    curr_int = 0
    curr_paper = "GS III"
    current_question = None
    for idx, line in enumerate(cleaned_lines):
        next_lines = cleaned_lines[idx+1:idx+16]
        if is_question_start(line, next_lines, curr_int):
            val, _ = parse_question_num(line.strip(), curr_int)
            curr_int = val
            current_question = {
                "header_line": line.strip(),
                "lines": [line],
                "answer_lines": [],
                "in_answer": False
            }
        elif current_question:
            line_strip = line.strip()
            clean_line_strip = line_strip.replace("**", "").strip()
            is_answer_start = (
                clean_line_strip.lower().startswith("answer:") or 
                clean_line_strip.lower().startswith("introduction:") or 
                clean_line_strip.lower().startswith("intro:")
            )
            if is_answer_start:
                current_question["in_answer"] = True
            if current_question["in_answer"]:
                current_question["answer_lines"].append(line)
            else:
                current_question["lines"].append(line)
                
    if current_question:
        print("\n--- Current Question Lines ---")
        for idx, l in enumerate(current_question["lines"]):
            print(f"{idx}: {l}")
            
        # Run the clean_q_text logic
        q_text = " ".join(current_question["lines"]).strip()
        print(f"\nJoined with space (q_text): {repr(q_text)}")
        clean_q_text = re.sub(r'^(?:Q|q)?\d*(?:\s*\.|\s*)\([a-d0-9]\)\s*', '', q_text, flags=re.IGNORECASE)
        clean_q_text = re.sub(r'^\([a-d0-9]\)\s*', '', clean_q_text, flags=re.IGNORECASE)
        clean_q_text = re.sub(r'^(?:Q|q)?\d+\.\s*', '', clean_q_text, flags=re.IGNORECASE)
        clean_q_text = clean_q_text.replace("**", "").strip()
        print(f"Cleaned and stripped (clean_q_text): {repr(clean_q_text)}")
        
        q_lines = clean_q_text.split("\n")
        print(f"q_lines: {q_lines}")
        joined_q_lines = join_paragraph_lines(q_lines)
        print(f"joined_q_lines: {joined_q_lines}")
