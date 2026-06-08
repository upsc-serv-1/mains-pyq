import json
import re
import os

with open("gs1_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Stop words to filter out for Layer 6 (short description)
STOP_WORDS = {
    "a", "an", "the", "and", "or", "but", "if", "then", "else", "when", "where", "why", "how", "what",
    "who", "whom", "which", "this", "that", "these", "those", "is", "am", "are", "was", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "to", "of", "in", "on", "at", "by",
    "for", "with", "about", "against", "between", "into", "through", "during", "before", "after",
    "above", "below", "from", "up", "down", "in", "out", "over", "under", "again", "further", "then",
    "once", "here", "there", "when", "where", "why", "how", "all", "any", "both", "each", "few",
    "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", "same", "so", "than",
    "too", "very", "s", "t", "can", "will", "just", "don", "should", "now", "d", "ll", "m", "o", "re",
    "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven", "isn", "ma", "mightn",
    "mustn", "needn", "shan", "shouldn", "wasn", "weren", "won", "wouldn",
    # Directive verbs to remove from short descriptions
    "discuss", "explain", "critically", "examine", "evaluate", "comment", "analyze", "analyse",
    "assess", "highlight", "enumerate", "trace", "clarify", "estimate", "underline", "delineate",
    "describe", "define", "write", "note", "elucidate", "substantiate", "bring", "out", "show",
    "compare", "contrast", "distinguish", "account", "suggest", "measures", "reconstruct", "historical",
    "sources", "source", "aspects", "features", "role", "impact", "effects", "consequences",
    "significance", "importance", "nature", "contribution", "contributions", "development"
}

custom_overrides = {
    # Page 6 & 7 (Art & Culture)
    "discuss the tandava dance as recorded in the early indian inscriptions.": "Tandava dance inscriptions",
    "safeguarding the indian art heritage is the need of the moment. discuss.": "Safeguarding art heritage",
    "evaluate the nature of the bhakti literature and its contribution to indian culture.": "Bhakti literature contribution",
    "the bhakti movement received a remarkable re-orientation with the advent of sri chaitanya mahaprabhu. discuss.": "Chaitanya Bhakti re-orientation",
    "sufis and medieval mystic saints failed to modify either the religious ideas and prac- tices or the outward structure of hindu/muslim societies to any appreciable extent. comment.": "Sufi movement limitations",
    "highlight the central asian and greco -bactrian elements in gandhara art.": "Gandhara art elements",
    "early buddhist stupa-art, while depicting folk motifs and narratives successfully expounds buddhist ideals. elucidate.": "Buddhist Stupa-art motifs",
    "gandhara sculpture owed as much to the romans as to the greeks. explain.": "Gandhara Greco-Roman influence",
    "discuss the salient features of the harappan architecture.": "Harappan architecture features",
    "underline the changes in the field of society and economy from the rig vedic to the later vedic period.": "Vedic socio-economic transition",
    "what are the main features of vedic society and religion? do you think some of the features are still prevailing in indian society?": "Vedic society continuity",
    "the ancient civilization in indian sub-continent differed from those of egypt, meso- potamia and greece in that its culture and traditions have been preserved without a breakdown to the present day. comment.": "Indian tradition continuity",
    "to what extent has the urban planning and culture of the Indus Valley Civilization provided inputs to the present day urbanization? discuss.": "Harappan urban influence",
    "indian philosophy and tradition played a significant role in conceiving and shaping the monuments and their art in india. discuss.": "Indian philosophy monuments",
    "‘the sculptors filled the chandella artform with resilient vigor and breadth of life.’ elucidate.": "Chandella artform vigor",
    "estimate the contribution of pallavas of kanchi for the development of art and litera- ture of south india.": "Pallava art literature",
    "“though the great cholas are no more yet their name is still remembered with great pride because of their highest achievements in the domain of art and architecture.” comment.": "Chola art achievements",
    "what were the major technological changes introduced during the sultanate peri- od? how did those technological changes influence the indian society?": "Sultanate technological changes",
    "discuss the main contributions of gupta period and chola period to indian heritage and culture.": "Gupta-Chola heritage contributions",
    "pala period is the most significant phase in the history of buddhism in india. enu- merate.": "Pala Buddhism significance",
    "how do you justify the view that the level of excellence of gupta numismatic art is not at all noticeable in later times?": "Gupta numismatic excellence",
    "chola architecture represents a high watermark in the evolution of temple architec- ture. discuss.": "Chola temple architecture",
    "examine the main aspects of akbar’s religious syncretism.": "Akbar religious syncretism",
    "krishnadeva raya, the king of vijayanagar, was not only an accomplished scholar himself but was also a great patron of learning and literature. discuss.": "Krishnadeva Raya patronage",
    "explain the role of geographical factors towards the development of ancient india.": "Ancient geography factors",
    "taxila university was one of the oldest universities of the world with which were associated a number of renowned learned personalities of different disciplines. its strategic location caused its fame to flourish, but unlike nalanda, it is not considered as a university in the modern sense. discuss.": "Taxila university comparison",
    "assess the importance of the accounts of the chinese and arab travellers in the reconstruction of the history of india.": "Foreign travellers accounts",
    "how will you explain that medieval indian temple sculptures represent the social life of those days?": "Sculptures social life",
    "discuss the significance of the lion and bull figures in indian mythology, art and architecture.": "Lion bull iconography",
    "the rock-cut architecture represents one of the most important sources of our knowledge of early indian art and history. discuss.": "Rock-cut architecture sources",
    "mesolithic rock cut architecture of india not only reflects the cultural life of the times but also a tine aesthetic sense comparable to modern painting. critically evaluate this comment.": "Mesolithic rock aesthetics",
    "persian literary sources of medieval india reflect the spirit of the age. comment.": "Persian literary sources",
    "though not very useful from the point of view of a connected political history of south india, the sangam literature portrays the social and economic conditions of its time with remarkable vividness. comment.": "Sangam literature portrayal",
}

def clean_and_tokenize(text):
    text = text.lower()
    text = re.sub(r"[^\w\s-]", "", text)
    tokens = text.split()
    return tokens

def generate_short_desc(question, microtheme):
    q_norm = question.strip().lower()
    for k, v in custom_overrides.items():
        if k in q_norm or q_norm in k:
            return v
            
    tokens = clean_and_tokenize(question)
    filtered = [t for t in tokens if t not in STOP_WORDS]
    
    if len(filtered) > 3:
        mt_tokens = clean_and_tokenize(microtheme)
        mt_filtered = [t for t in mt_tokens if t not in STOP_WORDS]
        if mt_filtered:
            best_words = []
            for t in filtered:
                if t in mt_filtered and t not in best_words:
                    best_words.append(t)
            for t in filtered:
                if t not in best_words:
                    best_words.append(t)
                if len(best_words) == 3:
                    break
            desc = " ".join(best_words)
        else:
            desc = " ".join(filtered[:3])
    else:
        desc = " ".join(filtered)
        
    desc = desc.title().strip()
    words = desc.split()
    if len(words) > 3:
        words = words[:3]
    return " ".join(words)

def determine_tag(question, marks_str):
    try:
        m_str = re.sub(r"[^\d.]", "", marks_str)
        marks = float(m_str)
    except:
        marks = 15.0
        
    if marks == 10.0:
        return "Short Note"
        
    q_lower = question.lower()
    
    if any(w in q_lower for w in ["compare", "contrast", "distinguish", "difference", "differed", "versus", "vs"]):
        return "Comparative"
        
    applied_keywords = [
        "present-day", "present day", "contemporary", "modern india", "today", 
        "relevance today", "covid", "pandemic", "digital", "cryptocurrency", 
        "smart city", "artificial intelligence", "drones", "still prevailing",
        "prevailing in", "current times", "challenges in", "modern era", "since independence"
    ]
    if any(w in q_lower for w in applied_keywords):
        return "Applied"
        
    analytical_verbs = ["critically", "evaluate", "analyze", "analyse", "discuss", "comment", "assess", "examine", "argue", "justify"]
    if any(v in q_lower for v in analytical_verbs):
        return "Analytical"
        
    descriptive_verbs = ["define", "explain", "describe", "elucidate", "what is", "highlight", "enumerate", "trace", "clarify", "outline", "delineate"]
    if any(v in q_lower for v in descriptive_verbs):
        return "Descriptive"
        
    return "Analytical"

def normalize_str(s):
    return re.sub(r"[^\w]", "", s.lower().strip())

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
    
    # Resolve hierarchy details dynamically
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
        
    pyq = q["question"]
    marks = q["marks"]
    year = q["year"]
    
    short_desc = generate_short_desc(pyq, microtheme)
    tag = determine_tag(pyq, marks)
    
    grouped[subject][bs][topic][microtheme].append({
        "question": pyq,
        "year": year,
        "marks": marks,
        "short_desc": short_desc,
        "tag": tag
    })

# Format Markdown using the exact tree order from hierarchy file
md_content = []
md_content.append("# UPSC GS Mains Paper 1 (GS-I) Syllabus Hierarchy & Tagged PYQs")
md_content.append("\nThis document contains the complete question bank of GS-I (2013-2025) structured into a 6-layer syllabus hierarchy and tagged with behavioral metadata.\n")

# Table of Contents
md_content.append("## Table of Contents")
for subject in subjects_order:
    if subject not in grouped:
        continue
    subj_anchor = subject.lower().replace(" ", "-").replace("&", "")
    md_content.append(f"- [{subject}](#subject-{subj_anchor})")
    
    for bs in sections_order[subject]:
        if bs not in grouped[subject]:
            continue
        bs_anchor = bs.lower().replace(" ", "-").replace("&", "")
        md_content.append(f"  - [{bs}](#section-{bs_anchor})")
        
        for topic in topics_order[(subject, bs)]:
            if topic not in grouped[subject][bs]:
                continue
            num_match = re.match(r"^(\d+)\.", topic)
            if num_match:
                topic_num = num_match.group(1)
                topic_text = topic.split(".", 1)[1].strip()
                topic_anchor = f"topic-{topic_num}"
                md_content.append(f"    - [Topic {topic_num}: {topic_text[:50]}...](#{topic_anchor})")
            else:
                topic_anchor = topic.lower().replace(" ", "-").replace("&", "").replace(":", "").replace("(", "").replace(")", "")
                md_content.append(f"    - [{topic[:50]}...](#{topic_anchor})")

md_content.append("\n---\n")

# Main Content in order of taxonomy tree
for subject in subjects_order:
    if subject not in grouped:
        continue
    subj_anchor = subject.lower().replace(" ", "-").replace("&", "")
    md_content.append(f"## SUBJECT: {subject} <a name=\"subject-{subj_anchor}\"></a>\n")
    
    for bs in sections_order[subject]:
        if bs not in grouped[subject]:
            continue
        bs_anchor = bs.lower().replace(" ", "-").replace("&", "")
        md_content.append(f"### Broad Section Group: {bs} <a name=\"section-{bs_anchor}\"></a>\n")
        
        for topic in topics_order[(subject, bs)]:
            if topic not in grouped[subject][bs]:
                continue
            num_match = re.match(r"^(\d+)\.", topic)
            if num_match:
                topic_num = num_match.group(1)
                topic_anchor = f"topic-{topic_num}"
            else:
                topic_anchor = topic.lower().replace(" ", "-").replace("&", "").replace(":", "").replace("(", "").replace(")", "")
            md_content.append(f"#### Syllabus Point: {topic} <a name=\"{topic_anchor}\"></a>\n")
            
            for microtheme in microthemes_order[(subject, bs, topic)]:
                if microtheme not in grouped[subject][bs][topic]:
                    continue
                md_content.append(f"##### Microtheme: {microtheme}\n")
                
                for q_data in grouped[subject][bs][topic][microtheme]:
                    q_text = q_data["question"]
                    year = q_data["year"]
                    marks = q_data["marks"]
                    short_desc = q_data["short_desc"]
                    tag = q_data["tag"]
                    
                    topic_name = topic.split('.', 1)[1].strip() if '.' in topic else topic
                    path = f"GS-I ➔ {subject} ➔ {bs} ➔ {topic_name} ➔ {microtheme} ➔ {short_desc}"
                    
                    md_content.append(f"*   **Q.** {q_text}")
                    md_content.append(f"    *   **Year**: {year} | **Marks**: {marks}")
                    md_content.append(f"    *   **Short Description (Layer 6)**: {short_desc}")
                    md_content.append(f"    *   **Behavioral Tag**: {tag}")
                    md_content.append(f"    *   **Path**: `{path}`")
                    md_content.append("")
                md_content.append("")

out_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\syllabus hierarchy\gs1"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "GS1_Syllabus_Hierarchy.md")

with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_content))

print(f"Generated 6-layer GS1 Syllabus Hierarchy at: {out_path}")
