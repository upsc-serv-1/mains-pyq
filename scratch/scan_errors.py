import re
import os

file_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper\gs1\gs1_pwonlyias.md"
out_path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\scratch\scan_results.txt"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

lines = content.splitlines()

with open(out_path, "w", encoding="utf-8") as out:
    out.write("Scanning for formatting anomalies in gs1_pwonlyias.md...\n")

    # 1. Glued bold markers (****)
    out.write("\n--- 1. Glued Bold Markers (****) ---\n")
    for idx, line in enumerate(lines):
        if "****" in line:
            out.write(f"Line {idx+1}: {line}\n")

    # 2. Odd number of bold stars in a line (potential orphaned bolds)
    out.write("\n--- 2. Odd Number of Bold Stars (potential orphaned bolds) ---\n")
    for idx, line in enumerate(lines):
        stars_only_double = line.replace('***', '')
        double_count = len(re.findall(r'\*\*', stars_only_double))
        
        if double_count % 2 != 0:
            out.write(f"Line {idx+1} (double count: {double_count}): {line}\n")

    # 3. Bad bold spacing (e.g. '** text**' or '**text **')
    out.write("\n--- 3. Bad Bold Spacing ---\n")
    for idx, line in enumerate(lines):
        bad_spacing_matches = re.findall(r'(\*\*\s+[^*]+?\s+\*\*|\*\*\s+[^*]+?\*\*|\*\*[^*]+?\s+\*\*)', line)
        if bad_spacing_matches:
            out.write(f"Line {idx+1}: {line} (Matches: {bad_spacing_matches})\n")
                
    # 4. Glued headers or list markers to end of words (e.g. word**Header or word**-**Bullet)
    out.write("\n--- 4. Glued Headers / Bullets ---\n")
    for idx, line in enumerate(lines):
        if re.search(r'\w\*\*[-*]', line) or re.search(r'\w\*\*(##|###)', line):
            out.write(f"Line {idx+1}: {line}\n")

print("Scan complete. Results written to scratch/scan_results.txt")
