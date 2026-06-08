import re
import os

import sys
import os
sys.path.append(os.getcwd())
from compile_master_gs3 import parse_institute_files, clean_and_tokenize, jaccard_similarity

institute_data = parse_institute_files()

# Test question statement
new_q = "How can India achieve energy independence through clean technology by 2047? How can biotechnology play a crucial role in this endeavour?"
year = "2025"

target_tokens = clean_and_tokenize(new_q)
print(f"Target tokens: {target_tokens}")

for inst_name, inst_qs in institute_data.items():
    same_year_qs = [iq for iq in inst_qs if iq['year'] == year]
    print(f"\n{inst_name}: Total questions in year {year}: {len(same_year_qs)}")
    best_sim = 0.0
    best_match = None
    for iq in same_year_qs:
        sim = jaccard_similarity(target_tokens, iq['tokens'])
        if sim > best_sim:
            best_sim = sim
            best_match = iq
    if best_match:
        print(f"  Best Match (Sim: {best_sim:.2f}): {best_match['original_text']}")
    else:
        print("  No match found in same year.")
