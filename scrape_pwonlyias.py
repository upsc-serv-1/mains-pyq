import urllib.request
import os
import re
import html
import json
import time
import hashlib
from html.parser import HTMLParser

# Base URL
BASE_URL = "https://pwonlyias.com"
INDEX_URL = "https://pwonlyias.com/mains-solved-papers-by-year/"

# Normalized lowercase keys mapping to standard Subject names
SUBJECT_MAPPING = {
    # GS 1
    "art & culture": "Ancient History and Art & Culture",
    "ancient history": "Ancient History and Art & Culture",
    "medieval indian history": "Ancient History and Art & Culture",
    "modern history": "Modern History",
    "world history": "World History",
    "post-india indpendence": "Post Independent India",
    "post-india independence": "Post Independent India",
    "post independence": "Post Independent India",
    "post-independence history": "Post Independent India",
    "indian society": "Indian Society",
    "society": "Indian Society",
    "geography": "Geography",
    "physical geography": "Geography",
    "indian geography": "Geography",
    "world geography": "Geography",
    
    # GS 2
    "polity": "Polity",
    "indian polity": "Polity",
    "governance": "Governance",
    "social justice": "Social Justice",
    "international relations": "International Relations",
    "international relation": "International Relations",
    "general": "Polity",
    
    # GS 3
    "economy": "Economic Development",
    "economic development": "Economic Development",
    "indian economy": "Economic Development",
    "agriculture": "Agriculture",
    "environment": "Environment and Ecology",
    "environment & ecology": "Environment and Ecology",
    "science & technology": "Science & Technology",
    "science & tech": "Science & Technology",
    "science and technology": "Science & Technology",
    "science & technology's": "Science & Technology",
    "internal security": "Internal Security",
    "disaster management": "Disaster Management",
    "disaster managements": "Disaster Management",
    
    # GS 4
    "ethics (section a)": "Ethics (Theoretical Questions)",
    "ethics (section b)": "Ethics (Case Studies)",
    "ethics case study": "Ethics (Case Studies)",
    "ethics theory": "Ethics (Theoretical Questions)",
    "ethics": "Ethics (Theoretical Questions)" # Fallback
}

FILENAME_MAPPING = {
    "Ancient History and Art & Culture": "ancient_history_and_art__culture.md",
    "Modern History": "modern_history.md",
    "World History": "world_history.md",
    "Post Independent India": "post_independent_india.md",
    "Indian Society": "indian_society.md",
    "Geography": "geography.md",
    "Polity": "polity.md",
    "Governance": "governance.md",
    "Social Justice": "social_justice.md",
    "International Relations": "international_relations.md",
    "Economic Development": "economic_development.md",
    "Agriculture": "agriculture.md",
    "Environment and Ecology": "environment_and_ecology.md",
    "Science & Technology": "science__technology.md",
    "Internal Security": "internal_security.md",
    "Disaster Management": "disaster_management.md",
    "Ethics (Case Studies)": "ethics_case_studies.md",
    "Ethics (Theoretical Questions)": "ethics_theoretical_questions.md"
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
        self.list_item_just_started = False

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
                        self.current_cell += f" ![Image]({local_path}) "
            elif tag == 'br':
                if self.in_cell:
                    self.current_cell += "<br>"
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
            if self.list_item_just_started:
                self.list_item_just_started = False
            elif len(self.stack) >= 2 and self.stack[-2] == 'li':
                indent = "  " * (len(self.list_indices) - 1)
                self.markdown.append(f"\n{indent}")
            else:
                self.markdown.append("\n\n")
        elif tag == 'br':
            indent = "  " * len(self.list_indices)
            self.markdown.append(f"\n{indent}")
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
            self.list_item_just_started = True
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
                alt = attrs_dict.get('alt', 'Image')
                self.markdown.append(f'\n\n<p align="center"><img src="{local_path}" alt="{alt}" /></p>\n\n')

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
            if not self.stack or self.stack[-1] in ('ul', 'ol', 'li'):
                if not cleaned.strip():
                    return
            if self.list_item_just_started:
                if not cleaned.strip():
                    return
                else:
                    self.list_item_just_started = False
            self.markdown.append(cleaned)

def fetch_page(url, cache_path=None):
    if cache_path and os.path.exists(cache_path):
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception:
            pass
            
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                content = response.read().decode('utf-8')
                if cache_path:
                    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
                    with open(cache_path, "w", encoding="utf-8") as f:
                        f.write(content)
                return content
        except Exception as e:
            print(f"  [Attempt {attempt+1}/{max_retries}] Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1.5)
    return None

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s-]+', '-', text)
    text = text.strip('-')
    return text

def parse_metadata_from_title(title):
    words = "N/A"
    marks = "N/A"
    
    # Try finding patterns like (150 Words, 10 Marks) or [150 Words, 10 Marks]
    pattern = r'[\(\[]\s*(\d+)\s*[Ww]ords?\s*,\s*(\d+)\s*[Mm]arks?\s*[\)\]]'
    m = re.search(pattern, title)
    if m:
        words = m.group(1) + " Words"
        marks = m.group(2) + " Marks"
        clean_title = title[:m.start()].strip()
    else:
        # Try alternate patterns
        # e.g., Just marks: (10 Marks) or [10 Marks]
        m_marks = re.search(r'[\(\[]\s*(\d+)\s*[Mm]arks?\s*[\)\]]', title)
        if m_marks:
            marks = m_marks.group(1) + " Marks"
            clean_title = title[:m_marks.start()].strip()
        else:
            # Try just words
            m_words = re.search(r'[\(\[]\s*(\d+)\s*[Ww]ords?\s*[\)\]]', title)
            if m_words:
                words = m_words.group(1) + " Words"
                clean_title = title[:m_words.start()].strip()
            else:
                clean_title = title
            
    # Clean up quotes and trailing punctuation
    clean_title = clean_title.strip("'\u201c\u201d\" ")
    # Clean up Que. prefix
    clean_title = re.sub(r'^(?:Que\.|Q\.)\s*\d+\s*\.?\s*', '', clean_title, flags=re.IGNORECASE).strip()
    return clean_title, words, marks

def extract_pf_content_html(html_content):
    start_match = re.search(r'<div\s+class="pf-content">', html_content, re.IGNORECASE)
    if not start_match:
        start_match = re.search(r'class="[^"]*pf-content[^"]*"', html_content, re.IGNORECASE)
        if not start_match:
            return ""
        tag_start = html_content.rfind("<div", 0, start_match.start())
        if tag_start == -1:
            return ""
        start_pos = html_content.find(">", start_match.end()) + 1
    else:
        start_pos = start_match.end()
        
    open_divs = 1
    pos = start_pos
    while open_divs > 0 and pos < len(html_content):
        next_open = html_content.find("<div", pos)
        next_close = html_content.find("</div>", pos)
        
        if next_close == -1:
            break
            
        if next_open != -1 and next_open < next_close:
            open_divs += 1
            pos = next_open + 4
        else:
            open_divs -= 1
            pos = next_close + 6
            
    if open_divs == 0:
        ans_html = html_content[start_pos : pos - 6]
    else:
        ans_html = html_content[start_pos:]
        
    # Strip out printfriendly buttons from the end
    pf_idx = ans_html.find('<div class="printfriendly')
    if pf_idx != -1:
        ans_html = ans_html[:pf_idx]
        
    return ans_html.strip()

def clean_html_tags(raw_html):
    clean = re.sub(r'<script.*?>.*?</script>', '', raw_html, flags=re.DOTALL | re.IGNORECASE)
    clean = re.sub(r'<style.*?>.*?</style>', '', clean, flags=re.DOTALL | re.IGNORECASE)
    return clean

def make_download_image_fn(img_dir, subject_name, q_index, downloaded_cache):
    img_counter = [0]
    def download_image(src):
        if not src.startswith("http"):
            if src.startswith("/"):
                src = BASE_URL + src
            else:
                return src
        
        if src in downloaded_cache:
            return downloaded_cache[src]
            
        try:
            img_counter[0] += 1
            clean_sub = "".join(c for c in subject_name if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_").lower()
            
            ext = os.path.splitext(src.split("?")[0])[1]
            if not ext or ext.lower() not in ('.jpg', '.jpeg', '.png', '.gif', '.webp'):
                ext = '.png'
                
            filename = f"pw_{clean_sub}_q{q_index}_img{img_counter[0]}{ext}"
            os.makedirs(img_dir, exist_ok=True)
            filepath = os.path.join(img_dir, filename)
            
            req = urllib.request.Request(
                src,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                with open(filepath, 'wb') as out_file:
                    out_file.write(response.read())
            print(f"    Downloaded image: {src} -> {filepath}")
            local_rel_path = f"images/{filename}"
            downloaded_cache[src] = local_rel_path
            return local_rel_path
        except Exception as e:
            print(f"    Failed to download image {src}: {e}")
            return src
    return download_image

def main(test_mode=False):
    output_dir = os.path.join("upsc", "solved paper", "pwonlyias")
    images_dir = os.path.join(output_dir, "images")
    cache_dir = os.path.join(output_dir, "cache")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    os.makedirs(cache_dir, exist_ok=True)
    
    # Clean up old subject files in output directory if not in test_mode
    if not test_mode and os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".md") and not f.endswith("_test.md"):
                try:
                    os.remove(os.path.join(output_dir, f))
                except Exception as e:
                    print(f"    Failed to remove old file {f}: {e}")
                    
    downloaded_images_cache = {}
    
    print("Starting PWOnlyIAS extraction...")
    
    # Standard years
    if test_mode:
        years = ["2025", "2018"]
    else:
        years = [str(y) for y in range(2013, 2026)]
        
    print(f"Years to process: {years}")
    
    # Store questions grouped by subject
    # Format: { "Polity": [ { question, year, paper, marks, words, answer_md }, ... ] }
    subject_groups = {}
    total_processed = 0
    
    for year in years:
        print(f"\n==========================================")
        print(f"Processing Year: {year}")
        print(f"==========================================")
        
        if year in ("2018", "2019"):
            url = f"{BASE_URL}/mains-previous-year-solved-questions/gs-paper-{year}"
        else:
            url = f"{BASE_URL}/mains-solved-papers-by-year/gs-paper-{year}/"
            
        year_hash = hashlib.md5(url.encode('utf-8')).hexdigest()
        cache_path = os.path.join(cache_dir, f"year_{year}_{year_hash}.html")
        year_html = fetch_page(url, cache_path=cache_path)
        if not year_html:
            print(f"[WARNING] Failed to fetch index page for year {year}.")
            continue
            
        q_urls = []
        if year in ("2018", "2019"):
            headings = re.findall(r'<h[1-6][^>]*>(.*?)</h[1-6]>', year_html, re.IGNORECASE)
            for h in headings:
                h_clean = re.sub(r'<[^>]+>', '', h).strip()
                if h_clean.startswith("Que.") or h_clean.startswith("Que"):
                    q_text = re.sub(r'^Que\.\d+\s*', '', h_clean)
                    q_text = re.sub(r'^Que\d+\s*', '', q_text)
                    q_text = re.sub(r'^Que\s*\d+\s*', '', q_text)
                    
                    pattern = r'[\(\[]\s*\d+\s*[Ww]ords?\s*,\s*\d+\s*[Mm]arks?\s*[\)\]]'
                    q_text_no_meta = re.sub(pattern, '', q_text).strip()
                    q_text_no_meta = re.sub(r'[\(\[]\s*\d+\s*[Mm]arks?\s*[\)\]]', '', q_text_no_meta).strip()
                    q_text_no_meta = re.sub(r'[\(\[]\s*\d+\s*[Ww]ords?\s*[\)\]]', '', q_text_no_meta).strip()
                    
                    slug = slugify(q_text_no_meta)
                    if slug:
                        q_url = f"{BASE_URL}/pyq/{slug}/"
                        q_urls.append((q_url, h_clean))
            print(f"    Constructed {len(q_urls)} slug-based question URLs for legacy year {year}.")
        else:
            matches = re.findall(r'href=["\'](https://pwonlyias.com/pyq/[^"\']+)["\']', year_html)
            unique_matches = sorted(list(set(matches)))
            for q_url in unique_matches:
                q_urls.append((q_url, None))
            print(f"    Found {len(q_urls)} question URLs for standard year {year}.")
            
        if test_mode:
            q_urls = q_urls[:2]
            
        for idx, (q_url, original_heading) in enumerate(q_urls, 1):
            print(f"    [{idx}/{len(q_urls)}] Fetching: {q_url}")
            
            # Simple yield to other tasks/rate limit
            if not test_mode and idx % 20 == 0:
                time.sleep(0.1)
                
            q_hash = hashlib.md5(q_url.encode('utf-8')).hexdigest()
            q_cache_path = os.path.join(cache_dir, f"q_{year}_{q_hash}.html")
            q_html = fetch_page(q_url, cache_path=q_cache_path)
            if not q_html:
                print(f"      [WARNING] Failed to fetch question detail page.")
                continue
                
            h4_match = re.search(r'<h4[^>]*>(.*?)</h4>', q_html, re.DOTALL | re.IGNORECASE)
            if h4_match:
                title_html = h4_match.group(1)
                title_text = re.sub(r'<[^>]+>', '', title_html).strip()
            elif original_heading:
                title_text = original_heading
            else:
                title_text = "Unknown Question"
                
            clean_q_text, words_tag, marks_tag = parse_metadata_from_title(title_text)
            
            cat_match = re.search(r'<div class="vc_cat_div">(.*?)</div>', q_html, re.DOTALL | re.IGNORECASE)
            subject_tag = "General"
            paper_tag = "N/A"
            
            if cat_match:
                cat_content = cat_match.group(1)
                anchors = re.findall(r'<a[^>]*>(.*?)</a>', cat_content, re.IGNORECASE)
                for a in anchors:
                    a_clean = html.unescape(a).strip()
                    if "Paper" in a_clean:
                        paper_tag = a_clean.replace("GS Paper ", "GS ")
                    else:
                        subject_tag = a_clean
            
            # Subject mapping to standard name (using lowercase comparison)
            lookup_tag = subject_tag.lower().strip()
            mapped_subject = SUBJECT_MAPPING.get(lookup_tag, subject_tag)
            
            if paper_tag == "N/A":
                for p in ["GS Paper 1", "GS Paper 2", "GS Paper 3", "GS Paper 4"]:
                    if p in q_html:
                        paper_tag = p.replace("GS Paper ", "GS ")
                        break
                        
            if paper_tag == "N/A":
                if mapped_subject in ("Ancient History and Art & Culture", "Modern History", "World History", "Post Independent India", "Indian Society", "Geography"):
                    paper_tag = "GS 1"
                elif mapped_subject in ("Polity", "Governance", "Social Justice", "International Relations"):
                    paper_tag = "GS 2"
                elif mapped_subject in ("Economic Development", "Agriculture", "Environment and Ecology", "Science & Technology", "Internal Security", "Disaster Management"):
                    paper_tag = "GS 3"
                elif "Ethics" in mapped_subject:
                    paper_tag = "GS 4"
                    
            ans_html = extract_pf_content_html(q_html)
            if not ans_html:
                print("      [WARNING] Answer block HTML not found.")
                continue
                
            cleaned_ans_html = clean_html_tags(ans_html)
            cleaned_ans_html = re.sub(r'<p[^>]*>\s*(?:<strong>|<b>)?\s*Enroll now for.*?(?:</strong>|</b>)?\s*</p>', '', cleaned_ans_html, flags=re.IGNORECASE)
            cleaned_ans_html = re.sub(r'<div[^>]*>\s*(?:<strong>|<b>)?\s*Enroll now for.*?(?:</strong>|</b>)?\s*</div>', '', cleaned_ans_html, flags=re.IGNORECASE)
            
            img_fn = make_download_image_fn(images_dir, mapped_subject, total_processed + 1, downloaded_images_cache)
            converter = HTMLToMarkdown(download_img_fn=img_fn)
            
            try:
                converter.feed(cleaned_ans_html)
                parsed_ans_md = "".join(converter.markdown)
                normalized_md = parsed_ans_md.replace("\r\n", "\n").replace("\r", "\n")
                
                lines = normalized_md.split("\n")
                cleaned_lines = []
                for line in lines:
                    if re.search(r'Enroll now for.*', line, re.IGNORECASE):
                        continue
                    cleaned_lines.append(line)
                normalized_md = "\n".join(cleaned_lines)
                
                formatted_ans_md = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', normalized_md).strip()
            except Exception as parse_err:
                print(f"      [Error parsing answer HTML]: {parse_err}")
                formatted_ans_md = f"*(Error parsing HTML content)*\n\nRaw HTML:\n```html\n{ans_html}\n```"
                
            if mapped_subject not in subject_groups:
                subject_groups[mapped_subject] = []
                
            subject_groups[mapped_subject].append({
                "question": clean_q_text,
                "year": year,
                "paper": paper_tag,
                "marks": marks_tag,
                "words": words_tag,
                "answer_md": formatted_ans_md
            })
            
            total_processed += 1
            
    print(f"\n==========================================")
    print(f"Writing {total_processed} answers to subject files...")
    print(f"==========================================")
    
    for subject, q_list in subject_groups.items():
        filename = FILENAME_MAPPING.get(subject)
        if not filename:
            filename = "".join(c for c in subject if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_").lower() + ".md"
            
        filepath = os.path.join(output_dir, filename)
        
        q_list_sorted = sorted(q_list, key=lambda x: x['year'], reverse=True)
        
        markdown_content = f"# UPSC Mains Solved Papers - {subject} (PWOnlyIAS)\n\n"
        markdown_content += f"This file contains all the {len(q_list_sorted)} solved previous year questions extracted from PWOnlyIAS.\n\n---\n\n"
        
        for idx, q_data in enumerate(q_list_sorted, 1):
            markdown_content += f"## Question {idx} (Year: {q_data['year']} | Paper: {q_data['paper']} | Marks: {q_data['marks']} | Words: {q_data['words']})\n\n"
            markdown_content += f"**{q_data['question']}**\n\n"
            markdown_content += "### Answer\n\n"
            markdown_content += q_data['answer_md'] + "\n\n"
            markdown_content += "---\n\n"
            
        if test_mode:
            filepath = filepath.replace(".md", "_test.md")
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"  [SUCCESS] Saved all {len(q_list_sorted)} answers to {filepath}")
        
    print(f"\nPWOnlyIAS extraction completed! Total questions saved: {total_processed}")

if __name__ == "__main__":
    import sys
    test_run = "--test" in sys.argv
    main(test_mode=test_run)
