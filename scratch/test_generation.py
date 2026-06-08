import os
import re
import pdfplumber
import sys

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

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
    pending_images = []
    
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
            
        clean_line_strip = line_strip.replace("**", "").strip()
        if clean_line_strip.startswith("<p align=") or clean_line_strip.startswith("![Image]"):
            pending_images.append(line_strip)
            continue
            
        is_new = False
        if not curr_words:
            is_new = True
        else:
            prev_line = curr_words[-1].strip()
            clean_prev_line = prev_line.replace("**", "").strip()
            ends_with_terminator = (
                clean_prev_line.endswith(".") or 
                clean_prev_line.endswith("?") or 
                clean_prev_line.endswith("!") or 
                clean_prev_line.endswith(":") or
                clean_prev_line.startswith("|") or
                clean_prev_line.endswith("|")
            )
            if ends_with_terminator:
                is_new = True
        
        if not is_new:
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

def format_answer_content(lines):
    formatted = []
    prev_was_table = False
    for line in lines:
        line_strip = line.strip()
        if not line_strip:
            continue
        clean_line = line_strip.replace("**", "").strip()
        is_table = line_strip.startswith("|")
        
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
            
        if clean_line.lower() in ["introduction:", "introduction :", "introduction"]:
            line_strip = "## **Introduction**"
        elif clean_line.lower() in ["body:", "body :", "body"]:
            line_strip = "## **Body**"
        elif clean_line.lower() in ["conclusion:", "conclusion :", "conclusion"]:
            line_strip = "## **Conclusion**"
        elif clean_line.endswith(":") and len(clean_line) < 60 and not is_table:
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

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\civilsdaily\GS-2 Model Answers (2018-2025).pdf"
with pdfplumber.open(pdf_path) as pdf:
    page = pdf.pages[14]
    page_els = extract_page_elements(page)
    q_start_idx = -1
    for idx, el in enumerate(page_els):
        if "Discuss the nature of Jammu and Kashmir" in el["text"]:
            q_start_idx = idx
            break
            
    if q_start_idx != -1:
        block_elements = page_els[q_start_idx:]
        full_text_block = "\n".join([el["text"] for el in block_elements])
        
        # Test fallback split
        full_text_block_clean = full_text_block.replace("**", "")
        marks_match = re.search(r'\(\d+\)|\b\d+\s*marks?\b', full_text_block_clean[:400])
        clean_split_pos = marks_match.end()
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
        
        # FIX 1: Clean boundary stray bold tag
        while answer_part.startswith("**"):
            if len(answer_part) == 2 or answer_part[2] in " \n\r\t":
                answer_part = answer_part[2:].strip()
            else:
                break
        
        # Extended sub-questions split
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
            
        clean_q_text = re.sub(r'^(\*+)?\s*\d{4}\s*[-–—]\s*', r'\1', question_part).strip()
        
        # FIX 2: Strip outer bold tags from clean_q_text to prevent ****Discuss
        clean_q_text = clean_q_text.strip("*").strip()
        
        q_lines = clean_q_text.split("\n")
        joined_q_lines = join_paragraph_lines(q_lines)
        clean_q_text = "\n\n".join(joined_q_lines)
        
        ans_lines_raw = answer_part.split("\n")
        answer_lines = join_paragraph_lines(ans_lines_raw)
        
        # Test formatting and writing
        q_text = clean_q_text.strip()
        year_val = 2025
        m_marks = re.search(r'(?:\((\d+)\)|\b(\d+)\s*marks?)\s*$', q_text, re.IGNORECASE)
        marks_str = ""
        if m_marks:
            marks_val = m_marks.group(1) or m_marks.group(2)
            marks_str = f"[Marks: {marks_val}]"
            q_text = q_text[:m_marks.start()].strip()
            
        # FIX 3: Strip bold asterisks again from final q_text
        q_text = q_text.strip("*").strip()
            
        final_q_text = f"{q_text} [Year: {year_val}]"
        if marks_str:
            final_q_text += f" {marks_str}"
            
        # Write to test_output.md
        with open("test_output.md", "w", encoding="utf-8") as f:
            f.write(f"## Question test\n\n")
            f.write(f"**{final_q_text}**\n\n")
            f.write(f"### Answer\n\n")
            # FIX 4: Avoid double calling join_paragraph_lines
            ans_text = format_answer_content(answer_lines)
            f.write(ans_text)
            f.write("\n\n---\n\n")
        print("Generated test_output.md successfully with fixes!")
