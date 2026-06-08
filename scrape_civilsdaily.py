import os
import re
import pdfplumber
import sys

# Paths
pdf_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\civilsdaily"
drishti_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\drishti ias"
superkalam_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\superkalam"
output_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\civilsdaily"
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

def normalize_text(text):
    t = text.lower()
    # Clean up hyphenated line breaks in PDF
    t = re.sub(r'-\n\s*', '', t) # Merge hyphenated line breaks
    t = re.sub(r'-', ' ', t)      # Convert other hyphens to spaces
    t = re.sub(r'[\*\(\)\[\]\.,\?:\'";“”\n]', ' ', t)
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
                
                # Remove the question number and year parenthetical prefix from the header block
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
                        count += 1
        print(f"  Loaded {count} questions for subject '{subject}' from {os.path.basename(directory)}")

load_from_dir(drishti_dir)
load_from_dir(superkalam_dir)
print(f"Total reference questions loaded: {len(ref_db)}")

# 3. Subject by Page Range Fallback Lookups
def get_subject_by_page_range(pdf_name, page_num):
    if "GS 1" in pdf_name:
        if 3 <= page_num <= 18:
            return "modern_history"
        elif 19 <= page_num <= 36:
            return "ancient_history_and_art__culture"
        elif 37 <= page_num <= 39:
            return "post_independent_india"
        elif 40 <= page_num <= 45:
            return "world_history"
        elif 46 <= page_num <= 109:
            return "geography"
        else:
            return "indian_society"
    elif "GS-2" in pdf_name:
        if 3 <= page_num <= 82:
            return "polity"
        elif 83 <= page_num <= 110:
            return "governance"
        elif 111 <= page_num <= 136:
            return "social_justice"
        else:
            return "international_relations"
    elif "GS 3" in pdf_name:
        if 3 <= page_num <= 38:
            return "economic_development"
        elif 39 <= page_num <= 79:
            return "agriculture"
        elif 80 <= page_num <= 106:
            return "environment_and_ecology"
        elif 107 <= page_num <= 119:
            return "disaster_management"
        elif 120 <= page_num <= 157:
            return "internal_security"
        else:
            return "science__technology"
    elif "GS 4" in pdf_name:
        if 3 <= page_num <= 101:
            return "ethics_theoretical_questions"
        else:
            return "ethics_case_studies"
    return "unknown"

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

def reconstruct_paragraph(lines):
    result = ""
    for line in lines:
        if not result:
            result = line
        else:
            if result.endswith("-"):
                result = result[:-1] + line
            else:
                if result.endswith("**") and line.startswith("**"):
                    result = result[:-2] + " " + line[2:]
                else:
                    result = result + " " + line
    return result

def is_list_start(line_str):
    clean = line_str.replace("**", "").strip()
    if (clean.startswith("y ") or 
        clean.startswith("- ") or 
        clean.startswith("○ ") or 
        clean.startswith("● ") or 
        clean.startswith("• ") or
        clean == "y" or clean == "-" or clean == "○" or clean == "●" or clean == "•"):
        return True
    if (re.match(r'^\d{1,2}\.\s+', clean) or
        re.match(r'^[a-zA-Z]\.\s+', clean) or
        re.match(r'^\(\d{1,2}\)(?:\s+|$)', clean) or
        re.match(r'^\([a-zA-Z]{1,2}\)(?:\s+|$)', clean)):
        return True
    return False

def join_paragraph_lines(lines):
    joined = []
    curr_words = []
    pending_images = []
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        clean_line_strip = line_strip.replace("**", "").strip()
        
        # Queue image tags to avoid inserting them between text lines of the same paragraph
        if clean_line_strip.startswith("<p align=") or clean_line_strip.startswith("![Image]"):
            pending_images.append(line_strip)
            continue
            
        is_new = False
        
        if not curr_words:
            is_new = True
        else:
            prev_line = curr_words[-1].strip()
            clean_prev_line = prev_line.replace("**", "").strip()
            
            in_list_item = curr_words and is_list_start(curr_words[0])
            
            # Check if previous line ended with a sentence terminator or was a heading
            ends_with_terminator = (
                clean_prev_line.endswith(".") or 
                clean_prev_line.endswith("?") or 
                clean_prev_line.endswith("!") or 
                clean_prev_line.endswith(":") or
                clean_prev_line.startswith("|") or
                clean_prev_line.endswith("|") or
                (not in_list_item and prev_line.startswith("**") and prev_line.endswith("**") and len(prev_line) > 4)
            )
            if ends_with_terminator:
                is_new = True
        
        # Also check current line forcing conditions
        if not is_new:
            # Check standard bullet patterns: ●, •, ○, numbered lists (1., 2., 1), 2)), case studies, etc.
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
            elif clean_line_strip.startswith("#") or clean_line_strip.startswith("|") or clean_line_strip.endswith("|") or (clean_line_strip.endswith(":") and len(clean_line_strip) < 60):
                is_new = True
            elif line_strip.startswith("**") and line_strip.endswith("**") and len(line_strip) > 4:
                # Check if we are currently building a list item
                in_list_item = False
                if curr_words and is_list_start(curr_words[0]):
                    in_list_item = True
                
                # If we are not in a list item, check if it is a subheading
                if not in_list_item:
                    content = line_strip[2:-2].strip()
                    stripped = content.lstrip(" '\"“‘")
                    if stripped and not stripped[0].islower():
                        is_new = True

                
        if is_new:
            if curr_words:
                joined.append(reconstruct_paragraph(curr_words))
                curr_words = []
                if pending_images:
                    joined.extend(pending_images)
                    pending_images = []
            curr_words.append(line_strip)
        else:
            curr_words.append(line_strip)
            
    if curr_words:
        joined.append(reconstruct_paragraph(curr_words))
        
    if pending_images:
        joined.extend(pending_images)
        
    return joined

def format_table_as_markdown(table_data):
    # Standardize all rows to have the same number of columns
    max_cols = max(len(row) for row in table_data if row is not None)
    cleaned_rows = []
    for r in table_data:
        if r is None:
            continue
        # Fill missing columns with empty string
        row_cells = [str(cell or "").strip() for cell in r]
        while len(row_cells) < max_cols:
            row_cells.append("")
        # Replace newlines with <br> to preserve cell formatting
        row_cells = [cell.replace("\n", "<br>").replace("\r", "") for cell in row_cells]
        cleaned_rows.append(row_cells)
        
    if not cleaned_rows:
        return ""
        
    # Build the markdown table
    md_lines = []
    # Header
    md_lines.append("| " + " | ".join(cleaned_rows[0]) + " |")
    # Separator
    md_lines.append("| " + " | ".join(["---"] * max_cols) + " |")
    # Data rows
    for row in cleaned_rows[1:]:
        md_lines.append("| " + " | ".join(row) + " |")
        
    return "\n" + "\n".join(md_lines) + "\n"

def is_real_table(data):
    if not data:
        return False
    rows_count = len(data)
    cols_count = max(len(r) for r in data if r is not None)
    if cols_count <= 1:
        return False
        
    total_cells = 0
    empty_cells = 0
    empty_cols_count = [0] * cols_count
    
    for r in data:
        if r is None:
            continue
        row_cells = list(r)
        while len(row_cells) < cols_count:
            row_cells.append(None)
            
        for c_idx, cell in enumerate(row_cells):
            total_cells += 1
            cell_str = str(cell or "").strip()
            if not cell_str:
                empty_cells += 1
                empty_cols_count[c_idx] += 1
                
    empty_ratio = empty_cells / total_cells if total_cells > 0 else 1.0
    col_empty_ratios = [count / rows_count for count in empty_cols_count]
    
    # Heuristic to detect fake tables:
    # 1. High empty cell ratio overall
    if empty_ratio > 0.20:
        return False
    # 2. Any column that is mostly empty (e.g. > 45% empty)
    if any(r > 0.45 for r in col_empty_ratios):
        return False
        
    return True

# Page content extraction: Reconstructs reading order and extracts diagrams by vertical positioning
def extract_page_elements(page, image_counter, images_dir):
    # 1. Detect multi-column tables first
    tables = page.find_tables()
    valid_tables = []
    table_bboxes = []
    for t in tables:
        data = t.extract()
        if not data:
            continue
        max_cols = max(len(row) for row in data if row is not None)
        if max_cols > 1 and is_real_table(data):
            valid_tables.append((t, data))
            table_bboxes.append(t.bbox)

    words = page.extract_words(extra_attrs=["fontname"])
    
    # 2. Filter out words that fall inside any valid table bounding boxes
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
        
        # Merge split words (e.g. from overlapping bold markers or font changes)
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
        
    # Add table markdown elements
    for t, data in valid_tables:
        table_md = format_table_as_markdown(data)
        elements.append({
            "type": "text",
            "top": t.bbox[1],
            "text": table_md
        })
        
    for img in page.images:
        # Ignore full-page watermark images
        img_width = img["x1"] - img["x0"]
        img_height = img["bottom"] - img["top"]
        if img_width > page.width * 0.85 and img_height > page.height * 0.85:
            continue
        elements.append({
            "type": "image",
            "top": img["top"],
            "img_obj": img
        })
            
    elements.sort(key=lambda x: x["top"])
    
    output_elements = []
    for item in elements:
        if item["type"] == "text":
            output_elements.append(item)
        elif item["type"] == "image":
            img = item["img_obj"]
            bbox = (img["x0"], img["top"], img["x1"], img["bottom"])
            w_page, h_page = page.width, page.height
            bbox = (max(0, bbox[0]-2), max(0, bbox[1]-2), min(w_page, bbox[2]+2), min(h_page, bbox[3]+2))
            
            image_counter[0] += 1
            img_filename = f"civilsdaily_p{page.page_number}_img{image_counter[0]}.png"
            img_path = os.path.join(images_dir, img_filename)
            
            try:
                img_crop = page.crop(bbox)
                rendered = img_crop.to_image(resolution=150)
                os.makedirs(images_dir, exist_ok=True)
                rendered.save(img_path, format="PNG")
                img_markdown = f'\n\n<p align="center"><img src="images/{img_filename}" alt="Diagram" /></p>\n\n'
                output_elements.append({
                    "type": "image",
                    "top": item["top"],
                    "text": img_markdown
                })
            except Exception as e:
                print(f"Error extracting image {img_filename} on page {page.page_number}: {e}")
                
    return output_elements

# 4. Processing PDFs
pdfs = [
    {"filename": "GS 1 Model Answers (2018-2025).pdf", "paper": "GS I"},
    {"filename": "GS-2 Model Answers (2018-2025).pdf", "paper": "GS II"},
    {"filename": "GS 3 Model Answers (2018-2025).pdf", "paper": "GS III"},
    {"filename": "GS 4 Model Answers (2018-2025).pdf", "paper": "GS IV"}
]

all_extracted_questions = []
image_counter = [0]

for pdf_info in pdfs:
    filename = pdf_info["filename"]
    paper = pdf_info["paper"]
    path = os.path.join(pdf_dir, filename)
    if not os.path.exists(path):
        print(f"File {filename} not found at {path}. Skipping.")
        continue
        
    print(f"\n======================================")
    print(f"Processing PDF: {filename} ({paper})")
    print(f"======================================")
    
    with pdfplumber.open(path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        # Accumulate elements page-by-page from Page 3 to end
        pdf_elements = []
        for p_idx in range(2, len(pdf.pages)):
            page_num = p_idx + 1
            if page_num % 10 == 0 or page_num == len(pdf.pages):
                print(f"  Reading elements from page {page_num}/{len(pdf.pages)}...")
            page = pdf.pages[p_idx]
            page_els = extract_page_elements(page, image_counter, images_dir)
            for el in page_els:
                el["page_num"] = page_num
            pdf_elements.extend(page_els)
            
        print(f"  Loaded {len(pdf_elements)} elements from PDF.")
        
        # Group elements into questions
        questions_blocks = []
        current_block = None
        active_year = None
        expecting_first_case_study = False
        
        for el in pdf_elements:
            if el["type"] == "text":
                line_strip = el["text"].strip()
                clean_line_strip = line_strip.replace("**", "").strip()
                
                m_year_only = re.match(r'^(2018|2019|2020|2021|2022|2023|2024|2025)$', clean_line_strip)
                m_q_start = re.match(r'^(2018|2019|2020|2021|2022|2023|2024|2025)\s*-\s*(.*)', clean_line_strip)
                m_cs_start = re.match(r'^[^\w\[]*\[Case Study\s*(\d+)\]\s*(.*)', clean_line_strip, re.IGNORECASE)
                
                is_new_q = False
                year_to_assign = None
                
                if m_q_start:
                    is_new_q = True
                    active_year = int(m_q_start.group(1))
                    year_to_assign = active_year
                    expecting_first_case_study = False
                elif m_year_only:
                    active_year = int(m_year_only.group(1))
                    if paper == "GS IV" and el["page_num"] >= 102:
                        expecting_first_case_study = True
                    continue # Skip appending this year header line to elements
                elif m_cs_start:
                    is_new_q = True
                    year_to_assign = active_year
                    expecting_first_case_study = False
                elif expecting_first_case_study:
                    is_new_q = True
                    year_to_assign = active_year
                    expecting_first_case_study = False
                    
                if is_new_q:
                    if current_block:
                        questions_blocks.append(current_block)
                    current_block = {
                        "year": year_to_assign if year_to_assign else (active_year if active_year else 2025),
                        "paper": paper,
                        "start_page": el["page_num"],
                        "elements": [el]
                    }
                    continue
            
            if current_block:
                current_block["elements"].append(el)
                
        if current_block:
            questions_blocks.append(current_block)
            
        print(f"  Parsed {len(questions_blocks)} raw question blocks from PDF.")
        
        # Split and map each question block
        for idx, block in enumerate(questions_blocks):
            year = block["year"]
            # Filter noise lines from the elements text
            filtered_elements = []
            for el in block["elements"]:
                if el["type"] == "text":
                    text_strip = el["text"].strip()
                    if not text_strip:
                        continue
                    if "civilsdaily.com" in text_strip.lower():
                        continue
                    if re.match(r'^\d+$', text_strip): # isolated page number
                        continue
                    if "model answers" in text_strip.lower():
                        continue
                    filtered_elements.append(el)
                else: # image markdown
                    filtered_elements.append(el)
            
            # Form full text block for similarity search and splitting
            full_text_block = "\n".join([el["text"] for el in filtered_elements])
            
            # Find the best match from the reference database
            candidates = [ref for ref in ref_db if ref["year"] == year and ref["paper"] == paper]
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
                if score > best_score:
                    best_score = score
                    best_ref = ref
                elif score == best_score and best_ref is not None:
                    # Tie-breaker: prefer the longer raw question text
                    if len(ref["q_text"]) > len(best_ref["q_text"]):
                        best_ref = ref
            
            assigned_subject = None
            split_idx = -1
            
            if best_ref and best_score > 0.50:
                assigned_subject = best_ref["subject"]
                # Split at the last words of the reference question
                # Extract clean tokens from the reference question
                cleaned_ref_tokens = re.findall(r'[a-zA-Z0-9]+', best_ref["q_text"])
                stop_words = {
                    "the", "of", "and", "to", "in", "is", "that", "for", "on", "with", 
                    "as", "at", "by", "an", "be", "this", "are", "from", "it", "its", 
                    "words", "marks", "word", "mark", "a", "or", "which", "how", "what", 
                    "who", "whose", "whom", "where", "when", "why", "if", "then", "else"
                }
                filtered_ref_tokens = []
                for w in cleaned_ref_tokens:
                    w_low = w.lower()
                    if w_low not in stop_words and len(w) > 2 and not w.isdigit():
                        filtered_ref_tokens.append(w)
                last_words = filtered_ref_tokens[-4:]
                if not last_words:
                    last_words = [w for w in best_ref["q_text"].split()[-3:] if len(w) > 2]
                
                # Dynamic search area to handle long case study scenarios
                clean_ref_q = best_ref["q_text"].strip()
                clean_ref_q = re.sub(r'\s*\([^)]*\)\s*$', '', clean_ref_q)
                clean_ref_q = re.sub(r'\s*\[[^\]]*\]\s*$', '', clean_ref_q)
                clean_ref_q = re.sub(r'\s*\b\d+\s*(?:words?|marks?)\b\s*$', '', clean_ref_q, flags=re.IGNORECASE)
                clean_ref_q = re.sub(r'\s*\b(?:answer in|words|marks)\b\s*$', '', clean_ref_q, flags=re.IGNORECASE)
                expected_len = len(clean_ref_q.strip())
                search_area_len = max(500, expected_len + 200)
                search_area = full_text_block_clean[:search_area_len]
                best_match_pos = -1
                for word in reversed(last_words):
                    # Find all occurrences of the word and pick the one closest to the expected question length
                    m = list(re.finditer(r'\b' + re.escape(word) + r'\b', search_area, re.IGNORECASE))
                    if m:
                        best_m = min(m, key=lambda x: abs(x.end() - expected_len))
                        best_match_pos = best_m.end()
                        break
                        
                if best_match_pos != -1:
                    marks_match = re.search(r'\(\d+\)|\b\d+\s*marks?\b', search_area[best_match_pos:best_match_pos+40])
                    if marks_match:
                        clean_split_pos = best_match_pos + marks_match.end()
                    else:
                        clean_split_pos = best_match_pos
                        
                    # Map clean_split_pos back to split_idx in full_text_block
                    orig_chars = 0
                    clean_chars = 0
                    while clean_chars < clean_split_pos and orig_chars < len(full_text_block):
                        if full_text_block[orig_chars:orig_chars+2] == "**":
                            orig_chars += 2
                        else:
                            orig_chars += 1
                            clean_chars += 1
                    split_idx = orig_chars
            
            # Fallback if no match or split fails
            if not assigned_subject:
                assigned_subject = get_subject_by_page_range(filename, block["start_page"])
                
            if split_idx == -1:
                # Fallback splitting: search for marks pattern or first paragraph break
                marks_match = re.search(r'\(\d+\)|\b\d+\s*marks?\b', full_text_block_clean[:400])
                if marks_match:
                    clean_split_pos = marks_match.end()
                else:
                    clean_split_pos = full_text_block_clean.find("\n")
                    if clean_split_pos == -1:
                        clean_split_pos = 100 # arbitrary boundary
                        
                # Map clean_split_pos back to split_idx in full_text_block
                orig_chars = 0
                clean_chars = 0
                while clean_chars < clean_split_pos and orig_chars < len(full_text_block):
                    if full_text_block[orig_chars:orig_chars+2] == "**":
                        orig_chars += 2
                    else:
                        orig_chars += 1
                        clean_chars += 1
                split_idx = orig_chars
                        
            question_part = full_text_block[:split_idx].strip()
            answer_part = full_text_block[split_idx:].strip()
            
            # Clean stray bold markers at the boundary between question and answer
            while answer_part.startswith("**"):
                if len(answer_part) == 2 or answer_part[2] in " \n\r\t":
                    answer_part = answer_part[2:].strip()
                else:
                    break
            
            # Sub-question extension: include trailing (a), (b), (c) lists into the question
            ans_lines = answer_part.split("\n")
            q_extend_lines = []
            ans_start_idx = 0
            for line in ans_lines:
                line_strip = line.strip()
                if not line_strip:
                    ans_start_idx += 1
                    continue
                clean_line_strip = line_strip.replace("**", "").strip()
                if re.match(r'^(\([a-d0-9]\)|[a-d0-9]\))', clean_line_strip, re.IGNORECASE):
                    q_extend_lines.append(line)
                    ans_start_idx += 1
                else:
                    break
            if q_extend_lines:
                question_part = question_part + "\n" + "\n".join(q_extend_lines)
                answer_part = "\n".join(ans_lines[ans_start_idx:])
                
            # Clean year-hyphen prefix from the question text (taking bold asterisks into account)
            clean_q_text = re.sub(r'^(\*+)?\s*\d{4}\s*[-–—]\s*', r'\1', question_part).strip()
            # Strip outer bold tags from clean_q_text to prevent ****Discuss
            clean_q_text = clean_q_text.strip("*").strip()
            
            # Join consecutive lines in the question text
            q_lines = clean_q_text.split("\n")
            joined_q_lines = join_paragraph_lines(q_lines)
            clean_q_text = "\n\n".join(joined_q_lines)
            
            # Split answer lines and join consecutive lines into proper paragraphs
            ans_lines_raw = answer_part.split("\n")
            answer_lines = join_paragraph_lines(ans_lines_raw)
            
            all_extracted_questions.append({
                "year": year,
                "paper": paper,
                "subject": assigned_subject,
                "question": clean_q_text,
                "answer_lines": answer_lines
            })

print(f"\nTotal questions successfully extracted: {len(all_extracted_questions)}")

# 5. Format and Write Outputs to Markdown Files grouped by Subject
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
    prev_was_table = False
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        clean_line = line_strip.replace("**", "").strip()
        is_table = line_strip.startswith("|")
        
        # Format bullet lists
        if clean_line.startswith("● "):
            idx = line_strip.find("● ")
            if idx != -1:
                line_strip = "- " + line_strip[idx+2:]
            else:
                line_strip = "- " + clean_line[2:]
        elif clean_line.startswith("• "):
            idx = line_strip.find("• ")
            if idx != -1:
                line_strip = "- " + line_strip[idx+2:]
            else:
                line_strip = "- " + clean_line[2:]
        elif clean_line.startswith("○ "):
            idx = line_strip.find("○ ")
            if idx != -1:
                line_strip = "  - " + line_strip[idx+2:]
            else:
                line_strip = "  - " + clean_line[2:]
        elif clean_line == "●" or clean_line == "•":
            line_strip = "-"
        elif clean_line == "○":
            line_strip = "  -"
            
        # Clean subheaders
        if clean_line.lower() in ["introduction:", "introduction :", "introduction"]:
            line_strip = "## **Introduction**"
        elif clean_line.lower() in ["body:", "body :", "body"]:
            line_strip = "## **Body**"
        elif clean_line.lower() in ["conclusion:", "conclusion :", "conclusion"]:
            line_strip = "## **Conclusion**"
        elif clean_line.endswith(":") and len(clean_line) < 60 and not is_table:
            # Other subheaders
            line_strip = f"## **{clean_line[:-1]}**"
            
        if formatted:
            if is_table and prev_was_table:
                formatted[-1] = formatted[-1] + "\n" + line_strip
            else:
                formatted.append(line_strip)
        else:
            formatted.append(line_strip)
            
        prev_was_table = is_table
        
    return "\n\n".join(formatted)

# Group questions by subject
questions_by_subject = {}
for q in all_extracted_questions:
    subj = q["subject"]
    if subj not in questions_by_subject:
        questions_by_subject[subj] = []
    questions_by_subject[subj].append(q)

# Write each subject file in its original extraction sequence
os.makedirs(output_dir, exist_ok=True)

for subject, subj_qs in questions_by_subject.items():
    # Keep the original order of questions as they appeared in the Civilsdaily PDFs
    # No sorting is needed since all_extracted_questions was populated in sequential PDF page order.
    
    subject_title = get_subject_title(subject)
    filepath = os.path.join(output_dir, f"{subject}.md")
    
    print(f"Writing {len(subj_qs)} questions to {filepath}...")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# UPSC Mains Solved Papers - {subject_title} (Civilsdaily)\n\n")
        f.write(f"This file contains the solved previous year questions extracted from Civilsdaily.\n\n---\n\n")
        
        for idx, q in enumerate(subj_qs):
            # Question Header
            f.write(f"## Question {idx + 1} (Year: {q['year']} | Paper: {q['paper']})\n\n")
            
            # Question Text & Marks Extraction
            q_text = q['question'].strip()
            year_val = q['year']
            
            # Try to match marks pattern like (10), (15), 10 marks at the end of question
            m_marks = re.search(r'(?:\((\d+)\)|\b(\d+)\s*marks?)\s*$', q_text, re.IGNORECASE)
            marks_str = ""
            if m_marks:
                marks_val = m_marks.group(1) or m_marks.group(2)
                marks_str = f"[Marks: {marks_val}]"
                q_text = q_text[:m_marks.start()].strip()
            else:
                m_marks_any = re.search(r'(?:\((\d+)\)|\b(\d+)\s*marks?)', q_text[-50:], re.IGNORECASE)
                if m_marks_any:
                    marks_val = m_marks_any.group(1) or m_marks_any.group(2)
                    marks_str = f"[Marks: {marks_val}]"
                    sub_start = len(q_text) - 50 + m_marks_any.start()
                    q_text = (q_text[:sub_start] + q_text[len(q_text) - 50 + m_marks_any.end():]).strip()
            
            # Strip outer bold asterisks again from final q_text
            q_text = q_text.strip("*").strip()
            
            final_q_text = f"{q_text} [Year: {year_val}]"
            if marks_str:
                final_q_text += f" {marks_str}"
                
            f.write(f"**{final_q_text}**\n\n")
            
            # Answer Section
            f.write(f"### Answer\n\n")
            
            ans_text = format_answer_content(q["answer_lines"])
            f.write(ans_text)
            f.write("\n\n---\n\n")

print("\nAll files successfully extracted and written!")
