import os
import re
import html
import sys
from fpdf import FPDF

class SolvedPapersPDF(FPDF):
    def __init__(self, title_text="UPSC Mains Solved Papers", *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_text = title_text

    def header(self):
        # Header text
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, self.title_text, align="L")
        self.ln(10)
        # Horizontal line
        self.set_draw_color(200, 200, 200)
        self.line(15, 18, 195, 18)

    def footer(self):
        # Footer text
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def clean_text_for_pdf(text):
    """Normalize unicode characters to latin-1 equivalents to prevent FPDF encoding crashes."""
    replacements = {
        "\u2022": chr(149), # Map unicode bullet to PDF bullet character
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2026": "...",
        "\xa0": " ",
        "\u200b": ""
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    # Ensure it's strictly latin-1 compatible
    return text.encode('latin-1', 'replace').decode('latin-1')

def write_rich_text(pdf, text, line_height=5):
    # Splits by double asterisks to toggle bold text
    parts = text.split("**")
    for idx, part in enumerate(parts):
        # Unescape HTML entities and clean for PDF
        part_clean = clean_text_for_pdf(html.unescape(part))
        if idx % 2 == 1:
            pdf.set_font(style="B")
        else:
            pdf.set_font(style="")
        pdf.write(line_height, part_clean)
    # Reset to regular font style at the end of the text block
    pdf.set_font(style="")

def is_subheading_line(line_str):
    line_str = line_str.strip()
    if line_str.startswith("**") and line_str.endswith("**") and len(line_str) > 4:
        content = line_str[2:-2].strip()
        # Must be entirely bolded (exactly one opening and one closing marker)
        if line_str.count("**") != 2:
            return False
        # Subheadings do not end with punctuation like periods, commas, question/exclamation marks, or parentheses
        if content.endswith(".") or content.endswith("?") or content.endswith("!") or content.endswith(")") or content.endswith(","):
            return False
        # Ensure it doesn't start with numbers (e.g. "1. ") or bullets
        if re.match(r'^\d+\.', content):
            return False
        if content.startswith("-") or content.startswith("*"):
            return False
        # Allow longer subheading text (up to 120 characters)
        if len(content) > 120:
            return False
            
        # Heading must start with an uppercase letter or digit, not a lowercase letter
        stripped = content.lstrip(" '\"“‘")
        if stripped and stripped[0].islower():
            return False
            
        # Single-word subheadings must be in a standard allowed list of section header keywords
        words = content.split()
        if len(words) == 1:
            allowed_keywords = {
                "challenges", "significance", "opportunities", "introduction",
                "conclusion", "background", "status", "overview", "context",
                "issues", "measures", "scope", "implications", "recommendations",
                "benefits", "objectives", "concerns"
            }
            if words[0].lower() not in allowed_keywords:
                return False
                
        return True
    return False

def clean_question_text(text):
    # Remove any multiple asterisks
    text = re.sub(r'\*+', '', text)
    # Remove leading year prefix (e.g. "2024 - " or "2021 — ")
    text = re.sub(r'^\d{4}\s*[-–—]\s*', '', text)
    return text.strip()

def draw_question_box(pdf, text):
    # 1. Clean the text
    q_text = clean_text_for_pdf(clean_question_text(text))
    
    # 2. Save current state
    y_start = pdf.get_y()
    
    # 3. Calculate height using dry run
    pdf.set_font("Helvetica", "B", 10.5)
    line_height = 5.5
    h = pdf.multi_cell(w=170, h=line_height, text=q_text, dry_run=True, output='HEIGHT')
    # Add padding (top/bottom padding of 3.5mm)
    padding = 3.5
    box_h = h + (padding * 2)
    
    # Check if there is enough space on the page, if not, add page
    remaining_height = 297 - 15 - pdf.get_y()
    if box_h > remaining_height:
        pdf.add_page()
        y_start = pdf.get_y()
        
    # 4. Draw background box
    # Fill color: soft cream/yellow RGB(252, 248, 227)
    pdf.set_fill_color(252, 248, 227)
    pdf.rect(15, y_start, 180, box_h, style="F")
    
    # Draw vertical gold/brown accent line on the left side
    # Accent color: RGB(189, 140, 54)
    pdf.set_fill_color(189, 140, 54)
    pdf.rect(15, y_start, 1.5, box_h, style="F")
    
    # Draw thin borders on top, right, bottom (light gold color RGB(248, 236, 184))
    pdf.set_draw_color(248, 236, 184)
    pdf.set_line_width(0.3)
    pdf.line(16.5, y_start, 195, y_start)
    pdf.line(195, y_start, 195, y_start + box_h)
    pdf.line(16.5, y_start + box_h, 195, y_start + box_h)
    
    # Reset line width
    pdf.set_line_width(0.2)
    
    # 5. Write the text
    pdf.set_xy(20, y_start + padding)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(51, 51, 51)
    
    pdf.multi_cell(w=170, h=line_height, text=q_text, border=0, fill=False)
    
    # Set y to the end of the box plus some spacing
    pdf.set_y(y_start + box_h)
    pdf.ln(5)

def process_markdown_line(pdf, line, md_file):
    line_stripped = line.strip()
    if not line_stripped:
        pdf.ln(3)
        return

    # Check for document main title
    if line.startswith("# "):
        title = clean_text_for_pdf(line[2:].strip())
        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(27, 85, 131) # Royal Blue
        pdf.write(10, title)
        pdf.ln(15)
        return

    # Skip question and answer headers because they are handled in the main loop
    if line.startswith("## Question") or line.startswith("### Answer"):
        return

    # Check for other second-level headings
    if line.startswith("## "):
        h2 = clean_text_for_pdf(line[3:].strip().replace("**", "")) # Remove bold markup in headers
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(27, 85, 131) # Royal Blue
        pdf.ln(4)
        pdf.write(6, h2)
        pdf.ln(8)
        return

    # Check for third-level headings
    if line.startswith("### "):
        h3 = clean_text_for_pdf(line[4:].strip().replace("**", ""))
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(27, 85, 131) # Royal Blue
        pdf.ln(3)
        pdf.write(6, h3)
        pdf.ln(8)
        return

    # Skip online image embed tags
    if line_stripped.startswith("![Image]"):
        return

    # Check for HTML image tags (e.g. from Civilsdaily output)
    if "<img src=" in line_stripped:
        match = re.search(r'src="images/(.*?)"', line_stripped)
        if match:
            filename = match.group(1)
            img_path = os.path.join(os.path.dirname(md_file), "images", filename)
            if os.path.exists(img_path):
                pdf.ln(5)
                print(f"  Attempting to load image: {img_path}")
                from PIL import Image
                try:
                    with Image.open(img_path) as img:
                        img_w, img_h = img.size
                    w_render = 140
                    h_render = (img_h / img_w) * w_render
                    
                    # Page size check: A4 is 297mm high, bottom margin is 15mm. Trigger page break at 270mm.
                    if pdf.get_y() + h_render > 270:
                        pdf.add_page()
                        
                    pdf.image(img_path, x=35, w=w_render)
                    pdf.set_y(pdf.get_y() + h_render)
                except Exception as e:
                    print(f"Error drawing image: {e}")
                    pdf.image(img_path, x=35, w=140)
                pdf.ln(5)
            else:
                print(f"Warning: Image file not found at {img_path}")
        return

    # Check for local image backup link
    if "[View Offline Local Backup]" in line_stripped:
        match = re.search(r'\(images/(.*?)\)', line_stripped)
        if match:
            filename = match.group(1)
            img_path = os.path.join(os.path.dirname(md_file), "images", filename)
            if os.path.exists(img_path):
                pdf.ln(5)
                print(f"  Attempting to load image: {img_path}")
                from PIL import Image
                try:
                    with Image.open(img_path) as img:
                        img_w, img_h = img.size
                    w_render = 120
                    h_render = (img_h / img_w) * w_render
                    
                    if pdf.get_y() + h_render > 270:
                        pdf.add_page()
                        
                    pdf.image(img_path, x=45, w=w_render)
                    pdf.set_y(pdf.get_y() + h_render)
                except Exception as e:
                    print(f"Error drawing local backup image: {e}")
                    pdf.image(img_path, x=45, w=120)
                pdf.ln(5)
            else:
                print(f"Warning: Image file not found at {img_path}")
        return

    # Check for subheadings inside answers (bold lines with no leading number/bullet)
    if is_subheading_line(line_stripped):
        subheading_text = line_stripped[2:-2].strip()
        pdf.set_font("Helvetica", "B", 11.5)
        pdf.set_text_color(27, 85, 131) # Royal Blue
        pdf.ln(4)
        pdf.write(5.5, clean_text_for_pdf(subheading_text))
        pdf.ln(6)
        return

    # Check for digit with period list (e.g. "1. ", "2. ")
    if re.match(r'^\d+\.\s', line_stripped):
        prefix_match = re.match(r'^\d+\.\s*', line_stripped)
        prefix = prefix_match.group(0)
        list_text = line_stripped[len(prefix):].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(15) # Standard margin (level 0)
        pdf.write(5, prefix)
        write_rich_text(pdf, list_text)
        pdf.ln(5)
        pdf.set_x(15)
        return

    # Check for letter/digit with parenthesis list (e.g. "a) ", "b) ", "1) ")
    if re.match(r'^[a-z0-9]\)\s', line_stripped, re.IGNORECASE) or re.match(r'^[ivx]+\)\s', line_stripped, re.IGNORECASE):
        prefix_match = re.match(r'^([a-z0-9]\)|[ivx]+\))\s*', line_stripped, re.IGNORECASE)
        prefix = prefix_match.group(0)
        list_text = line_stripped[len(prefix):].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(20) # Indented level 1
        pdf.write(5, prefix)
        write_rich_text(pdf, list_text)
        pdf.ln(5)
        pdf.set_x(15)
        return

    # Check for letter/digit with period list (e.g. "a. ", "b. ", "i. ")
    if re.match(r'^[a-z0-9]\.\s', line_stripped, re.IGNORECASE) or re.match(r'^[ivx]+\.\s', line_stripped, re.IGNORECASE):
        prefix_match = re.match(r'^([a-z0-9]\.|[ivx]+\.)\s*', line_stripped, re.IGNORECASE)
        prefix = prefix_match.group(0)
        list_text = line_stripped[len(prefix):].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(26) # Indented level 2 (sub-items under bullet)
        pdf.write(5, prefix)
        write_rich_text(pdf, list_text)
        pdf.ln(5)
        pdf.set_x(15)
        return

    # Handle bullet points
    bullet_char = chr(149)
    # Level 2 indentation (4 spaces or more)
    if line.startswith("    - ") or line.startswith("    * "):
        bullet_text = line.split("- ", 1)[-1].split("* ", 1)[-1].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(28) # Shift indent right
        pdf.write(5, bullet_char + "  ")
        write_rich_text(pdf, bullet_text)
        pdf.ln(5)
        pdf.set_x(15) # Reset margin
        return
        
    if line.startswith("  - ") or line.startswith("  * "):
        bullet_text = line.split("- ", 1)[-1].split("* ", 1)[-1].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(24) # Shift indent right
        pdf.write(5, bullet_char + "  ")
        write_rich_text(pdf, bullet_text)
        pdf.ln(5)
        pdf.set_x(15) # Reset margin
        return

    if line.startswith("- ") or line.startswith("* "):
        bullet_text = line[2:].strip()
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(51, 51, 51)
        pdf.set_x(22)
        pdf.write(5, bullet_char + "  ")
        write_rich_text(pdf, bullet_text)
        pdf.ln(5)
        pdf.set_x(15)
        return

    # Default paragraph text
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(51, 51, 51)
    write_rich_text(pdf, line_stripped)
    pdf.ln(5)

def render_table(pdf, table_lines):
    clean_lines = [l.strip() for l in table_lines if '---' not in l]
    if not clean_lines:
        return
        
    rows = []
    for line in clean_lines:
        parts = [p.strip() for p in line.split('|')]
        if parts and parts[0] == '':
            parts = parts[1:]
        if parts and parts[-1] == '':
            parts = parts[:-1]
        if parts:
            rows.append(parts)
            
    if not rows:
        return

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(51, 51, 51)
    
    try:
        with pdf.table(width=180, col_widths=None) as t:
            for row_idx, r in enumerate(rows):
                row_cells = t.row()
                for cell_text in r:
                    clean_cell = cell_text.replace("<br>", "\n").replace("&lt;br&gt;", "\n").replace("<br/>", "\n")
                    clean_cell = clean_text_for_pdf(html.unescape(clean_cell))
                    clean_cell = clean_cell.replace("**", "")
                    
                    if row_idx == 0:
                        pdf.set_font("Helvetica", "B", 10)
                        from fpdf.fonts import FontFace
                        header_style = FontFace(emphasis="BOLD", fill_color=(240, 240, 240))
                        row_cells.cell(clean_cell.strip(), style=header_style)
                    else:
                        pdf.set_font("Helvetica", "", 9)
                        row_cells.cell(clean_cell.strip())
    except ValueError as ve:
        print(f"  Warning: Table row too high to render as PDF table. Falling back to text rendering. Info: {ve}")
        pdf.set_draw_color(220, 220, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(2)
        for row_idx, r in enumerate(rows):
            # Print each cell's text sequentially or side-by-side
            if row_idx == 0:
                pdf.set_font("Helvetica", "B", 9.5)
                pdf.set_text_color(27, 85, 131) # Royal blue for headers
            else:
                pdf.set_font("Helvetica", "", 9)
                pdf.set_text_color(80, 80, 80)
            
            # Format row content
            row_parts = []
            for col_idx, cell_text in enumerate(r):
                clean_cell = cell_text.replace("<br>", "\n").replace("&lt;br&gt;", "\n").replace("<br/>", "\n")
                clean_cell = clean_text_for_pdf(html.unescape(clean_cell)).strip()
                if clean_cell:
                    row_parts.append(f"Column {col_idx+1}: {clean_cell}")
            
            row_text = "\n".join(row_parts)
            if row_text:
                pdf.multi_cell(w=180, h=5, text=row_text)
                pdf.ln(2)
        pdf.set_draw_color(220, 220, 220)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(3)
    pdf.ln(5)

def is_list_line(line_str):
    line_str = line_str.strip()
    if not line_str:
        return False
    if line_str.startswith("- ") or line_str.startswith("* "):
        return True
    if re.match(r'^\d+\.\s', line_str):
        return True
    return False

def preprocess_markdown_lines(lines):
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        line_stripped = line.strip()
        
        # Check if the line is entirely bolded
        if line_stripped.startswith("**") and line_stripped.endswith("**") and len(line_stripped) > 4:
            current_text = line_stripped[2:-2].strip()
            j = i + 1
            while j < len(lines):
                next_line = lines[j]
                next_line_stripped = next_line.strip()
                if not next_line_stripped:
                    j += 1
                    continue
                if next_line_stripped.startswith("**") and next_line_stripped.endswith("**") and len(next_line_stripped) > 4:
                    next_text = next_line_stripped[2:-2].strip()
                    if re.match(r'^\d+\.', next_text) or re.match(r'^\d+\.', current_text):
                        break
                    
                    # Detect if there was a blank line in between
                    has_blank = False
                    for k in range(i + 1, j):
                        if not lines[k].strip():
                            has_blank = True
                            break
                    # If separated by a blank line, only merge if the next block starts with a lowercase letter (grammatical continuation)
                    if has_blank and next_text and next_text[0].isupper():
                        break
                        
                    current_text += " " + next_text
                    i = j
                    j += 1
                else:
                    break
            new_lines.append("**" + current_text + "**\n")
        else:
            new_lines.append(line)
        i += 1
    return new_lines

def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_to_pdf.py <path_to_markdown_file> [path_to_output_pdf]")
        return
        
    md_file = sys.argv[1]
    if len(sys.argv) >= 3:
        pdf_file = sys.argv[2]
    else:
        pdf_file = md_file.replace(".md", ".pdf")
        
    if not os.path.exists(md_file):
        print(f"Error: Markdown file {md_file} does not exist.")
        return
        
    # Generate dynamic title from markdown header or filename
    title_text = "UPSC Mains Solved Papers"
    try:
        with open(md_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("# "):
                    title_text = line[2:].strip()
                    break
    except Exception:
        pass
        
    print(f"Reading {md_file}...")
    with open(md_file, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()
        
    lines = preprocess_markdown_lines(raw_lines)
        
    # FPDF setup
    pdf = SolvedPapersPDF(title_text=title_text, orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    pdf.set_auto_page_break(True, margin=15)
    
    in_table = False
    table_lines = []
    
    in_question = False
    question_lines = []
    
    print("Converting Markdown lines to PDF elements...")
    for idx, line in enumerate(lines):
        line_stripped = line.strip()
        
        # Detect table start/content
        if line_stripped.startswith("|"):
            if in_question:
                # If we hit table while collecting question, render question first
                in_question = False
                draw_question_box(pdf, " ".join(question_lines))
                question_lines = []
            in_table = True
            table_lines.append(line)
            continue
        elif in_table:
            in_table = False
            render_table(pdf, table_lines)
            table_lines = []
            
        if not line_stripped:
            if in_question:
                continue
            
            # Skip empty lines adjacent to list items to keep lists compact
            prev_non_empty = ""
            for i in range(idx - 1, -1, -1):
                if lines[i].strip():
                    prev_non_empty = lines[i].strip()
                    break
            next_non_empty = ""
            for i in range(idx + 1, len(lines)):
                if lines[i].strip():
                    next_non_empty = lines[i].strip()
                    break
                    
            if is_list_line(prev_non_empty) or is_list_line(next_non_empty):
                continue
                
        # Detect Question start
        if line_stripped.startswith("## Question"):
            if in_question:
                # Flush previous question if not closed (should not happen)
                draw_question_box(pdf, " ".join(question_lines))
            in_question = True
            pdf.add_page()
            
            # Write Question Header e.g. "Question 8 (Year: 2021 | Paper: GS I)"
            q_header = clean_text_for_pdf(line_stripped[3:].strip())
            pdf.set_font("Helvetica", "B", 12.5)
            pdf.set_text_color(27, 85, 131) # Royal Blue
            pdf.write(8, q_header)
            pdf.ln(8)
            question_lines = []
            continue
            
        if in_question:
            if line_stripped.startswith("### Answer"):
                in_question = False
                draw_question_box(pdf, " ".join(question_lines))
                question_lines = []
                
                # Print Answer Header
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(51, 51, 51)
                pdf.write(6, "Answer")
                pdf.ln(6)
                continue
            else:
                if line_stripped:
                    question_lines.append(line_stripped)
                continue
                
        process_markdown_line(pdf, line, md_file)
        
    if in_question:
        draw_question_box(pdf, " ".join(question_lines))
    if in_table:
        render_table(pdf, table_lines)
        
    pdf.output(pdf_file)
    print(f"Successfully generated PDF: {pdf_file}")

if __name__ == "__main__":
    main()
