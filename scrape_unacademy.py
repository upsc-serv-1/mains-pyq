import os
import re
import pdfplumber
import sys

# Set stdout/stderr encoding to UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Paths
pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy\unacademy mains solved paper.pdf"
drishti_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\drishti ias"
superkalam_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\superkalam"
output_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy"
images_dir = os.path.join(output_dir, "images")

# 1. Subject to Paper Mapping
SUBJECT_TO_PAPER = {
    # GS I
    "ancient_history_and_art__culture": "GS I",
    "modern_history": "GS I",
    "world_history": "GS I",
    "post_independent_india": "GS I",
    "indian_society": "GS I",
    "geography": "GS I",
    # GS II
    "polity": "GS II",
    "governance": "GS II",
    "social_justice": "GS II",
    "international_relations": "GS II",
    # GS III
    "economic_development": "GS III",
    "agriculture": "GS III",
    "environment_and_ecology": "GS III",
    "science__technology": "GS III",
    "internal_security": "GS III",
    "disaster_management": "GS III",
    # GS IV
    "ethics_theoretical_questions": "GS IV",
    "ethics_case_studies": "GS IV"
}

# Year-wise page ranges (1-indexed, inclusive)
YEAR_RANGES = {
    2024: (7, 99),
    2023: (100, 174),
    2022: (175, 260),
    2021: (261, 346),
    2020: (347, 448),
    2019: (449, 535),
    2018: (536, 630),
    2017: (631, 718),
    2016: (719, 806),
    2015: (807, 912),
    2014: (913, 998),
    2013: (999, 1109)
}

def normalize_text(text):
    t = text.lower()
    # Clean up hyphenated line breaks in PDF
    t = re.sub(r'-\s+', '', t)
    t = re.sub(r'[\*\(\)\[\]\-\.,\?:\'";“”\n]', ' ', t)
    t = re.sub(r'\b\d+\s*(?:words?|marks?)\b', ' ', t)
    t = re.sub(r'\b(?:answer in|words|marks)\b', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

# 2. Build Reference Database from Drishti and Superkalam
print("Building Subject Reference Database...")
ref_db = []

def load_from_dir(directory):
    if not os.path.exists(directory):
        print(f"Warning: Directory {directory} does not exist. Skipping.")
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
        count = 0
        for part in parts[1:]:
            if "### Answer" in part:
                q_header_block, _ = part.split("### Answer", 1)
                
                # Extract Year from header block
                m_year = re.search(r'Year:\s*(\d{4})', q_header_block)
                if not m_year:
                    continue
                year = int(m_year.group(1))
                
                lines = q_header_block.split("\n")
                q_text_lines = []
                for line in lines[1:]:
                    line = line.strip()
                    if line:
                        q_text_lines.append(line)
                q_text = " ".join(q_text_lines).replace("**", "").strip()
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
                        count += 1
        print(f"  Loaded {count} questions for subject '{subject}' from {os.path.basename(directory)}")

# Helper to parse bold words from font attributes
def format_words_with_bold(word_list):
    result_parts = []
    in_bold = False
    bold_words = []
    
    for w in word_list:
        font = w.get("fontname", "")
        # A word is bold if its font name contains 'bold' (case-insensitive)
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

# Helper to parse question number and clean prefix
def parse_question_num(line_strip, curr_int=None):
    clean_line = line_strip.replace("**", "").strip()
    # Case A: With prefix (e.g. Q1., q2(a), Question 3, Case Study 12)
    m_q = re.match(r'^(?:Q|q|Question|Case Study|Q\.)\s*(\d+)(?:\s*\.|\s*\([a-z0-9]\)|\.\([a-z0-9]\))?\s*(.*)', clean_line, re.IGNORECASE)
    if m_q:
        val = int(m_q.group(1))
        if val <= 25:
            return val, m_q.group(2)
    
    # Case B: Without prefix (e.g. 1., 2(b).) - restrict strictly to <= 25 and make sure it's not a decimal (e.g. 1.12%)
    m_noq = re.match(r'^(\d+)(?:\s*\.|\s*\([a-z0-9]\)|\.\([a-z0-9]\))\s*(.*)', clean_line, re.IGNORECASE)
    if m_noq:
        val = int(m_noq.group(1))
        if val <= 25:
            # Ensure it's not a decimal number (like 1.12 or 4.6)
            if re.match(r'^\d+\.\d+', clean_line):
                return None
            return val, m_noq.group(2)
        
    # Case C: Subpart parenthesis (e.g. (a) or (b))
    if curr_int is not None and curr_int <= 25:
        m_sub = re.match(r'^\(([a-d])\)\s*(.*)', clean_line, re.IGNORECASE)
        if m_sub:
            return curr_int, m_sub.group(2)
            
    return None

def is_question_start(line, next_lines, curr_int):
    line_strip = line.strip()
    clean_line_strip = line_strip.replace("**", "").strip()
    parsed = parse_question_num(clean_line_strip, curr_int)
    if not parsed:
        return False
    
    val, q_text_start = parsed
    
    # Rule 1: Q prefix is unconditionally a question start if it's a valid question number <= 25
    if re.match(r'^(?:Q|q|Question|Case Study|Q\.)\s*\d+', clean_line_strip, re.IGNORECASE):
        return True
        
    # Rule 2: Non-prefixed numbers (e.g. "1.", "2.") - must enforce sequential question numbers
    allowed_next = [1, curr_int, curr_int + 1, curr_int + 2]
    if curr_int > 0 and val not in allowed_next:
        return False
        
    # Check lookahead for words/marks keywords
    combined_text = clean_line_strip
    for next_line in next_lines:
        nl_strip = next_line.strip().replace("**", "").strip()
        if nl_strip.lower().startswith("answer:") or nl_strip.lower().startswith("introduction:") or nl_strip.lower().startswith("intro:"):
            break
        if parse_question_num(nl_strip, curr_int):
            break
        combined_text += " " + nl_strip
        
    combined_lower = combined_text.lower()
    if "words" in combined_lower or "marks" in combined_lower or "answer in" in combined_lower:
        return True
                
    return False

def get_clean_q_num(line_strip, curr_int):
    clean_line = line_strip.replace("**", "").strip()
    m_q = re.match(r'^(?:Q|q)?(\d+)(?:\s*\.|\s*)\(([a-z0-9])\)', clean_line, re.IGNORECASE)
    if m_q:
        return f"{m_q.group(1)}({m_q.group(2)})"
    
    m_dot = re.match(r'^(?:Q|q)?(\d+)\.', clean_line, re.IGNORECASE)
    if m_dot:
        return m_dot.group(1)
        
    m_sub = re.match(r'^\(([a-d])\)', clean_line, re.IGNORECASE)
    if m_sub:
        return f"{curr_int}({m_sub.group(1)})"
        
    return str(curr_int)

def strip_q_prefix(q_text, clean_num):
    text = q_text.strip()
    text = re.sub(r'^(?:Q|q)?\d*(?:\s*\.|\s*)\([a-d0-9]\)\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^\([a-d0-9]\)\s*', '', text, flags=re.IGNORECASE)
    text = re.sub(r'^(?:Q|q)?\d+\.\s*', '', text, flags=re.IGNORECASE)
    text = text.replace("**", "").strip()
    return text

def extract_smart_layout(page, image_counter, images_dir):
    words = page.extract_words(extra_attrs=["fontname"])
    if not words:
        return []
        
    width = page.width
    height = page.height
    
    # Group words into lines
    lines_dict = {}
    for w in words:
        if w["top"] < 40 or w["top"] > height - 37:
            continue
        found = False
        w_top = w["top"]
        for top_key in lines_dict:
            if abs(w_top - top_key) < 5:
                lines_dict[top_key].append(w)
                found = True
                break
        if not found:
            lines_dict[w_top] = [w]
            
    # Sort lines vertically
    sorted_tops = sorted(lines_dict.keys())
    
    # Process each line to detect segments (columns)
    lines_segments = []
    for top in sorted_tops:
        line_words = sorted(lines_dict[top], key=lambda x: x["x0"])
        
        # Merge split words
        merged = []
        for w in line_words:
            if not merged:
                merged.append(dict(w))
            else:
                prev = merged[-1]
                gap = w["x0"] - prev["x1"]
                if gap < 2.0:
                    prev["text"] += w["text"]
                    prev["x1"] = w["x1"]
                    if len(w["text"]) > len(prev["text"]) - len(w["text"]):
                        prev["fontname"] = w["fontname"]
                else:
                    merged.append(dict(w))
        line_words = merged
        
        # Split line into segments if there is a gap > 18 points
        segments = []
        curr_segment = []
        for i, w in enumerate(line_words):
            if not curr_segment:
                curr_segment.append(w)
            else:
                prev_w = curr_segment[-1]
                gap = w["x0"] - prev_w["x1"]
                if gap > 18: # gap threshold
                    segments.append(curr_segment)
                    curr_segment = [w]
                else:
                    curr_segment.append(w)
        if curr_segment:
            segments.append(curr_segment)
            
        # Convert segments of words to text and find their horizontal range
        segs_info = []
        for seg in segments:
            seg_text = format_words_with_bold(seg)
            seg_x0 = min([w["x0"] for w in seg])
            seg_x1 = max([w["x1"] for w in seg])
            segs_info.append({
                "text": seg_text,
                "x0": seg_x0,
                "x1": seg_x1,
                "cx": (seg_x0 + seg_x1) / 2
            })
            
        # Classify line type (single column vs multi column)
        if len(segs_info) > 1:
            line_type = "multi"
        elif len(segs_info) == 1:
            seg = segs_info[0]
            mid = width / 2
            if seg["x0"] < mid - 20 and seg["x1"] > mid + 20:
                line_type = "single"
            else:
                line_type = "multi"
        else:
            line_type = "single"
            
        lines_segments.append({
            "top": top,
            "segments": segs_info,
            "line_type": line_type
        })
        
    # Group consecutive lines by line_type and vertical gap
    grouped_blocks = []
    curr_block = []
    curr_type = None
    
    for line in lines_segments:
        l_type = line["line_type"]
        l_top = line["top"]
        
        large_gap = False
        if curr_block:
            prev_top = curr_block[-1]["top"]
            if l_top - prev_top > 40:
                large_gap = True
                
        if curr_type is None:
            curr_type = l_type
            curr_block.append(line)
        elif curr_type == l_type and not large_gap:
            curr_block.append(line)
        else:
            grouped_blocks.append((curr_type, curr_block))
            curr_type = l_type
            curr_block = [line]
    if curr_block:
        grouped_blocks.append((curr_type, curr_block))
        
    # Now reconstruct the text block by block
    final_text_lines = []
    images = [img for img in page.images if 40 <= img["top"] <= height - 37]
    # Ignore watermark images that cover more than 85% of page width and height
    images = [img for img in images if (img["x1"] - img["x0"]) < width * 0.85 or (img["bottom"] - img["top"]) < height * 0.85]
    images = sorted(images, key=lambda x: x["top"])
    img_idx = 0
    
    for b_type, block in grouped_blocks:
        block_top = block[0]["top"]
        
        # Insert any images
        while img_idx < len(images) and images[img_idx]["top"] < block_top:
            img = images[img_idx]
            bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
            bbox = (max(0, bbox[0]-2), max(0, bbox[1]-2), min(width, bbox[2]+2), min(height, bbox[3]+2))
            
            image_counter[0] += 1
            img_filename = f"unacademy_p{page.page_number}_img{image_counter[0]}.png"
            img_path = os.path.join(images_dir, img_filename)
            
            try:
                img_crop = page.crop(bbox)
                rendered = img_crop.to_image(resolution=150)
                os.makedirs(images_dir, exist_ok=True)
                rendered.save(img_path, format="PNG")
                final_text_lines.append(f'\n\n<p align="center"><img src="images/{img_filename}" alt="Diagram" /></p>\n\n')
            except Exception as e:
                print(f"Error extracting image {img_filename} on page {page.page_number}: {e}")
                
            img_idx += 1
            
        if b_type == "single":
            block_lines = []
            for line in block:
                if line["segments"]:
                    full_line_text = " ".join([seg["text"] for seg in line["segments"]])
                    block_lines.append(full_line_text)
            final_text_lines.extend(block_lines)
        else:
            left_lines = []
            right_lines = []
            mid = width / 2
            
            for line in block:
                left_segs = []
                right_segs = []
                for seg in line["segments"]:
                    if seg["cx"] < mid:
                        left_segs.append(seg["text"])
                    else:
                        right_segs.append(seg["text"])
                
                line_left = " ".join(left_segs)
                line_right = " ".join(right_segs)
                
                if line_left:
                    left_lines.append(line_left)
                if line_right:
                    right_lines.append(line_right)
                    
            final_text_lines.extend(left_lines)
            final_text_lines.extend(right_lines)
            
    while img_idx < len(images):
        img = images[img_idx]
        bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
        bbox = (max(0, bbox[0]-2), max(0, bbox[1]-2), min(width, bbox[2]+2), min(height, bbox[3]+2))
        
        image_counter[0] += 1
        img_filename = f"unacademy_p{page.page_number}_img{image_counter[0]}.png"
        img_path = os.path.join(images_dir, img_filename)
        
        try:
            img_crop = page.crop(bbox)
            rendered = img_crop.to_image(resolution=150)
            os.makedirs(images_dir, exist_ok=True)
            rendered.save(img_path, format="PNG")
            final_text_lines.append(f'\n\n<p align="center"><img src="images/{img_filename}" alt="Diagram" /></p>\n\n')
        except Exception as e:
            print(f"Error extracting image {img_filename} on page {page.page_number}: {e}")
            
        img_idx += 1
        
    return final_text_lines

def reconstruct_paragraph(lines):
    result = ""
    for line in lines:
        if not result:
            result = line
        else:
            if result.endswith("-"):
                result = result[:-1] + line
            else:
                result = result + " " + line
    return result

def join_paragraph_lines(lines):
    joined = []
    curr_words = []
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        clean_line_strip = line_strip.replace("**", "").strip()
        is_new = False
        if (clean_line_strip.startswith("y ") or 
            clean_line_strip.startswith("- ") or 
            clean_line_strip.startswith("○ ") or 
            clean_line_strip.startswith("● ") or 
            clean_line_strip.startswith("• ") or
            clean_line_strip == "y" or clean_line_strip == "-" or clean_line_strip == "○" or clean_line_strip == "●" or clean_line_strip == "•"):
            is_new = True
        elif (re.match(r'^\d{1,2}\.\s+', clean_line_strip) or
              re.match(r'^[a-zA-Z]\.\s+', clean_line_strip) or
              re.match(r'^\(\d{1,2}\)(?:\s+|$)', clean_line_strip) or
              re.match(r'^\([a-zA-Z]{1,2}\)(?:\s+|$)', clean_line_strip)):
            is_new = True
        elif re.match(r'^(?:Q|q|Question|Case Study|Q\.)\s*\d+', clean_line_strip, re.IGNORECASE):
            is_new = True
        elif clean_line_strip.startswith("#") or clean_line_strip.startswith("<p align=") or (clean_line_strip.endswith(":") and len(clean_line_strip) < 60):
            is_new = True
        # Removed bold heading auto-split to avoid false splits on inline bold segments
            
        if is_new:
            if curr_words:
                joined.append(reconstruct_paragraph(curr_words))
                curr_words = []
            curr_words.append(line_strip)
        else:
            curr_words.append(line_strip)
            
    if curr_words:
        joined.append(reconstruct_paragraph(curr_words))
        
    return joined

if __name__ == '__main__':
    print("Building Subject Reference Database...")
    load_from_dir(drishti_dir)
    load_from_dir(superkalam_dir)
    print(f"Total reference questions loaded: {len(ref_db)}")

    # 3. Main Extraction Process
    questions = []
    image_counter = [0]
    
    print("\nOpening PDF for extraction...")
    with pdfplumber.open(pdf_path) as pdf:
        # Process Year by Year
        for year, (start_page, end_page) in sorted(YEAR_RANGES.items()):
            print(f"\nProcessing Year {year} (Pages {start_page} to {end_page})...")
            
            # Accumulate text for the year's pages
            text_blocks = []
            for page_num in range(start_page, end_page + 1):
                if (page_num - start_page) % 20 == 0 or page_num == end_page:
                    print(f"  Processing page {page_num}/{end_page}...")
                page_idx = page_num - 1
                if page_idx >= len(pdf.pages):
                    break
                page = pdf.pages[page_idx]
                
                page_lines = extract_smart_layout(page, image_counter, images_dir)
                joined_page_lines = join_paragraph_lines(page_lines)
                if joined_page_lines:
                    text_blocks.append("\n".join(joined_page_lines))
                    
            full_text = "\n".join(text_blocks)
            
            # Clean noise lines
            lines = full_text.split("\n")
            cleaned_lines = []
            for line in lines:
                line_strip = line.strip()
                if not line_strip:
                    continue
                if "Previous Year Questions" in line_strip:
                    continue
                if "unacademy.com" in line_strip:
                    continue
                if "Download the Unacademy app" in line_strip:
                    continue
                if "Give your feedback here" in line_strip:
                    continue
                if re.match(r'^\d+\s*$', line_strip): # page number
                    continue
                cleaned_lines.append(line)
                
            # Parse questions and answers for this year
            curr_int = 0
            curr_paper = "GS I"
            papers_seq = ["GS I", "GS II", "GS III", "GS IV"]
            
            year_questions = []
            current_question = None
            
            for idx, line in enumerate(cleaned_lines):
                next_lines = cleaned_lines[idx+1:idx+16]
                if is_question_start(line, next_lines, curr_int):
                    if current_question:
                        year_questions.append(current_question)
                        
                    val, _ = parse_question_num(line.strip(), curr_int)
                    
                    # Determine active paper
                    if val == 1 and curr_int > 1:
                        try:
                            curr_idx = papers_seq.index(curr_paper)
                            curr_paper = papers_seq[curr_idx + 1]
                        except IndexError:
                            pass
                            
                    curr_int = val
                    clean_q_num = get_clean_q_num(line.strip(), curr_int)
                    current_question = {
                        "year": year,
                        "paper": curr_paper,
                        "num_val": val,
                        "clean_num": clean_q_num,
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
                    
                    # Transition to answer if previous line contained words/marks limit
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
                year_questions.append(current_question)
                
            print(f"  Parsed {len(year_questions)} questions for {year}.")
            questions.extend(year_questions)
    
    print(f"\nTotal questions parsed across all years: {len(questions)}")
    
    # 4. Map questions to subjects
    print("\nMapping parsed questions to subjects...")
    mapped_count = 0
    
    for q in questions:
        q_text = " ".join(q["lines"]).strip()
        q_text_clean = strip_q_prefix(q_text, q["clean_num"])
        q_norm = normalize_text(q_text_clean)
        
        # Subject Assignment Rules
        assigned_subject = None
        
        # Rule A: GS IV Subject Assignment is 100% split based on Question Number!
        if q["paper"] == "GS IV":
            if q["num_val"] <= 6:
                assigned_subject = "ethics_theoretical_questions"
            else:
                assigned_subject = "ethics_case_studies"
        else:
            # Rule B: Map GS I, II, III using context filtering (Same Year and Paper)
            candidates = [ref for ref in ref_db if ref["year"] == q["year"] and ref["paper"] == q["paper"]]
            
            best_match_subject = None
            best_match_score = 0.0
            
            w_q = set(q_norm.split())
            for ref in candidates:
                w_ref = set(ref["q_norm"].split())
                if not w_q or not w_ref:
                    continue
                sim = len(w_q.intersection(w_ref)) / len(w_q.union(w_ref))
                if sim > best_match_score:
                    best_match_score = sim
                    best_match_subject = ref["subject"]
                    
            if best_match_score >= 0.35:
                assigned_subject = best_match_subject
            else:
                # Fallback if no match: default to a standard subject for the paper
                print(f"  Warning: Low match score ({best_match_score:.3f}) for Q{q['clean_num']} ({q['year']} {q['paper']}). Text: {q_text[:60].encode('ascii', 'replace').decode('ascii')}")
                if q["paper"] == "GS I":
                    assigned_subject = "geography" # Default GS I
                elif q["paper"] == "GS II":
                    assigned_subject = "polity" # Default GS II
                else:
                    assigned_subject = "economic_development" # Default GS III
                    
        q["subject"] = assigned_subject
        q["clean_q_text"] = q_text_clean
        mapped_count += 1
    
    print(f"Mapped all {mapped_count} questions successfully.")
    
    # 5. Format and write outputs to Markdown files grouped by subject
    print("\nFormatting and writing Markdown files...")
    
    def get_subject_title(subject):
        mapping = {
            "ancient_history_and_art__culture": "Ancient History and Art & Culture",
            "science__technology": "Science & Technology",
            "post_independent_india": "Post-Independent India",
            "international_relations": "International Relations",
            "disaster_management": "Disaster Management",
            "economic_development": "Economic Development",
            "environment_and_ecology": "Environment and Ecology",
            "internal_security": "Internal Security",
            "social_justice": "Social Justice",
            "ethics_theoretical_questions": "Ethics Theoretical Questions",
            "ethics_case_studies": "Ethics Case Studies",
            "indian_society": "Indian Society",
            "modern_history": "Modern History",
            "world_history": "World History",
        }
        return mapping.get(subject, subject.replace("_", " ").title())
    
    def format_answer_content(lines):
        formatted = []
        for line in lines:
            line_strip = line.strip()
            if not line_strip:
                continue
                
            clean_line = line_strip.replace("**", "").strip()
            
            # Format bullet lists
            if clean_line.startswith("y "):
                # Find where the prefix ends in the original line
                idx = line_strip.find("y ")
                if idx != -1:
                    line_strip = "- " + line_strip[idx+2:]
                else:
                    line_strip = "- " + clean_line[2:]
            elif clean_line == "y":
                line_strip = "-"
            elif clean_line.startswith("○ "):
                idx = line_strip.find("○ ")
                if idx != -1:
                    line_strip = "  - " + line_strip[idx+2:]
                else:
                    line_strip = "  - " + clean_line[2:]
            elif clean_line == "○":
                line_strip = "  -"
                
            # Clean subheaders
            if clean_line.lower() in ["introduction:", "introduction :", "introduction"]:
                line_strip = "## **Introduction**"
            elif clean_line.lower() in ["body:", "body :", "body"]:
                line_strip = "## **Body**"
            elif clean_line.lower() in ["conclusion:", "conclusion :", "conclusion"]:
                line_strip = "## **Conclusion**"
            elif clean_line.endswith(":") and len(clean_line) < 60:
                # Other subheaders
                line_strip = f"## **{clean_line[:-1]}**"
                
            formatted.append(line_strip)
            
        return "\n\n".join(formatted)
    
    # Group questions by subject
    questions_by_subject = {}
    for q in questions:
        subj = q["subject"]
        if subj not in questions_by_subject:
            questions_by_subject[subj] = []
        questions_by_subject[subj].append(q)
    
    # Sort and write each subject file
    os.makedirs(output_dir, exist_ok=True)
    
    # Sequence of papers for sorting
    paper_order = {"GS I": 1, "GS II": 2, "GS III": 3, "GS IV": 4}
    
    for subject, subj_qs in questions_by_subject.items():
        # Sort: Year descending, Paper order ascending, Question number ascending
        # For question number, sort by num_val
        subj_qs.sort(key=lambda x: (-x["year"], paper_order.get(x["paper"], 5), x["num_val"], x["clean_num"]))
        
        subject_title = get_subject_title(subject)
        filepath = os.path.join(output_dir, f"{subject}.md")
        
        print(f"Writing {len(subj_qs)} questions to {filepath}...")
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# UPSC Mains Solved Papers - {subject_title} (Unacademy)\n\n")
            f.write(f"This file contains the solved previous year questions extracted from Unacademy.\n\n---\n\n")
            
            for idx, q in enumerate(subj_qs):
                # Question Header
                f.write(f"## Question {q['clean_num']} (Year: {q['year']} | Paper: {q['paper']})\n\n")
                
                # Question Text
                f.write(f"**{q['clean_q_text']}**\n\n")
                
                # Answer Section
                f.write(f"### Answer\n\n")
                
                ans_text = format_answer_content(join_paragraph_lines(q["answer_lines"]))
                f.write(ans_text)
                f.write("\n\n---\n\n")
    
    print("\nAll files successfully extracted and written!")
