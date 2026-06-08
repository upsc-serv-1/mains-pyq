import urllib.request
import os
import re
import html
import time
from html.parser import HTMLParser

# List of subjects and their URLs
SUBJECTS = {
    "Agriculture": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/agriculture",
    "Ancient History and Art & Culture": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/ancient%20history%20and%20art%20&%20culture",
    "Disaster Management": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/disaster%20management",
    "Economic Development": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/economic%20development%20",
    "Environment and Ecology": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/environment%20and%20ecology%20",
    "Ethics (Case Studies)": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/ethics%20%28case%20studies%29",
    "Ethics (Theoretical Questions)": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/ethics%20%28theoretical%20questions%29",
    "Geography": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/geography",
    "Governance": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/governance",
    "Indian Society": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/indian%20society",
    "Internal Security": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/internal%20security",
    "International Relations": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/international%20relations",
    "Modern History": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/modern%20history%20",
    "Polity": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/polity",
    "Post Independent India": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/post%20independent%20india",
    "Science & Technology": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/science%20&%20technology",
    "Social Justice": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/social%20justice",
    "World History": "https://www.drishtiias.com/upsc-mains-solved-papers/subject/world%20history"
}

class HTMLToMarkdown(HTMLParser):
    def __init__(self, download_img_fn=None):
        super().__init__()
        self.markdown = []
        self.download_img_fn = download_img_fn
        self.stack = []
        self.list_indices = []
        self.in_table = False
        self.table_rows = []
        self.current_row = []
        self.current_cell = ""
        self.in_cell = False

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.stack.append(tag)
        
        if self.in_table:
            if tag in ('strong', 'b'):
                if self.in_cell:
                    self.current_cell += "**"
            elif tag in ('em', 'i'):
                if self.in_cell:
                    self.current_cell += "*"
            elif tag == 'li':
                if self.in_cell:
                    self.current_cell += "<br>• "
            elif tag == 'img':
                src = attrs_dict.get('src', '')
                if src:
                    if self.download_img_fn:
                        local_path = self.download_img_fn(src)
                    else:
                        local_path = src
                    if self.in_cell:
                        self.current_cell += f" ![Image]({src}) "
            elif tag == 'tr':
                self.current_row = []
            elif tag in ('td', 'th'):
                self.in_cell = True
                self.current_cell = ""
            return
            
        if tag in ('h1', 'h2'):
            self.markdown.append("\n\n## ")
        elif tag in ('h3', 'h4'):
            self.markdown.append("\n\n### ")
        elif tag in ('h5', 'h6'):
            self.markdown.append("\n\n#### ")
        elif tag == 'p':
            self.markdown.append("\n\n")
        elif tag in ('strong', 'b'):
            self.markdown.append("**")
        elif tag in ('em', 'i'):
            self.markdown.append("*")
        elif tag == 'ul':
            self.list_indices.append(None)
            self.markdown.append("\n")
        elif tag == 'ol':
            self.list_indices.append(1)
            self.markdown.append("\n")
        elif tag == 'li':
            indent = "  " * (len(self.list_indices) - 1)
            list_type = self.list_indices[-1] if self.list_indices else None
            if list_type is None:
                self.markdown.append(f"\n{indent}- ")
            else:
                self.markdown.append(f"\n{indent}{list_type}. ")
                self.list_indices[-1] += 1
        elif tag == 'table':
            self.in_table = True
            self.table_rows = []
        elif tag == 'tr':
            self.current_row = []
        elif tag in ('td', 'th'):
            self.in_cell = True
            self.current_cell = ""
        elif tag == 'img':
            src = attrs_dict.get('src', '')
            if src:
                if self.download_img_fn:
                    local_path = self.download_img_fn(src)
                else:
                    local_path = src
                self.markdown.append(f"\n\n![Image]({src})\n[View Offline Local Backup]({local_path})\n\n")

    def handle_endtag(self, tag):
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        else:
            if tag in self.stack:
                while self.stack and self.stack[-1] != tag:
                    self.stack.pop()
                if self.stack:
                    self.stack.pop()
                    
        if self.in_table:
            if tag in ('strong', 'b'):
                if self.in_cell:
                    self.current_cell += "**"
            elif tag in ('em', 'i'):
                if self.in_cell:
                    self.current_cell += "*"
            elif tag in ('td', 'th'):
                self.in_cell = False
                self.current_row.append(self.current_cell.strip())
            elif tag == 'tr':
                self.table_rows.append(self.current_row)
            elif tag == 'table':
                self.in_table = False
                if self.table_rows:
                    num_cols = max(len(row) for row in self.table_rows) if self.table_rows else 0
                    padded_rows = []
                    for row in self.table_rows:
                        padded_row = row + [""] * (num_cols - len(row))
                        padded_rows.append(padded_row)
                    
                    if num_cols > 0:
                        headers = padded_rows[0]
                        self.markdown.append("\n\n| " + " | ".join(headers) + " |\n")
                        self.markdown.append("| " + " | ".join(["---"] * num_cols) + " |\n")
                        for row in padded_rows[1:]:
                            self.markdown.append("| " + " | ".join(row) + " |\n")
                        self.markdown.append("\n")
                self.table_rows = []
            return

        if tag in ('strong', 'b'):
            self.markdown.append("**")
        elif tag in ('em', 'i'):
            self.markdown.append("*")
        elif tag in ('ul', 'ol'):
            if self.list_indices:
                self.list_indices.pop()
            self.markdown.append("\n")

    def handle_data(self, data):
        cleaned = html.unescape(data).replace('\xa0', ' ').replace('\u200b', '')
        if self.in_table and self.in_cell:
            self.current_cell += cleaned.replace("\r", "").replace("\n", " ").replace("|", "\\|")
        else:
            self.markdown.append(cleaned)

def make_download_image_fn(img_dir, subject_name, q_index, downloaded_cache):
    img_counter = [0]
    def download_image(src):
        if not src.startswith("http"):
            if src.startswith("/"):
                src = "https://www.drishtiias.com" + src
            else:
                return src
        
        if src in downloaded_cache:
            return downloaded_cache[src]
            
        try:
            img_counter[0] += 1
            clean_sub = "".join(c for c in subject_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_").lower()
            
            # Determine correct file extension
            ext = os.path.splitext(src.split("?")[0])[1]
            if not ext or ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                ext = '.png'
                
            filename = f"{clean_sub}_q{q_index}_img{img_counter[0]}{ext}"
            os.makedirs(img_dir, exist_ok=True)
            filepath = os.path.join(img_dir, filename)
            
            req = urllib.request.Request(
                src,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                with open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
            print(f"  Downloaded image: {src} -> {filepath}")
            local_rel_path = f"images/{filename}"
            downloaded_cache[src] = local_rel_path
            return local_rel_path
        except Exception as e:
            print(f"  Failed to download image {src}: {e}")
            return src
    return download_image

def clean_html_tags(raw_html):
    clean = re.sub(r'<script.*?>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    return clean

def extract_questions_and_answers(html_content):
    accordion_match = re.search(r'<div[^>]*id="accordion"[^>]*>(.*?)</div>\s*<!--\s*end\s*accordion\s*-->', html_content, re.DOTALL | re.IGNORECASE)
    if not accordion_match:
        accordion_match = re.search(r'<div[^>]*id="accordion"[^>]*>(.*)', html_content, re.DOTALL | re.IGNORECASE)
        
    if not accordion_match:
        return []
        
    accordion_html = accordion_match.group(1)
    
    # Trim accordion_html to exclude site footer/sidebar
    footer_markers = [
        '<footer', 
        'id="disqus_thread"', 
        'class="reach-us"', 
        'class="reach_us"',
        'Reach Us',
        'class="progress-bookmark"',
        'class="bookmark-progress"',
        'class="solved-paper-subject"',
        'class="navigation_addon"'
    ]
    for marker in footer_markers:
        marker_pos = accordion_html.find(marker)
        if marker_pos != -1:
            accordion_html = accordion_html[:marker_pos]
            
    starts = [m.start() for m in re.finditer(r'<p\s+class="year"', accordion_html, re.IGNORECASE)]
    if not starts:
        starts = [m.start() for m in re.finditer(r'class="year"', accordion_html, re.IGNORECASE)]
        
    blocks = []
    for i in range(len(starts)):
        start_pos = starts[i]
        end_pos = starts[i+1] if i + 1 < len(starts) else len(accordion_html)
        blocks.append(accordion_html[start_pos:end_pos])
        
    extracted = []
    for block in blocks:
        year_match = re.search(r'<span[^>]*>(\d{4})</span>', block, re.IGNORECASE)
        year = year_match.group(1) if year_match else "N/A"
        
        btn_match = re.search(r'<button[^>]*class="btn"[^>]*>', block, re.IGNORECASE)
        btn_pos = btn_match.start() if btn_match else block.find("Show Answer")
            
        if btn_pos != -1:
            q_html = block[:btn_pos]
            q_text = re.sub(r'<[^>]+>', ' ', q_html)
            q_text = html.unescape(q_text).strip()
            q_text = re.sub(r'\s+', ' ', q_text)
            if year != "N/A" and q_text.startswith(year):
                q_text = q_text[len(year):].strip()
        else:
            q_text = "Unknown Question"
            
        desc_match = re.search(r'<div[^>]*class="desc"[^>]*>', block, re.IGNORECASE)
        if desc_match:
            ans_start = desc_match.end()
            ans_html = block[ans_start:]
            ans_html = ans_html.strip()
            while True:
                prev_len = len(ans_html)
                ans_html = re.sub(r'</?(?:li|ul|div|p)>\s*$', '', ans_html, flags=re.IGNORECASE).strip()
                if len(ans_html) == prev_len:
                    break
                    
            extracted.append({
                "year": year,
                "question": q_text,
                "answer_html": ans_html
            })
            
    return extracted

def main():
    output_dir = "solved paper/drishti ias"
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    downloaded_images_cache = {}
    
    print("Starting full extraction of UPSC Mains Solved Papers...")
    
    for subject_name, url in SUBJECTS.items():
        print(f"\n==========================================")
        print(f"Processing Subject: {subject_name}")
        print(f"==========================================")
        
        max_retries = 3
        page_html = None
        for attempt in range(max_retries):
            try:
                req = urllib.request.Request(
                    url,
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                )
                with urllib.request.urlopen(req) as response:
                    page_html = response.read().decode('utf-8')
                break
            except Exception as e:
                print(f"  [Attempt {attempt+1}/{max_retries}] Error fetching page: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    
        if not page_html:
            print(f"  [ERROR] Failed to fetch page for {subject_name} after {max_retries} attempts. Skipping.")
            continue
            
        questions = extract_questions_and_answers(page_html)
        if not questions:
            print(f"  [WARNING] No solved questions extracted for {subject_name}.")
            continue
            
        print(f"  Found {len(questions)} solved questions. Formatting and saving...")
        
        markdown_content = f"# UPSC Mains Solved Papers - {subject_name}\n\n"
        markdown_content += f"This file contains all the {len(questions)} subject-wise solved papers extracted from Drishti IAS.\n\n---\n\n"
        
        for idx, q_data in enumerate(questions, 1):
            print(f"  [{idx}/{len(questions)}] Formatting Question: {q_data['question'][:50]}...")
            
            img_fn = make_download_image_fn(images_dir, subject_name, idx, downloaded_images_cache)
            
            converter = HTMLToMarkdown(download_img_fn=img_fn)
            cleaned_ans_html = clean_html_tags(q_data['answer_html'])
            try:
                converter.feed(cleaned_ans_html)
                parsed_ans_md = "".join(converter.markdown)
                normalized_md = parsed_ans_md.replace("\r\n", "\n").replace("\r", "\n")
                formatted_ans_md = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', normalized_md).strip()
            except Exception as parse_err:
                print(f"    [Error parsing answer HTML]: {parse_err}")
                formatted_ans_md = f"*(Error parsing HTML content)*\n\nRaw HTML:\n```html\n{q_data['answer_html']}\n```"
                
            markdown_content += f"## Question {idx} (Year: {q_data['year']})\n\n"
            markdown_content += f"**{q_data['question']}**\n\n"
            markdown_content += "### Answer\n\n"
            markdown_content += formatted_ans_md + "\n\n"
            markdown_content += "---\n\n"
            
        filename = "".join(c for c in subject_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_").lower() + ".md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"  [SUCCESS] Saved all {len(questions)} answers to {filepath}")
        
        time.sleep(1.5)
        
    print("\n==========================================")
    print("Full extraction completed successfully!")
    print("==========================================")

if __name__ == "__main__":
    main()
