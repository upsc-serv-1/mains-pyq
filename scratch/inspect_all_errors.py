import os
import re
import sys

# Set stdout/stderr encoding to UTF-8 on Windows
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

folders = ["civilsdaily", "drishti ias", "pwonlyias", "superkalam", "unacademy"]
base_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

def inspect_file(filepath, folder_name):
    with open(filepath, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
        
    lines = content.split("\n")
    issues = []
    
    # 1. Unicode replacement char or specific patterns
    for idx, line in enumerate(lines):
        if "\ufffd" in line:
            issues.append({
                "line": idx + 1,
                "type": "unicode_corruption",
                "text": line.strip()
            })
            
    # 2. Potential split bold sentences or paragraph split issues
    in_answer = False
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if "### Answer" in line_strip:
            in_answer = True
            continue
        if line_strip.startswith("## Question"):
            in_answer = False
            continue
            
        if in_answer and line_strip:
            clean = line_strip.replace("**", "").strip()
            
            # Sentence starting with lowercase letter (likely split paragraph)
            # Exclude lines starting with list markers or markdown syntax
            if re.match(r'^[a-z]', clean) and not clean.startswith(("http", "www", "<", "src=")):
                # Check if previous line ended without sentence termination
                if idx > 0:
                    prev = lines[idx-1].strip().replace("**", "").strip()
                    if prev and not prev.endswith((".", "?", "!", ":")):
                        issues.append({
                            "line": idx + 1,
                            "type": "split_sentence_paragraph",
                            "text": f"PREV: '{prev}' | CURR: '{line_strip}'"
                        })
            
            # Short bold fragments that look like split bold texts
            if line_strip.startswith("**") and line_strip.endswith("**") and len(line_strip) > 4:
                inner = line_strip[2:-2].strip()
                if len(inner) < 50 and (inner.endswith(".") or inner.endswith(",") or inner.endswith(")") or inner.endswith(";")):
                    # It's bold and ends with punctuation, but is short and not a standard section header
                    if not any(h in inner.lower() for h in ["introduction", "conclusion", "body", "way forward", "significance", "challenges"]):
                        issues.append({
                            "line": idx + 1,
                            "type": "potential_false_bold_split",
                            "text": line_strip
                        })
                        
    # 3. Double bold tags or empty bold tags
    for idx, line in enumerate(lines):
        if "****" in line:
            issues.append({
                "line": idx + 1,
                "type": "empty_bold_tags",
                "text": line.strip()
            })
        # Odd number of bold tags
        if line.count("**") % 2 != 0:
            # check if inside code blocks
            if not line.strip().startswith("```"):
                issues.append({
                    "line": idx + 1,
                    "type": "unmatched_bold_tags",
                    "text": line.strip()
                })
                
    # 4. Stray bullet prefixes
    for idx, line in enumerate(lines):
        line_strip = line.strip()
        if line_strip.startswith(("●", "•", "○", "y ", "y\n", "y$")):
            issues.append({
                "line": idx + 1,
                "type": "unconverted_bullet",
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
        
    all_issues = {}
    for f in files:
        filepath = os.path.join(folder_path, f)
        issues = inspect_file(filepath, folder)
        if issues:
            all_issues[f] = issues
            
    if not all_issues:
        print("  No significant formatting errors found!")
    else:
        total_types = {}
        for filename, issues in all_issues.items():
            # Group by type and print top 2 examples for each type
            by_type = {}
            for iss in issues:
                by_type.setdefault(iss["type"], []).append(iss)
                total_types[iss["type"]] = total_types.get(iss["type"], 0) + 1
                
            print(f"\n  File: {filename} (Total issues: {len(issues)})")
            for t, items in by_type.items():
                print(f"    Type: {t} (Count: {len(items)})")
                for item in items[:2]:
                    # Escape text for safe printing
                    safe_text = item['text'].encode('ascii', 'replace').decode('ascii')
                    print(f"      Line {item['line']}: {safe_text}")
                    
        print(f"\nSummary of issues for {folder}:")
        for t, count in total_types.items():
            print(f"  - {t}: {count} occurrences")
