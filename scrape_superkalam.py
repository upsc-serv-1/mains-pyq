import urllib.request
import os
import re
import html
import json
import time
from html.parser import HTMLParser

# Base URL
BASE_URL = "https://superkalam.com"
INDEX_URL = "https://superkalam.com/upsc-mains/previous-year-question-paper"

# Subject mapping from Superkalam tags to Drishti IAS subject names
SUBJECT_MAPPING = {
    "Art & Culture": "Ancient History and Art & Culture",
    "Ancient History": "Ancient History and Art & Culture",
    "Modern History": "Modern History",
    "World History": "World History",
    "Post Independence History": "Post Independent India",
    "Indian Society": "Indian Society",
    "Physical Geography": "Geography",
    "Indian Geography": "Geography",
    "World Geography": "Geography",
    "Geography": "Geography",
    "Indian Polity": "Polity",
    "Polity": "Polity",
    "Governance": "Governance",
    "Social Justice": "Social Justice",
    "International Relations": "International Relations",
    "Economy": "Economic Development",
    "Economic Development": "Economic Development",
    "Agriculture": "Agriculture",
    "Environment & Ecology": "Environment and Ecology",
    "Science & Technology": "Science & Technology",
    "Internal Security": "Internal Security",
    "Disaster Management": "Disaster Management",
    "Ethics Case Study": "Ethics (Case Studies)",
    "Ethics: Case Study": "Ethics (Case Studies)",
    "Ethics Theory": "Ethics (Theoretical Questions)",
    "Ethics: Theory": "Ethics (Theoretical Questions)"
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

def fetch_page(url):
    max_retries = 3
    for attempt in range(max_retries):
        try:
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req) as response:
                return response.read().decode('utf-8')
        except Exception as e:
            print(f"  [Attempt {attempt+1}/{max_retries}] Error fetching {url}: {e}")
            if attempt < max_retries - 1:
                time.sleep(1.5)
    return None

def extract_years(index_html):
    # Year paths look like: /upsc-mains/previous-year-question-paper/2025
    years = re.findall(r'href=["\']/upsc-mains/previous-year-question-paper/(\d{4})["\']', index_html)
    return sorted(list(set(years)), reverse=True)

def extract_question_urls(paper_html):
    # Try to find JSON-LD script first
    urls = []
    scripts = re.findall(r'<script type="application/ld\+json">(.*?)</script>', paper_html, re.DOTALL)
    for script in scripts:
        try:
            data = json.loads(script)
            if data.get("@type") == "ItemList":
                for item in data.get("itemListElement", []):
                    q_url = item.get("url")
                    if q_url:
                        urls.append(q_url)
        except Exception:
            pass
            
    # Fallback to standard regex match if list empty
    if not urls:
        matches = re.findall(r'href=["\'](/upsc-mains/previous-year-question-paper/\d{4}/[^"\'#]+)["\']', paper_html)
        for m in matches:
            if not m.endswith("/gs-paper-1") and not m.endswith("/gs-paper-2") and not m.endswith("/gs-paper-3") and not m.endswith("/ethics"):
                url = m if m.startswith("http") else BASE_URL + m
                urls.append(url)
                
    return sorted(list(set(urls)))

def extract_markdownanswer_html(html_content):
    start_match = re.search(r'<div\s+class="text-base\s+markdownanswer\s+w-full[^"]*">', html_content, re.IGNORECASE)
    if not start_match:
        return ""
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
        return html_content[start_pos : pos - 6]
    else:
        return html_content[start_pos:]

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
                
            filename = f"superkalam_{clean_sub}_q{q_index}_img{img_counter[0]}{ext}"
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

def main():
    output_dir = os.path.join("upsc", "solved paper", "superkalam")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    # Clean up old markdown files in output directory
    if os.path.exists(output_dir):
        for f in os.listdir(output_dir):
            if f.endswith(".md"):
                try:
                    os.remove(os.path.join(output_dir, f))
                except Exception as e:
                    print(f"    Failed to remove old file {f}: {e}")
                    
    downloaded_images_cache = {}
    
    print("Starting Superkalam extraction...")
    index_html = fetch_page(INDEX_URL)
    if not index_html:
        print("[ERROR] Failed to fetch Superkalam main index page.")
        return
        
    years = extract_years(index_html)
    print(f"Found {len(years)} years: {years}")
    
    # Store questions grouped by subject
    # Format: { "Indian Society": [ { question, year, paper, marks, answer_md }, ... ] }
    subject_groups = {}
    
    # Track metrics
    total_processed = 0
    
    for year in years:
        print(f"\n==========================================")
        print(f"Processing Year: {year}")
        print(f"==========================================")
        
        papers = [
            ("GS 1", f"{BASE_URL}/upsc-mains/previous-year-question-paper/{year}/gs-paper-1"),
            ("GS 2", f"{BASE_URL}/upsc-mains/previous-year-question-paper/{year}/gs-paper-2"),
            ("GS 3", f"{BASE_URL}/upsc-mains/previous-year-question-paper/{year}/gs-paper-3"),
            ("Ethics", f"{BASE_URL}/upsc-mains/previous-year-question-paper/{year}/ethics")
        ]
        
        for paper_name, paper_url in papers:
            print(f"  Fetching paper: {paper_name} ({paper_url})")
            paper_html = fetch_page(paper_url)
            if not paper_html:
                print(f"    [WARNING] Skip: Paper not found or failed to fetch.")
                continue
                
            q_urls = extract_question_urls(paper_html)
            print(f"    Found {len(q_urls)} questions.")
            
            for q_idx, q_url in enumerate(q_urls, 1):
                if not q_url.startswith("http"):
                    q_url = BASE_URL + q_url
                    
                print(f"    [{q_idx}/{len(q_urls)}] Fetching: {q_url}")
                time.sleep(0.5)
                
                q_html = fetch_page(q_url)
                if not q_html:
                    print(f"      [WARNING] Failed to fetch question detail page.")
                    continue
                    
                # Extract tags (Subject, Marks, Year, Paper)
                tag_matches = re.findall(r'<div[^>]*style="background-color:[^"]*"[^>]*>([^<]+)</div>', q_html)
                
                # Filter tags
                subject_tag = "General"
                marks_tag = "N/A"
                year_tag = year
                paper_tag = paper_name
                
                for tag in tag_matches:
                    tag_clean = tag.strip()
                    if tag_clean.isdigit() and len(tag_clean) == 4:
                        year_tag = tag_clean
                    elif "Mark" in tag_clean:
                        marks_tag = tag_clean
                    elif tag_clean in ("GS 1", "GS 2", "GS 3", "GS 4", "Ethics"):
                        paper_tag = tag_clean
                    else:
                        subject_tag = html.unescape(tag_clean).strip()
                        
                # Map subject to Drishti IAS format
                mapped_subject = SUBJECT_MAPPING.get(subject_tag, subject_tag)
                
                # Extract question text from title tag
                title_match = re.search(r'<title>(.*?)</title>', q_html, re.IGNORECASE)
                question_text = "Unknown Question"
                if title_match:
                    title_text = title_match.group(1).strip()
                    # Strip suffix if present
                    suffix_match = re.search(r'\s*\|\s*UPSC Mains.*', title_text, re.IGNORECASE)
                    if suffix_match:
                        question_text = title_text[:suffix_match.start()].strip()
                    else:
                        question_text = title_text
                        
                # Extract model answer HTML
                ans_html = extract_markdownanswer_html(q_html)
                if not ans_html:
                    print("      [WARNING] Answer block HTML not found.")
                    continue
                    
                # Format to Markdown
                img_fn = make_download_image_fn(images_dir, mapped_subject, total_processed + 1, downloaded_images_cache)
                converter = HTMLToMarkdown(download_img_fn=img_fn)
                cleaned_ans_html = clean_html_tags(ans_html)
                
                try:
                    converter.feed(cleaned_ans_html)
                    parsed_ans_md = "".join(converter.markdown)
                    normalized_md = parsed_ans_md.replace("\r\n", "\n").replace("\r", "\n")
                    formatted_ans_md = re.sub(r'\n[ \t]*\n(?:[ \t]*\n)+', '\n\n', normalized_md).strip()
                except Exception as parse_err:
                    print(f"      [Error parsing answer HTML]: {parse_err}")
                    formatted_ans_md = f"*(Error parsing HTML content)*\n\nRaw HTML:\n```html\n{ans_html}\n```"
                
                # Add to subject group
                if mapped_subject not in subject_groups:
                    subject_groups[mapped_subject] = []
                    
                subject_groups[mapped_subject].append({
                    "question": question_text,
                    "year": year_tag,
                    "paper": paper_tag,
                    "marks": marks_tag,
                    "answer_md": formatted_ans_md
                })
                
                total_processed += 1
                
    # Step 6: Write all files grouped by subject
    print(f"\n==========================================")
    print(f"Writing {total_processed} answers to subject files...")
    print(f"==========================================")
    
    for subject, q_list in subject_groups.items():
        # Match Drishti filename pattern
        clean_sub_filename = "".join(c for c in subject if c.isalnum() or c in (" ", "_", "-")).replace(" ", "_").lower() + ".md"
        filepath = os.path.join(output_dir, clean_sub_filename)
        
        # Sort questions by year (descending)
        q_list_sorted = sorted(q_list, key=lambda x: x['year'], reverse=True)
        
        markdown_content = f"# UPSC Mains Solved Papers - {subject} (Superkalam)\n\n"
        markdown_content += f"This file contains all the {len(q_list_sorted)} solved previous year questions extracted from Superkalam.\n\n---\n\n"
        
        for idx, q_data in enumerate(q_list_sorted, 1):
            markdown_content += f"## Question {idx} (Year: {q_data['year']} | Paper: {q_data['paper']} | Marks: {q_data['marks']})\n\n"
            markdown_content += f"**{q_data['question']}**\n\n"
            markdown_content += "### Answer\n\n"
            markdown_content += q_data['answer_md'] + "\n\n"
            markdown_content += "---\n\n"
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        print(f"  [SUCCESS] Saved all {len(q_list_sorted)} answers to {filepath}")
        
    print(f"\nSuperkalam extraction completed! Total questions saved: {total_processed}")

if __name__ == "__main__":
    main()
