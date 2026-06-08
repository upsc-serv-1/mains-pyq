import os
import re

# Base directory
base_solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"

# Mapping of GS papers to their subjects in logical order
GS_MAPPING = {
    "gs1": [
        "ancient_history_and_art__culture",
        "modern_history",
        "post_independent_india",
        "world_history",
        "indian_society",
        "geography"
    ],
    "gs2": [
        "polity",
        "governance",
        "social_justice",
        "international_relations"
    ],
    "gs3": [
        "economic_development",
        "agriculture",
        "environment_and_ecology",
        "science__technology",
        "internal_security",
        "disaster_management"
    ],
    "gs4": [
        "ethics_theoretical_questions",
        "ethics_case_studies"
    ]
}

# Folders to process (EXCLUDING pwonlyias)
FOLDERS = [
    os.path.join(base_solved_dir, "civilsdaily"),
    os.path.join(base_solved_dir, "drishti ias"),
    os.path.join(base_solved_dir, "superkalam"),
    os.path.join(base_solved_dir, "unacademy")
]

def get_folder_suffix(folder_path):
    base_name = os.path.basename(folder_path)
    return base_name.lower().replace(" ", "_")

def combine_gs_files():
    for folder in FOLDERS:
        if not os.path.exists(folder):
            print(f"Warning: Folder {folder} does not exist. Skipping.")
            continue
            
        suffix = get_folder_suffix(folder)
        folder_display_name = os.path.basename(folder).title()
        
        for gs_paper, subjects in GS_MAPPING.items():
            combined_filename = f"{gs_paper}_{suffix}.md"
            gs_folder = os.path.join(base_solved_dir, gs_paper)
            os.makedirs(gs_folder, exist_ok=True)
            combined_filepath = os.path.join(gs_folder, combined_filename)
            
            print(f"Generating {combined_filename} in {gs_paper} folder...")
            
            combined_blocks = []
            q_counter = 0
            
            for subj in subjects:
                subj_file = os.path.join(folder, f"{subj}.md")
                if not os.path.exists(subj_file):
                    continue
                    
                with open(subj_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    
                # Split by ---
                blocks = re.split(r'\n\s*---\s*\n', content)
                
                for block in blocks:
                    block_strip = block.strip()
                    if not block_strip:
                        continue
                        
                    # Skip main file headers
                    if block_strip.startswith("# UPSC Mains") or block_strip.startswith("# "):
                        continue
                    if "This file contains" in block_strip:
                        continue
                        
                    # Verify it contains a question header
                    if "## Question" in block_strip:
                        q_counter += 1
                        
                        # Find the year using regex
                        m_year = re.search(r'Year:\s*(\d{4})', block_strip)
                        year = m_year.group(1) if m_year else "unknown"
                        
                        q_id = f"{year}-{gs_paper}-q{q_counter}-{suffix}"
                        
                        # Renumber the question: replace "## Question \d+" at start of line with "## Question {q_counter}"
                        updated_block = re.sub(
                            r'^## Question \d+', 
                            f"## Question {q_counter}", 
                            block_strip
                        )
                        
                        # Split block to insert the Question ID below the header line
                        lines_block = updated_block.split("\n")
                        
                        # Remove empty lines immediately after header line (index 0)
                        cursor = 1
                        while cursor < len(lines_block) and not lines_block[cursor].strip():
                            lines_block.pop(cursor)
                            
                        # Insert the Question ID
                        lines_block.insert(1, f"**Question ID: {q_id}**")
                        lines_block.insert(2, "")
                        
                        # Append the Question ID in bracket format at the bottom
                        lines_block.append("")
                        lines_block.append(f"[Question ID: {q_id}]")
                        
                        final_block = "\n".join(lines_block)
                        combined_blocks.append(final_block)
            
            if q_counter > 0:
                # Write to combined file
                title_paper = gs_paper.upper()
                with open(combined_filepath, "w", encoding="utf-8") as f_out:
                    f_out.write(f"# UPSC Mains Solved Papers - {title_paper} ({folder_display_name})\n\n")
                    f_out.write(f"This file contains the combined solved papers for {title_paper} subjects in logical order.\n\n---\n\n")
                    f_out.write("\n\n---\n\n".join(combined_blocks))
                    f_out.write("\n\n---\n") # final trailing divider
                print(f"  Successfully combined {q_counter} questions into {combined_filename}")
            else:
                print(f"  No questions found for {gs_paper} in {os.path.basename(folder)}")

if __name__ == "__main__":
    combine_gs_files()
