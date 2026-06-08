import re
import os
import fitz

sarrthi_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\GS 3 PYQs.pdf"

def get_column(x0):
    if 20 < x0 < 58:
        return "qn_no"
    elif 58 <= x0 < 100:
        return "year"
    elif 100 <= x0 < 465:
        return "question"
    elif 465 <= x0 < 535:
        return "topic"
    elif 535 <= x0 < 600:
        return "marks"
    return None

# Reuse the parser
import sys
sys.path.append(r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\scratch")
from thorough_audit import parse_sarrthi_pdf

sarrthi_qs = parse_sarrthi_pdf(sarrthi_path)

missing_keywords = ["ppp model", "multibrand", "multi-brand", "low income trap", "life expectancy", "energy independence"]

print("MATCHED MISSING QUESTIONS IN SARRTHI PDF:")
for sq in sarrthi_qs:
    q_text = sq["question"].lower()
    if any(k in q_text for k in missing_keywords):
        print(f"Sarrthi Qn: {sq['qn_no']}")
        print(f"Year:       {sq['year']}")
        print(f"Topic:      {sq['topic']}")
        print(f"Marks:      {sq['marks']}")
        print(f"Question:   {sq['question']}")
        print("-" * 50)
