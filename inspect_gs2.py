import pdfplumber

pdf_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\Civilsdaily GS Mains Microthemes_2025 Edition.pdf"

with pdfplumber.open(pdf_path) as pdf:
    for page_num in range(26, 49): # Pages 26 to 48
        page = pdf.pages[page_num - 1]
        table = page.extract_table()
        if not table:
            print(f"Page {page_num}: No table found")
            continue
        print(f"Page {page_num}: Table found with {len(table)} rows, columns: {table[0]}")
        # Print first 2 data rows
        data_rows = [r for r in table if r[1] != "UPSC PYQs" and r[1] is not None]
        print(f"  First 2 data rows:")
        for r in data_rows[:2]:
            print(f"    {r}")
