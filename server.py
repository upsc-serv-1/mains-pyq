import http.server
import socketserver
import urllib.parse
import json
import os
import re
import subprocess

import sys

PORT = 8000
if len(sys.argv) > 1:
    try:
        PORT = int(sys.argv[1])
    except ValueError:
        pass

WORKSPACE_DIR = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc"

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def translate_path(self, path):
        # Override to serve files from WORKSPACE_DIR
        parsed_url = urllib.parse.urlparse(path)
        path = urllib.parse.unquote(parsed_url.path)
        
        # If accessing the root, serve viewer_app/index.html
        if path == "/" or path == "":
            return os.path.join(WORKSPACE_DIR, "viewer_app", "index.html")
        
        rel_path = path.lstrip("/")
        
        # 1. Check if the file exists in the viewer_app directory
        # (This resolves relative HTML links like styles.css or app.js when accessed from root)
        viewer_app_path = os.path.join(WORKSPACE_DIR, "viewer_app", rel_path)
        if os.path.exists(viewer_app_path) and not os.path.isdir(viewer_app_path):
            return viewer_app_path
            
        # 2. Check if path starts with /viewer_app, serve relative to viewer_app
        if path.startswith("/viewer_app/"):
            rel_path_clean = path.replace("/viewer_app/", "", 1)
            return os.path.join(WORKSPACE_DIR, "viewer_app", rel_path_clean)
            
        # 3. Otherwise, serve relative to the root WORKSPACE_DIR
        return os.path.join(WORKSPACE_DIR, rel_path)

    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200, "ok")
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed_url.query)
        
        if parsed_url.path == "/api/get-questions":
            self.handle_get_questions(query_params)
        elif parsed_url.path == "/api/list-config":
            self.handle_list_config()
        else:
            super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        
        if parsed_url.path == "/api/save-answer":
            self.handle_save_answer()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_list_config(self):
        solved_paper_dir = os.path.join(WORKSPACE_DIR, "solved paper")
        coachings = set()
        
        # Scan directories gs1, gs2, gs3, gs4 to find all raw coaching files
        for paper in ["gs1", "gs2", "gs3", "gs4"]:
            paper_dir = os.path.join(solved_paper_dir, paper)
            if os.path.exists(paper_dir):
                for entry in os.scandir(paper_dir):
                    if entry.is_file() and entry.name.endswith(".md"):
                        match = re.match(r'^gs\d+_([a-zA-Z0-9_-]+)\.md$', entry.name)
                        if match:
                            coaching_suffix = match.group(1)
                            # Exclude master, audit, or report files
                            if "master" not in coaching_suffix and "audit" not in coaching_suffix and "report" not in coaching_suffix:
                                coaching_name = coaching_suffix.replace("_", " ")
                                coachings.add(coaching_name)
        
        subjects = ["gs1", "gs2", "gs3", "gs4"]
        
        response = {
            "coachings": sorted(list(coachings)),
            "subjects": subjects
        }
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(response).encode('utf-8'))

    def handle_get_questions(self, params):
        coaching = params.get("coaching", [""])[0]
        subject = params.get("subject", [""])[0]  # This is the GS Paper, e.g. "gs1", "gs2", etc.
        
        if not coaching or not subject:
            self.send_error(400, "Missing coaching or subject parameters")
            return
            
        coaching_suffix = coaching.lower().replace(" ", "_")
        file_path = os.path.join(WORKSPACE_DIR, "solved paper", subject, f"{subject}_{coaching_suffix}.md")
        if not os.path.exists(file_path):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"questions": [], "error": "File not found"}).encode('utf-8'))
            return
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            blocks = re.split(r'\n\s*(?:(?:-\s*){3,}|(?:\*\s*){3,})\n', content)
            questions = []
            
            for block in blocks:
                block_strip = block.strip()
                if not block_strip:
                    continue
                if block_strip.startswith("# ") or "This file contains" in block_strip:
                    continue
                    
                # Parse block
                header_match = re.match(r'^##\s+Question\s+(\d+)\s*(?:\(Year:\s*([^\)]+)\))?', block_strip)
                if not header_match:
                    continue
                    
                q_num = int(header_match.group(1))
                year_info = header_match.group(2) if header_match.group(2) else ""
                year_match = re.search(r'(\d{4})', year_info)
                year = year_match.group(1) if year_match else year_info
                
                parts = re.split(r'###\s*Answer', block_strip, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    # Strip the ## Question header prefix cleanly using regex
                    statement = re.sub(r'^##\s+Question\s+\d+\s*(?:\([^\)]*\))?\s*', '', parts[0], flags=re.IGNORECASE).strip()
                    answer = "### Answer".join(parts[1:]).strip()
                else:
                    statement = block_strip
                    answer = ""
                    
                questions.append({
                    "q_num": q_num,
                    "year": year,
                    "statement": statement,
                    "answer": answer
                })
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"questions": questions}).encode('utf-8'))
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def handle_save_answer(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        try:
            data = json.loads(post_data.decode('utf-8'))
            coaching = data.get("coaching")
            subject = data.get("subject")  # This is the GS Paper, e.g. "gs1", "gs2", etc.
            q_num = int(data.get("q_num"))
            new_answer = data.get("new_answer")
            
            if not coaching or not subject or q_num is None or new_answer is None:
                self.send_error(400, "Missing post parameters")
                return
                
            coaching_suffix = coaching.lower().replace(" ", "_")
            file_path = os.path.join(WORKSPACE_DIR, "solved paper", subject, f"{subject}_{coaching_suffix}.md")
            if not os.path.exists(file_path):
                self.send_error(404, "File not found")
                return
                
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            blocks = re.split(r'\n\s*(?:(?:-\s*){3,}|(?:\*\s*){3,})\n', content)
            updated_blocks = []
            file_header = ""
            changed = False
            
            for block in blocks:
                block_strip = block.strip()
                if not block_strip:
                    continue
                if block_strip.startswith("# ") or "This file contains" in block_strip:
                    file_header = block_strip
                    continue
                    
                header_match = re.match(r'^##\s+Question\s+(\d+)', block_strip)
                if header_match and int(header_match.group(1)) == q_num:
                    parts = re.split(r'###\s*Answer', block_strip, flags=re.IGNORECASE)
                    if len(parts) >= 2:
                        # Extract Question ID from parts[0]
                        qid_match = re.search(r'Question ID:\s*([a-zA-Z0-9_-]+)', parts[0], re.IGNORECASE)
                        qid = qid_match.group(1) if qid_match else None
                        
                        # Clean new_answer of any trailing Question ID brackets
                        clean_answer = re.sub(r'\[Question ID:.*?\]', '', new_answer, flags=re.IGNORECASE).strip()
                        clean_answer = re.sub(r'\r?\n---+$', '', clean_answer).strip()
                        
                        if qid:
                            final_answer = f"{clean_answer}\n\n[Question ID: {qid}]"
                        else:
                            final_answer = clean_answer
                        
                        new_block = f"{parts[0].strip()}\n\n### Answer\n\n{final_answer.strip()}"
                        updated_blocks.append(new_block)
                        changed = True
                    else:
                        updated_blocks.append(block_strip)
                else:
                    updated_blocks.append(block_strip)
                    
            if changed:
                new_content = ""
                if file_header:
                    new_content += file_header + "\n\n---\n\n"
                new_content += "\n\n---\n\n".join(updated_blocks)
                new_content += "\n\n---\n"
                
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(new_content)
                    
                print(f"Saved Question {q_num} in {subject}_{coaching_suffix}.md. Recompilation started...")
                fix_script = os.path.join(WORKSPACE_DIR, "scratch", "fix_drishti_all.py")
                if os.path.exists(fix_script):
                    subprocess.run(["python", fix_script], check=True)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Answer saved and recompiled!"}).encode('utf-8'))
            else:
                self.send_response(400)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({"error": f"Question {q_num} not found in file"}).encode('utf-8'))
                
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

def run():
    print(f"Starting server on port {PORT}...")
    print(f"Local editor address: http://localhost:{PORT}/viewer_app/editor.html")
    server_address = ('', PORT)
    httpd = socketserver.ThreadingTCPServer(server_address, CustomHandler)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == "__main__":
    run()
