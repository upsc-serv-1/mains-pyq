import pdfplumber
import json

pdf_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\Civilsdaily GS Mains Microthemes_2025 Edition.pdf"

microthemes_by_page = {}

with pdfplumber.open(pdf_path) as pdf:
    for page_num in range(26, 49): # Pages 26 to 48
        page = pdf.pages[page_num - 1]
        table = page.extract_table()
        if not table:
            continue
        
        start_row = 0
        if table[0][0] == "Microthemes" or table[0][1] == "UPSC PYQs":
            start_row = 1
            
        page_mts = []
        current_mt = ""
        for row in table[start_row:]:
            if len(row) < 4:
                continue
            mt = row[0]
            pyq = row[1]
            if not pyq or pyq.strip() == "" or pyq.strip() == "UPSC PYQs":
                continue
            
            if mt and mt.strip():
                current_mt = mt.replace("\n", " ").replace("\x07", "").strip()
            
            if current_mt not in page_mts:
                page_mts.append(current_mt)
        
        microthemes_by_page[page_num] = page_mts

print(json.dumps(microthemes_by_page, indent=4))
