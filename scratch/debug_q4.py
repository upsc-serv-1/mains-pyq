import os
import re
import pdfplumber
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Re-implement the extraction and normalizer functions from scrape_civilsdaily.py

SUBJECT_TO_PAPER = {
    "polity": "GS II",
    "governance": "GS II",
    "social_justice": "GS II",
    "international_relations": "GS II"
}

def normalize_text(text):
    t = text.lower()
    t = re.sub(r'-\s+', '', t)
    t = re.sub(r'[\*\(\)\[\]\-\.,\?:\'";“”\n]', ' ', t)
    t = re.sub(r'\b\d+\s*(?:words?|marks?)\b', ' ', t)
    t = re.sub(r'\b(?:answer in|words|marks)\b', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

drishti_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\drishti ias"
superkalam_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\superkalam"

ref_db = []
def load_from_dir(directory):
    if not os.path.exists(directory):
        return
    for filename in os.listdir(directory):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(directory, filename)
        subject = filename.replace(".md", "")
        paper = SUBJECT_TO_PAPER.get(subject)
        if not paper:
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        parts = content.split("## Question")
        for part in parts[1:]:
            if "### Answer" in part:
                q_header_block, _ = part.split("### Answer", 1)
                m_year = re.search(r'Year:\s*(\d{4})', q_header_block)
                if not m_year:
                    continue
                year = int(m_year.group(1))
                q_text = re.sub(r'^\s*\d+\s*\([^)]*\)\s*', '', q_header_block).strip()
                q_text = q_text.replace("**", "").strip()
                if q_text:
                    norm = normalize_text(q_text)
                    if norm:
                        ref_db.append({
                            "year": year,
                            "paper": paper,
                            "subject": subject,
                            "q_text": q_text,
                            "q_norm": norm
                        })

print("Loading reference database...")
load_from_dir(drishti_dir)
load_from_dir(superkalam_dir)
print(f"Loaded {len(ref_db)} reference questions.")

# Format helper
def format_words_with_bold(word_list):
    result_parts = []
    in_bold = False
    bold_words = []
    for w in word_list:
        font = w.get("fontname", "")
        is_bold = "bold" in font.lower()
        if is_bold:
            if not in_bold:
                in_bold = True
                bold_words = [w["text"]]
            else:
                bold_words.append(w["text"])
        else:
            if in_bold:
                bold_text = " ".join(bold_words)
                if bold_text.strip():
                    result_parts.append(f"**{bold_text}**")
                else:
                    result_parts.append(bold_text)
                in_bold = False
                bold_words = []
            result_parts.append(w["text"])
    if in_bold:
        bold_text = " ".join(bold_words)
        if bold_text.strip():
            result_parts.append(f"**{bold_text}**")
        else:
            result_parts.append(bold_text)
    return " ".join(result_parts)

# Page elements extraction
def extract_page_elements(page):
    tables = page.find_tables()
    valid_tables = []
    table_bboxes = []
    for t in tables:
        data = t.extract()
        if not data:
            continue
        max_cols = max(len(row) for row in data if row is not None)
        if max_cols > 1:
            valid_tables.append((t, data))
            table_bboxes.append(t.bbox)

    words = page.extract_words(extra_attrs=["fontname"])
    filtered_words = []
    for w in words:
        cx = (w["x0"] + w["x1"]) / 2
        cy = (w["top"] + w["bottom"]) / 2
        in_table = False
        for bbox in table_bboxes:
            if bbox[0] - 1 <= cx <= bbox[2] + 1 and bbox[1] - 1 <= cy <= bbox[3] + 1:
                in_table = True
                break
        if not in_table:
            filtered_words.append(w)

    lines_dict = {}
    for w in filtered_words:
        found_line = False
        w_top = w["top"]
        for top_key in lines_dict:
            if abs(w_top - top_key) < 4:
                lines_dict[top_key].append(w)
                found_line = True
                break
        if not found_line:
            lines_dict[w_top] = [w]
            
    elements = []
    for top_key, line_words in lines_dict.items():
        line_words.sort(key=lambda x: x["x0"])
        merged_words = []
        for w in line_words:
            if not merged_words:
                merged_words.append(dict(w))
            else:
                prev = merged_words[-1]
                gap = w["x0"] - prev["x1"]
                if gap < 2.0:
                    prev["text"] += w["text"]
                    prev["x1"] = w["x1"]
                    if len(w["text"]) > len(prev["text"]) - len(w["text"]):
                        prev["fontname"] = w["fontname"]
                else:
                    merged_words.append(dict(w))
        line_text = format_words_with_bold(merged_words)
        avg_top = sum([w["top"] for w in line_words]) / len(line_words)
        elements.append({
            "type": "text",
            "top": avg_top,
            "text": line_text
        })
    elements.sort(key=lambda x: x["top"])
    return elements

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\civilsdaily\GS-2 Model Answers (2018-2025).pdf"
with pdfplumber.open(pdf_path) as pdf:
    # Page 15 is index 14
    page = pdf.pages[14]
    page_els = extract_page_elements(page)
    print(f"\nExtracted {len(page_els)} elements from page 15:")
    for idx, el in enumerate(page_els):
        print(f"[{idx}] Top={el['top']:.2f}: {el['text']}")

    # Let's see the grouping and matching for the block starting with "2025 - Discuss the nature..."
    # The J&K question is towards the end of page 15.
    # In the full list of page elements, let's find where the question starts
    q_start_idx = -1
    for idx, el in enumerate(page_els):
        if "Discuss the nature of Jammu and Kashmir" in el["text"]:
            q_start_idx = idx
            break
            
    print(f"\nJ&K question starts at element index: {q_start_idx}")
    if q_start_idx != -1:
        # Reconstruct the text block from q_start_idx to end of page elements
        block_elements = page_els[q_start_idx:]
        full_text_block = "\n".join([el["text"] for el in block_elements])
        print("\n--- Full Text Block ---")
        print(full_text_block)
        
        # Now run matching
        year = 2025
        paper = "GS II"
        candidates = [ref for ref in ref_db if ref["year"] == year and ref["paper"] == paper]
        print(f"\nFound {len(candidates)} reference candidates for GS II, 2025.")
        
        best_ref = None
        best_score = 0
        full_text_block_clean = full_text_block.replace("**", "")
        
        for ref in candidates:
            ref_norm_words = ref["q_norm"].split()
            cand_norm = normalize_text(full_text_block_clean)
            cand_words = cand_norm.split()
            
            ref_words_set = set(ref_norm_words)
            check_len = min(len(cand_words), len(ref_norm_words) + 10)
            cand_sub_set = set(cand_words[:check_len])
            overlap = len(ref_words_set.intersection(cand_sub_set))
            
            score = overlap / len(ref_words_set) if ref_words_set else 0
            # Print scores for candidates containing Jammu
            if "jammu" in ref["q_norm"]:
                print(f"Candidate: '{ref['q_text'][:60]}...' score = {score:.4f}")
            if score > best_score:
                best_score = score
                best_ref = ref
                
        print(f"\nBest Ref: {best_ref['q_text'] if best_ref else 'None'} with score: {best_score:.4f}")
        
        # Now test splitting
        split_idx = -1
        if best_ref and best_score > 0.50:
            ref_words = best_ref["q_text"].split()
            last_words = [w for w in ref_words[-4:] if len(w) > 2]
            if not last_words:
                last_words = ref_words[-3:]
            print(f"Last words of ref: {last_words}")
            
            search_area_len = max(500, len(best_ref["q_text"]) + 200)
            search_area = full_text_block_clean[:search_area_len]
            best_match_pos = -1
            for word in reversed(last_words):
                pos = search_area.rfind(word)
                if pos != -1:
                    best_match_pos = pos + len(word)
                    print(f"Matched word '{word}' at pos {pos}")
                    break
                    
            if best_match_pos != -1:
                marks_match = re.search(r'\(\d+\)|\b\d+\s*marks?\b', search_area[best_match_pos:best_match_pos+40])
                if marks_match:
                    clean_split_pos = best_match_pos + marks_match.end()
                    print(f"Matched marks at pos: {best_match_pos} + {marks_match.end()}")
                else:
                    clean_split_pos = best_match_pos
                    print(f"No marks matched, split pos = {clean_split_pos}")
                    
                orig_chars = 0
                clean_chars = 0
                while clean_chars < clean_split_pos and orig_chars < len(full_text_block):
                    if full_text_block[orig_chars:orig_chars+2] == "**":
                        orig_chars += 2
                    else:
                        orig_chars += 1
                        clean_chars += 1
                split_idx = orig_chars
                print(f"Mapped split_idx = {split_idx}")
                
        if split_idx == -1:
            print("Split index is -1. Doing fallback.")
            marks_match = re.search(r'\(\d+\)|\b\d+\s*marks?\b', full_text_block_clean[:400])
            if marks_match:
                clean_split_pos = marks_match.end()
            else:
                clean_split_pos = full_text_block_clean.find("\n")
            orig_chars = 0
            clean_chars = 0
            while clean_chars < clean_split_pos and orig_chars < len(full_text_block):
                if full_text_block[orig_chars:orig_chars+2] == "**":
                    orig_chars += 2
                else:
                    orig_chars += 1
                    clean_chars += 1
            split_idx = orig_chars
            print(f"Fallback split_idx = {split_idx}")
            
        print(f"\nResulting split at char index {split_idx}:")
        print("QUESTION:")
        print(full_text_block[:split_idx])
        print("ANSWER:")
        print(full_text_block[split_idx:])
