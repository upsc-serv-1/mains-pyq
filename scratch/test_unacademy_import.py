import pdfplumber
import sys
import os

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy\unacademy mains solved paper.pdf"
sys.path.append(r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc")
from scrape_unacademy import extract_smart_layout, join_paragraph_lines, is_question_start, parse_question_num

image_counter = [0]
text_blocks = []

print("Extracting pages for 2020 (Pages 347 to 448)...")
with pdfplumber.open(pdf_path) as pdf:
    # 2020 is pages 347 to 448 (0-indexed 346 to 447)
    for page_num in range(347, 449):
        page = pdf.pages[page_num - 1]
        page_lines = extract_smart_layout(page, image_counter, "scratch_images")
        joined_page_lines = join_paragraph_lines(page_lines)
        if joined_page_lines:
            text_blocks.append("\n".join(joined_page_lines))

full_text = "\n".join(text_blocks)
lines = full_text.split("\n")
cleaned_lines = []
for line in lines:
    line_strip = line.strip()
    if not line_strip:
        continue
    cleaned_lines.append(line)

curr_int = 0
curr_paper = "GS I"
papers_seq = ["GS I", "GS II", "GS III", "GS IV"]
questions = []
current_question = None

for idx, line in enumerate(cleaned_lines):
    next_lines = cleaned_lines[idx+1:idx+16]
    if is_question_start(line, next_lines, curr_int):
        if current_question:
            questions.append(current_question)
        val, _ = parse_question_num(line.strip(), curr_int)
        
        if val == 1 and curr_int > 1:
            try:
                curr_idx = papers_seq.index(curr_paper)
                curr_paper = papers_seq[curr_idx + 1]
            except IndexError:
                pass
        curr_int = val
        current_question = {
            "paper": curr_paper,
            "header_line": line.strip(),
            "answer_lines": [],
            "in_answer": False,
            "lines": [line]
        }
    elif current_question:
        line_strip = line.strip()
        clean_line_strip = line_strip.replace("**", "").strip()
        is_answer_start = (
            clean_line_strip.lower().startswith("answer:") or 
            clean_line_strip.lower().startswith("introduction:") or 
            clean_line_strip.lower().startswith("intro:")
        )
        prev_line_contains_meta = False
        if len(current_question["lines"]) > 0:
            prev_line_lower = current_question["lines"][-1].lower()
            if "words" in prev_line_lower or "marks" in prev_line_lower:
                prev_line_contains_meta = True
                
        if is_answer_start or (prev_line_contains_meta and not current_question["in_answer"]):
            current_question["in_answer"] = True
            
        if current_question["in_answer"]:
            current_question["answer_lines"].append(line)
        else:
            current_question["lines"].append(line)

if current_question:
    questions.append(current_question)

# Search for the question with "income substantially" in its answer
target_q = None
for q in questions:
    ans_str = " ".join(q["answer_lines"])
    if "income substantially" in ans_str:
        target_q = q
        break

if target_q:
    print(f"\nFound target question! Header: {target_q['header_line']}")
    print("\n--- q['answer_lines'] before write-stage join_paragraph_lines ---")
    for idx, l in enumerate(target_q["answer_lines"]):
        if "farmers" in l or "income" in l or "substantially" in l or "Decoding" in l or "Intro" in l:
            print(f"Index {idx}: {repr(l)}")
            
    print("\n--- running join_paragraph_lines(q['answer_lines']) ---")
    joined = join_paragraph_lines(target_q["answer_lines"])
    for idx, l in enumerate(joined):
        if "farmers" in l or "income" in l or "substantially" in l or "Decoding" in l or "Intro" in l:
            print(f"Joined Index {idx}: {repr(l)}")
else:
    print("\nTarget question not found!")
