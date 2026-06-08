import fitz
import re
import os

# Base paths
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
        
    print(f"Extracted {len(all_questions)} questions from Sarrthi PDF: {os.path.basename(pdf_path)}")
    return all_questions

# Character-level trigram extraction
def get_char_trigrams(text):
    # Strip spaces and non-alphanumeric chars
    clean = re.sub(r'[^a-z0-9]', '', text.lower())
    return set(clean[i:i+3] for i in range(len(clean) - 2))

def jaccard_similarity(set1, set2):
    if not set1 or not set2:
        return 0.0
    return len(set1.intersection(set2)) / len(set1.union(set2))

def audit_paper(paper_num):
    pdf_path = sarrthi_paths[paper_num]
    syllabus_path = syllabus_paths[paper_num]
    
    if not os.path.exists(pdf_path) or not os.path.exists(syllabus_path):
        print(f"Skipping GS{paper_num}: PDF or Syllabus file missing.")
        return
        
    sarrthi_qs = parse_sarrthi_pdf(pdf_path)
    
    # Tokenize Sarrthi questions into character trigrams
    for sq in sarrthi_qs:
        sq["trigrams"] = get_char_trigrams(sq["question"])
        
    with open(syllabus_path, "r", encoding="utf-8") as f:
        syllabus_content = f.read()
        
    blocks = re.split(r'\r?\n(?=Q\d+\.)', syllabus_content)
    
    updated_blocks = []
    matched_sarrthi_indices = set()
    missing_marks_count = 0
    updated_marks_count = 0
    
    for block in blocks:
        block_strip = block.strip()
        if not block_strip.startswith("Q"):
            updated_blocks.append(block)
            continue
            
        lines = block_strip.split('\n')
        statement = lines[0].strip()
        
        # Read subsequent metadata lines
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
        
        clean_statement = re.sub(r'^Q\d+\.\s*', '', statement).strip()
        target_trigrams = get_char_trigrams(clean_statement)
        
        best_match = None
        best_sim = 0.0
        best_idx = -1
        
        # Match within the same year first
        for idx, sq in enumerate(sarrthi_qs):
            if sq["year"] == year:
                sim = jaccard_similarity(target_trigrams, sq["trigrams"])
                if sim > best_sim:
                    best_sim = sim
                    best_match = sq
                    best_idx = idx
                    
        # Fallback to search all years if no close match in same year
        if not (best_match and best_sim > 0.50):
            for idx, sq in enumerate(sarrthi_qs):
                sim = jaccard_similarity(target_trigrams, sq["trigrams"])
                if sim > best_sim:
                    best_sim = sim
                    best_match = sq
                    best_idx = idx
                    
        has_marks = "[Marks:" in combined_metadata
        
        if best_match and best_sim > 0.50:
            matched_sarrthi_indices.add(best_idx)
            
            # Get Sarrthi marks
            marks = best_match["marks"].strip()
            marks_clean = re.sub(r'(?i)marks?\s*', '', marks).strip()
            if not marks_clean:
                marks_clean = "10"
                
            # If metadata lacks Marks tag, insert it
            if not has_marks:
                new_meta = re.sub(r'(\[Year:\s*\d{4}\])', r'\1 [Marks: ' + marks_clean + ']', combined_metadata)
                block_reconstructed = statement + "\n\n" + new_meta + "\n" + "\n".join(lines[i:])
                updated_blocks.append(block_reconstructed)
                updated_marks_count += 1
            else:
                # If it already has it, keep it
                updated_blocks.append(block)
        else:
            if not has_marks:
                missing_marks_count += 1
            updated_blocks.append(block)
            
    updated_content = "\n".join(updated_blocks)
    with open(syllabus_path, "w", encoding="utf-8") as f:
        f.write(updated_content)
        
    print(f"GS{paper_num}: Audited against Sarrthi.")
    print(f"  - Questions missing Marks that were successfully updated: {updated_marks_count}")
    print(f"  - Questions still missing Marks (no Sarrthi match): {missing_marks_count}")
    
    # Check for unmatched Sarrthi questions
    unmatched_sarrthi = []
    for idx, sq in enumerate(sarrthi_qs):
        if idx not in matched_sarrthi_indices:
            unmatched_sarrthi.append(sq)
            
    if unmatched_sarrthi:
        print(f"  - WARNING: Found {len(unmatched_sarrthi)} Sarrthi questions NOT matched to our syllabus hierarchy:")
        for idx, sq in enumerate(unmatched_sarrthi[:5]):
            print(f"    {idx+1}. Year {sq['year']} (Sarrthi Q{sq['qn_no']}): {sq['question'][:120]}...")
        if len(unmatched_sarrthi) > 5:
            print(f"    ... and {len(unmatched_sarrthi)-5} more unmatched Sarrthi questions.")
    else:
        print("  - Excellent: 100% of Sarrthi questions exist in our master solved papers database!")
        
    return len(unmatched_sarrthi)

def main():
    print("Starting Sarrthi IAS PDF Audit and Marks Update (with Trigram Matching)...")
    for p in [1, 2, 3]:
        print("="*60)
        audit_paper(p)
    print("\nAudit and Marks Update complete!")

if __name__ == "__main__":
    main()
