import re
import os
import fitz

sarrthi_paths = {
    1: r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\GS 1 PYQs.pdf",
    2: r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\GS 2 PYQs.pdf",
    3: r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\GS 3 PYQs.pdf"
}

syllabus_paths = {
    1: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs1\GS1_Syllabus_Questions_Formatted.md",
    2: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs2\GS2_Syllabus_Questions_Formatted.md",
    3: r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
}

def get_column(x0):
    if 20 < x0 < 58:
        return "qn_no"
    elif 58 <= x0 < 100:
        return "year"
    elif 100 <= x0 < 465:
        return "question"
    elif 465 <= x0 < 535:
        return "topic"
    elif 535 <= x0 < 600:
        return "marks"
    return None

def parse_sarrthi_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    all_questions = []
    current_qn = None
    
    for page_idx in range(len(doc)):
        page = doc[page_idx]
        drawings = page.get_drawings()
        
        y_lines = []
        for d in drawings:
            rect = d["rect"]
            if rect.y1 - rect.y0 < 2:
                y_lines.append(rect.y0)
                
        y_lines = sorted(list(set(round(y, 1) for y in y_lines)))
        table_lines = [y for y in y_lines if y > 70]
        
        if not table_lines:
            words = page.get_text("words")
            for w in words:
                x0, y0, text = w[0], w[1], w[4].replace('\u200b', '')
                if y0 < 80: continue
                col = get_column(x0)
                if col and current_qn:
                    if col == "question": current_qn["question"] += " " + text
                    elif col == "topic": current_qn["topic"] += " " + text
                    elif col == "marks": current_qn["marks"] += " " + text
            continue
            
        intervals = []
        for i in range(len(table_lines) - 1):
            intervals.append({
                "start_y": table_lines[i],
                "end_y": table_lines[i+1],
                "words": {
                    "qn_no": [],
                    "year": [],
                    "question": [],
                    "topic": [],
                    "marks": []
                }
            })
            
        words = page.get_text("words")
        for w in words:
            x0, y0, text = w[0], w[1], w[4].replace('\u200b', '')
            col = get_column(x0)
            if not col:
                continue
                
            if intervals and y0 < intervals[0]["start_y"]:
                if y0 > 80:
                    if col == "question" and current_qn: current_qn["question"] += " " + text
                    elif col == "topic" and current_qn: current_qn["topic"] += " " + text
                    elif col == "marks" and current_qn: current_qn["marks"] += " " + text
            else:
                for inv in intervals:
                    if inv["start_y"] <= y0 < inv["end_y"]:
                        inv["words"][col].append(w)
                        break
                        
        for inv in intervals:
            qn_w = sorted(inv["words"]["qn_no"], key=lambda x: (x[1], x[0]))
            qn_str = " ".join(w[4].replace('\u200b', '') for w in qn_w).strip()
            
            year_w = sorted(inv["words"]["year"], key=lambda x: (x[1], x[0]))
            year_str = " ".join(w[4].replace('\u200b', '') for w in year_w).strip()
            
            q_w = sorted(inv["words"]["question"], key=lambda x: (x[1], x[0]))
            q_str = " ".join(w[4].replace('\u200b', '') for w in q_w).strip()
            
            topic_w = sorted(inv["words"]["topic"], key=lambda x: (x[1], x[0]))
            topic_str = " ".join(w[4].replace('\u200b', '') for w in topic_w).strip()
            
            marks_w = sorted(inv["words"]["marks"], key=lambda x: (x[1], x[0]))
            marks_str = " ".join(w[4].replace('\u200b', '') for w in marks_w).strip()
            
            if qn_str.lower() in ["qn no.", "qn.no", "qn no", "qn. no."]:
                continue
                
            if qn_str.isdigit():
                if current_qn:
                    all_questions.append(current_qn)
                current_qn = {
                    "qn_no": int(qn_str),
                    "year": year_str,
                    "question": q_str,
                    "topic": topic_str,
                    "marks": marks_str
                }
            else:
                if current_qn:
                    if year_str: current_qn["year"] += " " + year_str
                    if q_str: current_qn["question"] += " " + q_str
                    if topic_str: current_qn["topic"] += " " + topic_str
                    if marks_str: current_qn["marks"] += " " + marks_str
                    
    if current_qn:
        all_questions.append(current_qn)
        
    return all_questions

def get_char_trigrams(text):
    clean = re.sub(r'[^a-z0-9]', '', text.lower())
    return set(clean[i:i+3] for i in range(len(clean) - 2))

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def parse_syllabus_file(path):
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    blocks = re.split(r'\r?\n(?=Q\d+\.)', content)
    questions = []
    
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            continue
        lines = block_strip.split('\n')
        statement = lines[0].strip()
        
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
        
        year_match = re.search(r'\[Year:\s*(\d{4})\]', combined_metadata)
        year = year_match.group(1) if year_match else "Unknown"
        
        marks_match = re.search(r'\[Marks:\s*([^\]]+)\]', combined_metadata, re.IGNORECASE)
        marks = marks_match.group(1).strip() if marks_match else None
        
        clean_statement = re.sub(r'^Q\d+\.\s*', '', statement).strip()
        
        questions.append({
            "full_qid": statement.split('.')[0], # e.g. Q12
            "statement": clean_statement,
            "year": year,
            "marks": marks,
            "trigrams": get_char_trigrams(clean_statement)
        })
    return questions

def run_detailed_audit():
    for paper in [1, 2, 3]:
        print("="*80)
        print(f"AUDITING GS{paper} BETWEEN SARRTHI PDF AND SYLLABUS FILES")
        print("="*80)
        
        sarrthi_qs = parse_sarrthi_pdf(sarrthi_paths[paper])
        syllabus_qs = parse_syllabus_file(syllabus_paths[paper])
        
        # Calculate trigrams for Sarrthi questions
        for sq in sarrthi_qs:
            sq["trigrams"] = get_char_trigrams(sq["question"])
            
        unmatched_sarrthi = []
        matched_pairs = []
        
        for sq in sarrthi_qs:
            best_sim = 0.0
            best_match = None
            
            for syq in syllabus_qs:
                sim = jaccard_similarity(sq["trigrams"], syq["trigrams"])
                if sim > best_sim:
                    best_sim = sim
                    best_match = syq
                    
            if best_match and best_sim > 0.40:
                matched_pairs.append((sq, best_match, best_sim))
            else:
                unmatched_sarrthi.append((sq, best_match, best_sim))
                
        print(f"Sarrthi questions: {len(sarrthi_qs)}")
        print(f"Syllabus questions: {len(syllabus_qs)}")
        print(f"Successfully matched: {len(matched_pairs)}")
        print(f"Unmatched Sarrthi questions: {len(unmatched_sarrthi)}")
        
        if unmatched_sarrthi:
            print("\nUNMATCHED SARRTHI QUESTIONS DETAILS:")
            for idx, (sq, bm, sim) in enumerate(unmatched_sarrthi):
                print(f"{idx+1}. Sarrthi Q{sq['qn_no']} (Year: {sq['year']}):")
                print(f"   Text: {sq['question']}")
                if bm:
                    print(f"   Best syllabus match found ({bm['full_qid']}, Sim: {sim:.2f}): {bm['statement']}")
                else:
                    print(f"   No syllabus match found at all.")
                print()
        else:
            print("\nALL Sarrthi questions have a corresponding match in the syllabus file (100% covered)!")
            
        # Check for syllabus questions with missing marks tags
        missing_marks = [syq for syq in syllabus_qs if not syq["marks"]]
        print(f"Syllabus questions missing marks tags: {len(missing_marks)}")
        if missing_marks:
            for syq in missing_marks:
                print(f"  - {syq['full_qid']}. {syq['statement'][:100]}...")
        print()

if __name__ == "__main__":
    run_detailed_audit()
