import fitz

pdf_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\Civilsdaily GS Mains Microthemes_2025 Edition.pdf"
doc = fitz.open(pdf_path)

with open("gs1_pages_6_22.txt", "w", encoding="utf-8") as f:
    for i in range(5, 22): # Pages 6 to 22 (0-indexed 5 to 21)
        f.write(f"======================================== PAGE {i+1} ========================================\n")
        f.write(doc[i].get_text())
print("Done writing pages 6 to 22 text to gs1_pages_6_22.txt")
