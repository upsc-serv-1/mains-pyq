import os
import re

solved_paper_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
target_files = [
    os.path.join(solved_paper_dir, "gs1", "gs1_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs2", "gs2_pwonlyias.md"),
    os.path.join(solved_paper_dir, "gs3", "gs3_pwonlyias.md"),
]

output_file = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\scratch\unmatched_headings.txt"

with open(output_file, "w", encoding="utf-8") as out:
    for path in target_files:
        if not os.path.exists(path):
            continue
        out.write(f"\n=================== {os.path.basename(path)} ===================\n")
        with open(path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        
        for idx, line in enumerate(lines):
            stripped = line.strip()
            # If line starts with "**"
            if stripped.startswith("**"):
                # Count occurrences of "**"
                stars_count = stripped.count("**")
                # If there's only one "**" (meaning it starts with "**" but has no closing "**" at all)
                # or if the line does not end with "**" and has odd number of "**"
                if stars_count == 1:
                    out.write(f"Line {idx+1}: {line}")
                elif stars_count % 2 != 0:
                    out.write(f"Line {idx+1} (Odd count={stars_count}): {line}")
                elif not stripped.endswith("**") and not stripped.endswith("**:"):
                    # Ends with something else, let's check if it closes correctly
                    # E.g., "**Title:** text" has even stars but does not end with stars. That is valid bold text at start.
                    # But if it is "**Title: text" it would have stars_count = 1.
                    pass

print("Done scanning unmatched bold headings!")
