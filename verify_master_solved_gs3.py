import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs3\master_gs3_solved.md"

def verify_master():
    if not os.path.exists(path):
        print(f"Error: File not found: {path}")
        return False
        
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
        
    errors = []
    
    # 1. Check for HTML collapsibles
    details_count = content.lower().count("<details")
    summary_count = content.lower().count("<summary")
    if details_count > 0 or summary_count > 0:
        errors.append(f"Found HTML collapsibles: <details> count = {details_count}, <summary> count = {summary_count}")
        
    # 2. Check for duplicate Answer headers inside
    ans_headers_count = len(re.findall(r'^###\s*Answer\s*$', content, re.MULTILINE | re.IGNORECASE))
    ans_bold_count = len(re.findall(r'^\*\*Answer:\*\*\s*$', content, re.MULTILINE | re.IGNORECASE))
    if ans_headers_count > 0 or ans_bold_count > 0:
        errors.append(f"Found duplicate Answer headers: '### Answer' count = {ans_headers_count}, '**Answer:**' count = {ans_bold_count}")
        
    # 3. Check for correct explanation headers format
    exp_headers = re.findall(r'^.*Explanation_.*$', content, re.MULTILINE)
    for h in exp_headers:
        if not re.match(r'^1\.\s+Explanation_(?:Civilsdaily|Drishti IAS|PWOnlyIAS|Superkalam|Unacademy):$', h):
            errors.append(f"Invalid explanation header format: {repr(h)}")
            
    # 4. Check that bracketed metadata is immediately below the question
    lines = content.split('\n')
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if re.match(r'^Q\d+\.', line_strip):
            if idx + 2 < len(lines):
                blank_line = lines[idx+1].strip()
                meta_line = lines[idx+2].strip()
                if blank_line != "":
                    errors.append(f"Expected blank line after question {repr(line_strip)} at line {idx+1}")
                if not meta_line.startswith('['):
                    errors.append(f"Expected metadata block at line {idx+3}, got {repr(meta_line)}")
            else:
                errors.append(f"Question {repr(line_strip)} is cut off at the end of the file")

    # 5. Check if any relative image paths still use "images/" without prepended folder
    unprepended_images = re.findall(r'(?:\(|=\"|=\')images/', content)
    if unprepended_images:
        errors.append(f"Found unprepended relative image references: {unprepended_images}")

    print(f"\nVerification for master_gs3_solved.md:")
    if errors:
        print(f"  FAILED with {len(errors)} errors:")
        for err in errors[:10]:
            print(f"    - {err}")
        if len(errors) > 10:
            print(f"    - ... and {len(errors)-10} more errors.")
        return False
    else:
        print("  PASSED! All formatting rules adhered to perfectly.")
        return True

if __name__ == "__main__":
    verify_master()
