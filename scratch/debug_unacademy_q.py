import pdfplumber
import re

pdf_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\unacademy\unacademy mains solved paper.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for idx, page in enumerate(pdf.pages):
        text = page.extract_text()
        if "income substantially" in text:
            print(f"Found on page {idx+1}")
            words = page.extract_words()
            # Sort words by top then x0
            lines = {}
            for w in words:
                top = w["top"]
                found = False
                for t in lines:
                    if abs(t - top) < 4:
                        lines[t].append(w)
                        found = True
                        break
                if not found:
                    lines[top] = [w]
            sorted_tops = sorted(lines.keys())
            for top in sorted_tops:
                line_words = sorted(lines[top], key=lambda x: x["x0"])
                line_text = " ".join([w["text"] for w in line_words])
                if "farmers" in line_text or "income substantially" in line_text:
                    print(f"Top {top:.2f}: {line_text}")
