import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_drishti_ias.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

idx = content.find("Differences between Offshore and Onshore")
if idx != -1:
    print("=== Table Source in gs1_drishti_ias.md ===")
    print(content[idx-100:idx+800])
else:
    print("Table not found!")
