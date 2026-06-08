import pdfplumber
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy\unacademy mains solved paper.pdf"

with pdfplumber.open(pdf_path) as pdf:
    # Let's search all pages for "income substantially"
    for page_num in range(1, len(pdf.pages) + 1):
        page = pdf.pages[page_num - 1]
        text = page.extract_text() or ""
        if "income substantially" in text:
            print(f"Found 'income substantially' on page {page_num}")
            
            # Let's extract words and see their font/text
            words = page.extract_words(extra_attrs=["fontname"])
            print(f"\n--- Raw Words on page {page_num} containing 'substantially' ---")
            for w in words:
                if "substantially" in w["text"] or "farmers" in w["text"] or "income" in w["text"]:
                    print(w)
                    
            # Let's run the page layout extraction like in scrape_unacademy.py
            print(f"\n--- Reconstructed Lines for page {page_num} ---")
            sys.path.append(r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc")
            from scrape_unacademy import extract_smart_layout, join_paragraph_lines
            image_counter = [0]
            lines = extract_smart_layout(page, image_counter, "scratch_images")
            for idx, line in enumerate(lines):
                if "farmers" in line or "income" in line:
                    print(f"Line {idx}: {line}")
                    
            print(f"\n--- After join_paragraph_lines on page {page_num} ---")
            joined = join_paragraph_lines(lines)
            for idx, line in enumerate(joined):
                if "farmers" in line or "income" in line:
                    print(f"Joined Line {idx}: {line}")
