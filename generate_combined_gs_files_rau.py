import os
import re

# Base directory
base_solved_dir = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\solved paper"
rau_dir = os.path.join(base_solved_dir, "rau ias")

# GS papers to process
GS_PAPERS = ["gs1", "gs2", "gs3", "gs4"]

def clean_trailing_dividers(text):
    text = text.strip()
    while True:
        lines = text.splitlines()
        if not lines:
            break
        last_line = lines[-1].strip()
        if last_line == '---' or not last_line:
            text = "\n".join(lines[:-1]).strip()
        else:
            break
    return text

def combine_rau_files():
    for gs_paper in GS_PAPERS:
        source_filename = f"{gs_paper}_solved_pyqs.md"
        source_path = os.path.join(rau_dir, source_filename)
        
        if not os.path.exists(source_path):
            print(f"Warning: Source file {source_path} does not exist. Skipping.")
            continue
            
        target_filename = f"{gs_paper}_rau_ias.md"
        target_folder = os.path.join(base_solved_dir, gs_paper)
        os.makedirs(target_folder, exist_ok=True)
        target_path = os.path.join(target_folder, target_filename)
        
        print(f"Processing {source_filename} -> {target_path}...")
        
        with open(source_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Find all question header matches
        q_matches = list(re.finditer(r'^##\s*Question\s*\d+.*', content, re.MULTILINE | re.IGNORECASE))
        
        combined_blocks = []
        q_counter = 0
        
        for idx, match in enumerate(q_matches):
            start = match.start()
            end = q_matches[idx+1].start() if idx + 1 < len(q_matches) else len(content)
            
            block = content[start:end].strip()
            if not block:
                continue
                
            q_counter += 1
            
            # Find the year using regex
            m_year = re.search(r'Year:\s*(\d{4})', block)
            year = m_year.group(1) if m_year else "unknown"
            
            q_id = f"{year}-{gs_paper}-q{q_counter}-rau_ias"
            
            # Renumber the question
            lines_block = block.splitlines()
            header_line = lines_block[0]
            header_line_updated = re.sub(r'^##\s*Question\s*\d+', f"## Question {q_counter}", header_line, flags=re.IGNORECASE)
            lines_block[0] = header_line_updated
            
            # Remove empty lines immediately after header line
            cursor = 1
            while cursor < len(lines_block) and not lines_block[cursor].strip():
                lines_block.pop(cursor)
                
            # Insert the Question ID and a blank line
            lines_block.insert(1, f"**Question ID: {q_id}**")
            lines_block.insert(2, "")
            
            # Clean up the rest of the block (remove trailing dividers)
            block_content = "\n".join(lines_block)
            block_content = clean_trailing_dividers(block_content)
            
            # Append the Question ID at the bottom
            lines_block_final = block_content.splitlines()
            lines_block_final.append("")
            lines_block_final.append(f"[Question ID: {q_id}]")
            
            final_block = "\n".join(lines_block_final)
            combined_blocks.append(final_block)
            
        if q_counter > 0:
            title_paper = gs_paper.upper()
            with open(target_path, "w", encoding="utf-8") as f_out:
                f_out.write(f"# UPSC Mains Solved Papers - {title_paper} (Rau IAS)\n\n")
                f_out.write(f"This file contains the combined solved papers for {title_paper} subjects in logical order.\n\n---\n\n")
                f_out.write("\n\n---\n\n".join(combined_blocks))
                f_out.write("\n\n---\n") # final trailing divider
            print(f"  Successfully combined {q_counter} questions into {target_filename}")
        else:
            print(f"  No questions found for {gs_paper} in {source_filename}")

if __name__ == "__main__":
    combine_rau_files()
