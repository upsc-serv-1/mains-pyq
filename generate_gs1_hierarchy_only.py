import json
import os
import re

with open("gs1_questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

# Reference taxonomy mappings (same as in generate_final_gs1_v2)
def get_broad_section_group(topic_str):
    num_match = re.match(r"^(\d+)", topic_str)
    if not num_match:
        return "Unknown"
    topic_num = int(num_match.group(1))
    
    if topic_num == 1:
        return "Art and Culture"
    elif topic_num in [2, 3]:
        return "Modern History"
    elif topic_num == 4:
        return "Post Independence"
    elif topic_num == 5:
        return "World History"
    elif topic_num in [6, 7, 8, 9, 10]:
        return "Society"
    elif topic_num in [11, 14]:
        return "Physical Geography & Geophysical Phenomena"
    elif topic_num in [12, 13]:
        return "Economic & Resource Geography"
    elif topic_num == 15:
        return "Environmental Geography & Climate Dynamics"
    return "Unknown"

# Custom mapping for Society based on User's Final Complete 5-Layer Society Taxonomy
society_mapping = {
    "family": ("Foundations & Diversity", "Salient features of Indian Society"),
    "uniqueness of indian society": ("Foundations & Diversity", "Salient features of Indian Society"),
    "diversity and pluralism": ("Foundations & Diversity", "Diversity of India"),
    "tribes & related issues": ("Foundations & Diversity", "Diversity of India"),
    "globalisation": ("Social Dynamics & Ideologies", "Effects of globalization on Indian society"),
    "communalism": ("Social Dynamics & Ideologies", "National Integration, communalism, regionalism & secularism"),
    "regionalism": ("Social Dynamics & Ideologies", "National Integration, communalism, regionalism & secularism"),
    "secularism": ("Social Dynamics & Ideologies", "National Integration, communalism, regionalism & secularism"),
    "caste system": ("Social Dynamics & Ideologies", "National Integration, communalism, regionalism & secularism"),
    "miscellaneous": ("Social Dynamics & Ideologies", "National Integration, communalism, regionalism & secularism"),
    "women and associated concerns": ("Gender & Demographics", "Role of women and women's organization"),
    "population and associated issues": ("Gender & Demographics", "Population and associated issues (Added to house the PDF microtheme)"),
    "social empowerment": ("Poverty, Empowerment & Development", "Social empowerment, poverty and developmental issues"),
    "poverty and related issues": ("Poverty, Empowerment & Development", "Social empowerment, poverty and developmental issues"),
    "development and related issues": ("Poverty, Empowerment & Development", "Social empowerment, poverty and developmental issues"),
    "urban water management": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)"),
    "environmental issues": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)"),
    "urban planning": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)"),
    "urban poverty and migration": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)"),
    "urban poverty and migra- tion": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)"),
    "emerging urbanisation trends": ("Urbanisation", "Urbanisation: problems and remedies (Added to house the PDF microthemes)")
}

# Group paths by Subject -> Broad Section Group -> Topic (Syllabus Point) -> Microtheme
grouped = {}

for q in questions:
    subject = q["subject"]
    if subject == "Art and Culture":
        subject = "History"
    topic = q["topic"]
    microtheme = q["microtheme"]
    
    if subject == "Society":
        mt_key = microtheme.lower().strip()
        if mt_key in society_mapping:
            broad_section, topic = society_mapping[mt_key]
        else:
            broad_section = "Social Dynamics & Ideologies"
            topic = "National Integration, communalism, regionalism & secularism"
    else:
        mt_key = microtheme.lower().strip()
        if mt_key in ["revolt and mutiny", "socio-religious reform", "viceroy and their adminis- tration", "viceroy and their administration"]:
            topic = "02. Modern Indian History-Mid-18th century - Present (significant events, personalities, issues);"
        broad_section = get_broad_section_group(topic)
        
    mt_clean = microtheme.replace("\n", " ").replace("\x07", "").strip()
    
    if subject not in grouped:
        grouped[subject] = {}
    if broad_section not in grouped[subject]:
        grouped[subject][broad_section] = {}
    if topic not in grouped[subject][broad_section]:
        grouped[subject][broad_section][topic] = set()
    grouped[subject][broad_section][topic].add(mt_clean)

# Format markdown in the UPSC CMS Taxonomy Hierarchy format:
# ## SUBJECT: <Name>
# ### Section Group: <Name>
# - <Syllabus Point>
#   - <Microtheme>
md_content = []

for subject in sorted(grouped.keys()):
    md_content.append(f"## SUBJECT: {subject.upper()}")
    md_content.append("")
    
    for bs in sorted(grouped[subject].keys()):
        md_content.append(f"### Section Group: {bs}")
        
        for topic in sorted(grouped[subject][bs].keys()):
            clean_topic = re.sub(r"^\d+\.\s*", "", topic).strip()
            md_content.append(f"- {clean_topic}")
            
            # Sort microthemes for a clean layout
            for microtheme in sorted(list(grouped[subject][bs][topic])):
                md_content.append(f"  - {microtheme}")
        
        md_content.append("") # Extra newline between section groups

out_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\syllabus hierarchy"
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "GS1_Syllabus_Taxonomy_Hierarchy.md")

# Write to file
with open(out_path, "w", encoding="utf-8") as f:
    f.write("\n".join(md_content).strip() + "\n")

print(f"Successfully generated hierarchy-only markdown at: {out_path}")
