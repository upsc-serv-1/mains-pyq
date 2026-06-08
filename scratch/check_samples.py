import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

folders = ["civilsdaily", "drishti ias", "pwonlyias", "superkalam", "unacademy"]
base_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

def check_file_formatting(filepath, folder_name):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
        
    lines = content.split("\n")
    issues = []
    
    # 1. Check for duplicate year prefixes (e.g. "## Question 1" followed by "**2025 - ...")
    in_q = False
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if line_strip.startswith("## Question"):
            in_q = True
            continue
        if in_q and line_strip:
            # First non-empty line after question header should be the question text
            # E.g. "**2025 - Mahatma..."
            if re.search(r'^\*+\s*\d{4}\s*[-–—]\s*', line_strip):
                issues.append({
                    "line_num": idx + 1,
                    "type": "duplicate_year_prefix",
                    "text": line_strip
                })
            in_q = False
            
    # 2. Check for bold lines ending with period or other sentence punctuation (indicating false splits / heading formats)
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if line_strip.startswith("**") and line_strip.endswith("**") and len(line_strip) > 4:
            inner = line_strip[2:-2].strip()
            # If it has internal periods or ends in a period/comma/parenthesis, it is likely a sentence segment, not a heading!
            if inner.endswith(".") or inner.endswith("?") or inner.endswith("!") or inner.endswith(")") or inner.endswith(","):
                # Make sure it's not a block quote or standard bold paragraph
                # Heading checks
                if "introduction" not in inner.lower() and "body" not in inner.lower() and "conclusion" not in inner.lower():
                    issues.append({
                        "line_num": idx + 1,
                        "type": "potential_false_bold_heading",
                        "text": line_strip
                    })
                    
    return issues

for folder in folders:
    folder_path = os.path.join(base_dir, folder)
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        continue
        
    print(f"\n==========================================")
    print(f"Analyzing folder: {folder}")
    print(f"==========================================")
    
    files = [f for f in os.listdir(folder_path) if f.endswith(".md")]
    if not files:
        print("  No markdown files found.")
        continue
        
    total_issues = 0
    for f in files[:5]: # Check first 5 files as sample
        filepath = os.path.join(folder_path, f)
        issues = check_file_formatting(filepath, folder)
        if issues:
            print(f"\n  File: {f} (Found {len(issues)} potential issues)")
            for iss in issues[:3]: # Print top 3 issues
                print(f"    Line {iss['line_num']} [{iss['type']}]: {iss['text']}")
            total_issues += len(issues)
            
    print(f"  Total potential issues in sample files: {total_issues}")
