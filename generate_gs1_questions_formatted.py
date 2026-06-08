import json
import os
import re

with open("gs1_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

def normalize_str(s):
    return re.sub(r"[^\w]", "", s.lower().strip())

def determine_tags_and_directives(question):
    q_lower = question.lower()
    macrotags = []
    microtags = []
    
    # 1. Descriptive
    descriptive_map = {
        "write short note": "Write short note",
        "write a note": "Write note",
        "throw light on": "Throw light on",
        "bring out": "Bring out",
        "underline": "Underline",
        "elaborate": "Elaborate",
        "define": "Define",
        "explain": "Explain",
        "describ": "Describe",
        "elucidate": "Elucidate",
        "what is": "What is",
        "what": "What",
        "why": "Why",
        "how": "How",
        "highlight": "Highlight",
        "enumerate": "Enumerate",
        "trace": "Trace",
        "clarify": "Clarify",
        "outline": "Outline",
        "delineate": "Delineate",
        "mention": "Mention",
        "indicate": "Indicate",
        "account for": "Account for"
    }
    des_matched = []
    for k, v in descriptive_map.items():
        if k in q_lower:
            if v not in des_matched:
                if v == "What" and "what is" in q_lower:
                    continue
                if v == "How" and "how far" in q_lower:
                    continue
                if v == "Write note" and "write short note" in q_lower:
                    continue
                des_matched.append(v)
    if des_matched:
        macrotags.append("Descriptive")
        microtags.extend(des_matched)
        
    # 2. Analytical
    analytical_map = {
        "critically examine": "Critically examine",
        "critically analyze": "Critically analyze",
        "critically evaluate": "Critically evaluate",
        "critical note": "Critical note",
        "do you agree": "Do you agree",
        "do you think": "Do you think",
        "how far": "How far",
        "substantiate": "Substantiate",
        "evaluate": "Evaluate",
        "analyze": "Analyze",
        "analyse": "Analyze",
        "discuss": "Discuss",
        "comment": "Comment",
        "assess": "Assess",
        "examine": "Examine",
        "argue": "Argue",
        "justify": "Justify"
    }
    ana_matched = []
    for k, v in analytical_map.items():
        if k in q_lower:
            if v not in ana_matched:
                if v == "Examine" and "critically examine" in q_lower:
                    continue
                if v == "Analyze" and "critically analyze" in q_lower:
                    continue
                if v == "Evaluate" and "critically evaluate" in q_lower:
                    continue
                ana_matched.append(v)
    if ana_matched:
        macrotags.append("Analytical")
        microtags.extend(ana_matched)
        
    # 3. Comparative
    comparative_map = {
        "compare": "Compare",
        "contrast": "Contrast",
        "distinguish": "Distinguish",
        "different": "Different",
        "differ": "Differ",
        "difference": "Difference",
        "differed": "Differed",
        "versus": "Versus",
        "vs": "Vs"
    }
    comp_matched = []
    for k, v in comparative_map.items():
        if k in q_lower:
            if v not in comp_matched:
                if v == "Differ" and ("different" in q_lower or "difference" in q_lower or "differed" in q_lower):
                    continue
                comp_matched.append(v)
    if comp_matched:
        macrotags.append("Comparative")
        microtags.extend(comp_matched)
        
    # 4. Applied
    applied_map = {
        "present-day": "Present-day",
        "present day": "Present day",
        "contemporary": "Contemporary",
        "modern india": "Modern India",
        "today": "Today",
        "relevance today": "Relevance today",
        "covid": "Covid",
        "pandemic": "Pandemic",
        "digital": "Digital",
        "cryptocurrency": "Cryptocurrency",
        "smart city": "Smart City",
        "artificial intelligence": "Artificial Intelligence",
        "drones": "Drones",
        "still prevailing": "Still prevailing",
        "prevailing in": "Prevailing",
        "current times": "Current times",
        "challenges in": "Challenges",
        "modern era": "Modern era",
        "since independence": "Since independence",
        "india": "India",
        "indian": "Indian",
        "policy": "Policy",
        "current event": "Current event",
        "problem": "Problem"
    }
    app_matched = []
    for k, v in applied_map.items():
        if k in q_lower:
            if v not in app_matched:
                if v == "India" and "modern india" in q_lower:
                    continue
                app_matched.append(v)
    if app_matched:
        macrotags.append("Applied")
        microtags.extend(app_matched)
        
    if not macrotags:
        macrotags.append("Analytical")
        microtags.append("Discuss")
        
    return ", ".join(macrotags), ", ".join(microtags)

# Parse hierarchy from taxonomy tree structure file
def load_hierarchy():
    hierarchy_map_3way = {}
    hierarchy_map_2way = {}
    
    subjects_order = []
    sections_order = {}
    topics_order = {}
    microthemes_order = {}
    
    subject = None
    bs = None
    topic = None
    
    path = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\syllabus hierarchy\gs1\GS1_Syllabus_Taxonomy_Hierarchy.md"
    if not os.path.exists(path):
        path = r"C:\Users\Dr. Yogesh\.gemini\antigravity\brain\c49261a9-6687-4e81-a5d3-757c25cdafa1\GS1_Syllabus_Taxonomy_Hierarchy.md"
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line_str = line.rstrip("\n")
            line_stripped = line_str.strip()
            if line_stripped.startswith("## SUBJECT:"):
                subject = line_stripped.split(":", 1)[1].strip()
                subject_title = subject.title()
                if subject_title not in subjects_order:
                    subjects_order.append(subject_title)
                if subject_title not in sections_order:
                    sections_order[subject_title] = []
            elif line_stripped.startswith("### Section Group:"):
                bs = line_stripped.split(":", 1)[1].strip()
                subject_title = subject.title()
                if bs not in sections_order[subject_title]:
                    sections_order[subject_title].append(bs)
                if (subject_title, bs) not in topics_order:
                    topics_order[(subject_title, bs)] = []
            elif line_str.startswith("- "):
                topic = line_str[2:].strip()
                subject_title = subject.title()
                if topic not in topics_order[(subject_title, bs)]:
                    topics_order[(subject_title, bs)].append(topic)
                if (subject_title, bs, topic) not in microthemes_order:
                    microthemes_order[(subject_title, bs, topic)] = []
            elif line_str.startswith("  - "):
                mt = line_str[4:].strip()
                subject_title = subject.title()
                if mt not in microthemes_order[(subject_title, bs, topic)]:
                    microthemes_order[(subject_title, bs, topic)].append(mt)
                
                subj_norm = normalize_str(subject_title)
                topic_norm = normalize_str(topic)
                mt_norm = normalize_str(mt)
                
                hierarchy_map_3way[(subj_norm, topic_norm, mt_norm)] = (subject_title, bs, topic, mt)
                hierarchy_map_2way[(subj_norm, mt_norm)] = (subject_title, bs, topic, mt)
                
    return subjects_order, sections_order, topics_order, microthemes_order, hierarchy_map_3way, hierarchy_map_2way

subjects_order, sections_order, topics_order, microthemes_order, hierarchy_map_3way, hierarchy_map_2way = load_hierarchy()

# Group questions
grouped = {}

for q in questions:
    q_subj = q["subject"]
    if q_subj == "Art and Culture":
        q_subj = "History"
    q_topic = q["topic"]
    q_mt = q["microtheme"]
    
    subj_norm = normalize_str(q_subj)
    topic_norm = normalize_str(q_topic)
    mt_norm = normalize_str(q_mt)
    
    match = hierarchy_map_3way.get((subj_norm, topic_norm, mt_norm))
    if not match:
        match = hierarchy_map_2way.get((subj_norm, mt_norm))
        
    if match:
        subject, bs, topic, microtheme = match
    else:
        subject = q_subj
        bs = "Social Dynamics & Ideologies"
        topic = q_topic
        microtheme = q_mt
    
    if subject not in grouped:
        grouped[subject] = {}
    if bs not in grouped[subject]:
        grouped[subject][bs] = {}
    if topic not in grouped[subject][bs]:
        grouped[subject][bs][topic] = {}
    if microtheme not in grouped[subject][bs][topic]:
        grouped[subject][bs][topic][microtheme] = []
        
    grouped[subject][bs][topic][microtheme].append(q)

# Generate Markdown in hierarchy ordering
md_content = []
md_content.append("# Paper: GS-I")
md_content.append("")

q_counter = 1
for subject in subjects_order:
    if subject not in grouped:
        continue
    md_content.append(f"## Subject: {subject.upper()}")
    md_content.append("")
    
    for bs in sections_order[subject]:
        if bs not in grouped[subject]:
            continue
    
        md_content.append(f"### Section Group: {bs}")
        md_content.append("")
        
        for topic in topics_order[(subject, bs)]:
            if topic not in grouped[subject][bs]:
                continue
            md_content.append(f"#### Microtopic: {topic}")
            md_content.append("")
            
            for subtopic in microthemes_order[(subject, bs, topic)]:
                if subtopic not in grouped[subject][bs][topic]:
                    continue
                md_content.append(f"##### Subtopic: {subtopic}")
                md_content.append("")
                
                # Output questions under this subtopic
                for q_data in grouped[subject][bs][topic][subtopic]:
                    pyq = q_data["question"].strip()
                    year = q_data["year"]
                    marks = q_data["marks"]
                    macro_tags, micro_tags = determine_tags_and_directives(pyq)
                    
                    md_content.append(f"Q{q_counter}. {pyq}")
                    q_counter += 1
                    md_content.append(f"[Year: {year}] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 1]")
                    md_content.append(f"[Subject: {subject.upper()}]")
                    md_content.append(f"[Section Group: {bs}]")
                    md_content.append(f"[Microtopic: {topic}]")
                    md_content.append(f"[Subtopic: {subtopic}]")
                    md_content.append(f"[Macrotag: {macro_tags}]")
                    md_content.append(f"[Microtag: {micro_tags}]")
                    md_content.append("")
                
                md_content.append("")

out_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\syllabus hierarchy\gs1"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "GS1_Syllabus_Questions_Formatted.md")

# Write to file
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_content).strip() + "\n")

print(f"Successfully generated formatted questions markdown at: {out_path}")
