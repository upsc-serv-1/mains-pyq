import os
import re

folders = ["civilsdaily", "unacademy"]
base_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        continue
        
    print(f"\n==========================================")
    print(f"Scanning folder for split issues: {folder}")
    print(f"==========================================")
    
    for filename in os.listdir(folder_path):
        if not filename.endswith(".md"):
            continue
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        
        # We are looking for lines inside the answer (after ### Answer) that:
        # 1. Start and end with **
        # 2. Are very short (e.g. < 40 characters)
        # 3. Contain sentence-ending punctuation like period, comma, parenthesis
        # 4. Are not standard subheaders like "Introduction", "Conclusion", "Body"
        
        in_answer = False
        for idx, line in enumerate(lines):
            line_strip = line.strip()
            if "### Answer" in line_strip:
                in_answer = True
                continue
            if line_strip.startswith("## Question"):
                in_answer = False
                continue
                
            if in_answer and line_strip.startswith("**") and line_strip.endswith("**") and len(line_strip) > 4:
                inner = line_strip[2:-2].strip()
                if len(inner) < 40:
                    # Check if it ends with punctuation
                    if inner.endswith(".") or inner.endswith(",") or inner.endswith(")") or inner.endswith(":") or inner.endswith(";"):
                        # Exclude common headings
                        if not any(h in inner.lower() for h in ["introduction", "conclusion", "body", "significance", "way forward"]):
                            print(f"  File: {filename} | Line {idx+1}: {line_strip}")
