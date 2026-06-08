import re

test_lines = [
    # Case 1: Subheading in the middle of a line
    "The wind is used to produce electricity using the kinetic energy. **Potential:** - India has the potential of about 60 GW of wind.",
    # Case 2: Subheading at the start of a line (should be split from inline bullet)
    "**Potential:** - India has the potential of about 60 GW of wind.",
    # Case 3: Another subheading in the middle of a line
    "In 2022, Tamil Nadu is among the largest producer. **Reasons:** - Wind power must compete with other low-cost energy sources.",
    # Case 4: Long subheading in the middle
    "Meeting of cold and warm currents forms fishing zones. **Creation of Fishing Zones:** - Prominent examples are North East Pacific Zone.",
    # Case 5: Standard list item (should NOT be split)
    "- **Access to Finance:** Farmers require credit to purchase seeds."
]

def clean_line_v8(line):
    # Split inline subheadings (at start or middle of a line)
    line = re.sub(r'\s*\*\*([^*:]{2,80}:?)\*\*\s*-\s*', r'\n\n**\1**\n\n- ', line)
    
    # 1. Normalize malformed list bullets first: -** or *** or - ** or * **
    line = re.sub(r'(^|\s)([\-*])\s*\*\*\s*', r'\1\2 **', line)
    
    # We split by \n to process sub-lines
    sub_lines = line.split('\n')
    cleaned_sub_lines = []
    
    for sub in sub_lines:
        sub_strip = sub.strip()
        if not sub_strip:
            continue
        cleaned_sub_lines.append(sub_strip)
        
    return "\n\n".join(cleaned_sub_lines)

for line in test_lines:
    print(f"ORIGINAL:\n{line}")
    print(f"CLEANED:\n{clean_line_v8(line)}")
    print("-" * 50)
