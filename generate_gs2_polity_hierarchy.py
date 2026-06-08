import pdfplumber
import json
import re
import os

pdf_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\Civilsdaily GS Mains Microthemes_2025 Edition.pdf"
out_dir = r"c:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\syllabus hierarchy\gs2"
os.makedirs(out_dir, exist_ok=True)

artifact_dir = r"C:\Users\Dr. Yogesh\.gemini\antigravity\brain\c49261a9-6687-4e81-a5d3-757c25cdafa1"

# Verbatim GS2 topics
gs2_topics = {
    1: "01. Indian Constitution-Historical underpinnings & evolution; Features, amendments, significant provisions, basic structure of Constitution",
    2: "02. Functions & responsibilities of the Union and the States; issues and challenges of federal structure;",
    3: "03. Separation of Powers between different organs, dispute redressal mechanisms and institutions",
    4: "04. Devolution of powers and finances up to local levels and challenges therein",
    5: "05. Comparison of Indian constitutional scheme with other countries’",
    6: "06. Parliament and State Legislatures (structure, functioning, conduct of business, powers & privileges; issues therein)",
    7: "07. Structure, organization and functioning of the Executive and the Judiciary–Ministries and Departments of the Government; pressure groups and formal/informal associations and their role in the Polity",
    8: "08. Salient features of the Representation of People’s Act.",
    9: "09. Appointment to various Constitutional posts; Constitutional Bodies (powers, functions and responsibilities); Statutory, Regulatory and Quasi-judicial bodies",
    10: "10. Government Policies & Interventions for development of various sectors (issues in their design, implementation)",
    11: "11. Development processes and the development industry –the role of NGOs, SHGs, various groups and associations, donors, charities, institutional and other stakeholders.",
    12: "12. Welfare schemes for vulnerable sections of the population by the Centre and States and the performance of these schemes; mechanisms, laws, institutions and Bodies constituted for the protection and betterment of these vulnerable sections.",
    13: "13. Issues relating to development and management of Social Sector/Services relating to Health, Education, Human Resources.",
    14: "14. Issues relating to poverty and hunger",
    15: "15. Transaparency and accountability (institutional and other measures); Citizens Charter, E-Governance (applications, models, successes, limitations, potential)",
    16: "16. Role of Civil Services in a democracy.",
    17: "17. India and its neighborhood- relations.",
    18: "18. Bilateral, regional and global groupings and agreements involving India and/or affecting India’s interests.",
    19: "19. Effect of policies and politics of developed and developing countries on India’s interests, Indian diaspora.",
    20: "20. Important International institutions, agencies and fora- their structure, mandate."
}

# Mapping of microthemes to Broad Section Group (Layer 3), Topic (Layer 4), and Microtheme (Layer 5) for Polity
polity_taxonomy_map = {
    # Broad Section Group: Constitutional Framework & Evolution
    "making of the constitution": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Indian Constitution- historical underpinnings and evolution",
        "microtheme": "Making of the Constitution"
    },
    "amendments": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Features, amendments, significant provisions and basic structure",
        "microtheme": "Amendments"
    },
    "case laws": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Features, amendments, significant provisions and basic structure",
        "microtheme": "Case Laws"
    },
    "constitutional morality": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Features, amendments, significant provisions and basic structure",
        "microtheme": "Constitutional Morality"
    },
    "dpsp": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Fundamental Rights, Preamble, DPSP, Fundamental Duties, etc.",
        "microtheme": "DPSP"
    },
    "fundamental rights": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Fundamental Rights, Preamble, DPSP, Fundamental Duties, etc.",
        "microtheme": "Fundamental Rights"
    },
    "constitutional comparison": {
        "section": "Constitutional Framework & Evolution",
        "topic": "Comparison of the Indian constitutional scheme with that of other countries",
        "microtheme": "Constitutional Comparison"
    },

    # Broad Section Group: Federal Structure & Local Governance
    "emergency": {
        "section": "Federal Structure & Local Governance",
        "topic": "Functions and responsibilities of the Union and the States",
        "microtheme": "Emergency"
    },
    "special provisions": {
        "section": "Federal Structure & Local Governance",
        "topic": "Functions and responsibilities of the Union and the States",
        "microtheme": "Special Provisions"
    },
    "federalism": {
        "section": "Federal Structure & Local Governance",
        "topic": "Issues and challenges pertaining to the federal structure",
        "microtheme": "Federalism"
    },
    "union territory": {
        "section": "Federal Structure & Local Governance",
        "topic": "Issues and challenges pertaining to the federal structure",
        "microtheme": "Union Territory"
    },
    "local self government": {
        "section": "Federal Structure & Local Governance",
        "topic": "Devolution of powers and finances up to local levels and challenges therein",
        "microtheme": "Local Self Government"
    },

    # Broad Section Group: Organs of Government & Dispute Redressal
    "separation of powers": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Separation of powers between different organs",
        "microtheme": "Separation of Powers"
    },
    "executive vs judiciary": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Separation of powers between different organs",
        "microtheme": "Executive Vs Judiciary"
    },
    "judiciary vs legislature": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Separation of powers between different organs",
        "microtheme": "Judiciary Vs Legislature"
    },
    "executive vs legislature": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Separation of powers between different organs",
        "microtheme": "Executive Vs Legislature"
    },
    "bicameralism": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Parliament and State Legislatures - structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "microtheme": "Bicameralism"
    },
    "parliamentary committees": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Parliament and State Legislatures - structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "microtheme": "Parliamentary Committees"
    },
    "parliamentary privileges": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Parliament and State Legislatures - structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "microtheme": "Parliamentary Privileges"
    },
    "presiding officers": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Parliament and State Legislatures - structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "microtheme": "Presiding Officers"
    },
    "role of mps": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Parliament and State Legislatures - structure, functioning, conduct of business, powers & privileges and issues arising out of these",
        "microtheme": "Role of MPs"
    },
    "union executive": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Structure, organization and functioning of the Executive",
        "microtheme": "Union Executive"
    },
    "judiciary": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Structure, organization and functioning of the Judiciary (including Tribunals & ADR)",
        "microtheme": "Judiciary"
    },
    "alternate dispute resolution": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Structure, organization and functioning of the Judiciary (including Tribunals & ADR)",
        "microtheme": "Alternate Dispute Resolution"
    },
    "tribunal": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Structure, organization and functioning of the Judiciary (including Tribunals & ADR)",
        "microtheme": "Tribunal"
    },
    "informal associations and their role in polity": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Pressure groups and formal/informal associations and their role in the Polity",
        "microtheme": "Informal associations and their role in polity"
    },
    "pressure groups": {
        "section": "Organs of Government & Dispute Redressal",
        "topic": "Pressure groups and formal/informal associations and their role in the Polity",
        "microtheme": "Pressure Groups"
    },

    # Broad Section Group: Elections & Political Dynamics
    "election dispute and disqualification": {
        "section": "Elections & Political Dynamics",
        "topic": "Salient features of the Representation of People's Act",
        "microtheme": "Election Dispute and Disqualification"
    },
    "electoral reforms": {
        "section": "Elections & Political Dynamics",
        "topic": "Salient features of the Representation of People's Act",
        "microtheme": "Electoral reforms"
    },
    "mcc": {
        "section": "Elections & Political Dynamics",
        "topic": "Salient features of the Representation of People's Act",
        "microtheme": "MCC"
    },
    "political parties": {
        "section": "Elections & Political Dynamics",
        "topic": "Salient features of the Representation of People's Act",
        "microtheme": "Political Parties"
    }
}

# Mapping of microthemes to Broad Section Group (Layer 3), Topic (Layer 4), and Microtheme (Layer 5) for Governance
governance_taxonomy_map = {
    # Broad Section Group: Constitutional & Regulatory Bodies
    "constitutional bodies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Appointment to various Constitutional posts; Constitutional Bodies (powers, functions and responsibilities)",
        "microtheme": "Constitutional Bodies"
    },
    "enforcement agencies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Statutory, Regulatory and Quasi-judicial bodies",
        "microtheme": "Enforcement Agencies"
    },
    "quasi-judicial bodies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Statutory, Regulatory and Quasi-judicial bodies",
        "microtheme": "Quasi judicial Bodies"
    },
    "quasi judicial bodies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Statutory, Regulatory and Quasi-judicial bodies",
        "microtheme": "Quasi judicial Bodies"
    },
    "sectoral regulatory bodies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Statutory, Regulatory and Quasi-judicial bodies",
        "microtheme": "Sectoral Regulatory Bodies"
    },
    "statutory bodies": {
        "section": "Constitutional & Regulatory Bodies",
        "topic": "Statutory, Regulatory and Quasi-judicial bodies",
        "microtheme": "Statutory Bodies"
    },

    # Broad Section Group: Development Processes & Policies
    "government schemes and policies": {
        "section": "Development Processes & Policies",
        "topic": "Government Policies & Interventions for development of various sectors (issues in their design, implementation)",
        "microtheme": "Government Schemes and Policies"
    },
    "structural reforms and actions": {
        "section": "Development Processes & Policies",
        "topic": "Government Policies & Interventions for development of various sectors (issues in their design, implementation)",
        "microtheme": "Structural reforms and Actions"
    },
    "civil society": {
        "section": "Development Processes & Policies",
        "topic": "Development processes and the role of NGOs, Civil Society, and various groups and associations",
        "microtheme": "Civil Society"
    },
    "shgs": {
        "section": "Development Processes & Policies",
        "topic": "Role of Self Help Groups (SHGs) and microfinancing in development activities",
        "microtheme": "SHGs"
    },
    "donor agencies": {
        "section": "Development Processes & Policies",
        "topic": "Role of donors, charities, institutional and other external stakeholders",
        "microtheme": "Donor Agencies"
    },

    # Broad Section Group: Accountability & Civil Services
    "citizens charter": {
        "section": "Accountability & Civil Services",
        "topic": "Transaparency and accountability (institutional and other measures); Citizens Charter",
        "microtheme": "Citizens Charter"
    },
    "transparency and accountability": {
        "section": "Accountability & Civil Services",
        "topic": "Transaparency and accountability (institutional and other measures); Citizens Charter",
        "microtheme": "Transaparency and Account-ability"
    },
    "e-governance": {
        "section": "Accountability & Civil Services",
        "topic": "E-Governance (applications, models, successes, limitations, potential)",
        "microtheme": "E-governance"
    },
    "civil services": {
        "section": "Accountability & Civil Services",
        "topic": "Role of Civil Services in a democracy",
        "microtheme": "Civil Services"
    }
}




# Mapping of microthemes to Broad Section Group (Layer 3), Topic (Layer 4), and Microtheme (Layer 5) for Social Justice (User Edited Headers)
social_justice_taxonomy_map = {
    "children": {
        "section": "Vulnerable Sections & Welfare",
        "topic": "Welfare Schemes (Vulnerable Sections): Performance, Mechanisms, Laws, Institutions & Bodies",
        "microtheme": "Children"
    },
    "disables": {
        "section": "Vulnerable Sections & Welfare",
        "topic": "Welfare Schemes (Vulnerable Sections): Performance, Mechanisms, Laws, Institutions & Bodies",
        "microtheme": "Disables"
    },
    "disabled and vulnerable sections": {
        "section": "Vulnerable Sections & Welfare",
        "topic": "Welfare Schemes (Vulnerable Sections): Performance, Mechanisms, Laws, Institutions & Bodies",
        "microtheme": "Disables"
    },
    "efficacy of welfare and development schemes": {
        "section": "Vulnerable Sections & Welfare",
        "topic": "Welfare Schemes (Vulnerable Sections): Performance, Mechanisms, Laws, Institutions & Bodies",
        "microtheme": "Efficacy of Welfare and Development Schemes"
    },
    "women": {
        "section": "Vulnerable Sections & Welfare",
        "topic": "Welfare Schemes (Vulnerable Sections): Performance, Mechanisms, Laws, Institutions & Bodies",
        "microtheme": "Women"
    },
    "education": {
        "section": "Social Sector & Human Development",
        "topic": "Social Sector & Services: Issues relating to Development & Management of Health, Education & Human Resources",
        "microtheme": "Education"
    },
    "health": {
        "section": "Social Sector & Human Development",
        "topic": "Social Sector & Services: Issues relating to Development & Management of Health, Education & Human Resources",
        "microtheme": "Health"
    },
    "human resources": {
        "section": "Social Sector & Human Development",
        "topic": "Social Sector & Services: Issues relating to Development & Management of Health, Education & Human Resources",
        "microtheme": "Human Resources"
    },
    "miscellenous (social sector)": {
        "section": "Social Sector & Human Development",
        "topic": "Social Sector & Services: Issues relating to Development & Management of Health, Education & Human Resources",
        "microtheme": "Miscellenous (Social Sector)"
    },
    "hunger": {
        "section": "Poverty & Hunger",
        "topic": "Issues and Challenges relating to Poverty & Hunger",
        "microtheme": "Hunger"
    },
    "poverty": {
        "section": "Poverty & Hunger",
        "topic": "Issues and Challenges relating to Poverty & Hunger",
        "microtheme": "Poverty"
    },
    "miscellenous (poverty & hunger)": {
        "section": "Poverty & Hunger",
        "topic": "Issues and Challenges relating to Poverty & Hunger",
        "microtheme": "Miscellenous (Poverty & Hunger)"
    }
}

# Mapping of microthemes to Broad Section Group (Layer 3), Topic (Layer 4), and Microtheme (Layer 5) for International Relations
international_relations_taxonomy_map = {
    "neighbourhood": {
        "section": "Neighborhood & Bilateral Engagements",
        "topic": "Neighborhood Relations: India & its Neighborhood-Relations",
        "microtheme": "Neighbourhood"
    },
    "bilateral relations": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Groupings & Agreements: Bilateral, Regional & Global Groupings & Agreements Involving or Affecting India's Interests",
        "microtheme": "Bilateral Relations"
    },
    "groupings beyond south asia": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Groupings & Agreements: Bilateral, Regional & Global Groupings & Agreements Involving or Affecting India's Interests",
        "microtheme": "Groupings beyond South Asia"
    },
    "groupings involving immediate and extended neighbours": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Groupings & Agreements: Bilateral, Regional & Global Groupings & Agreements Involving or Affecting India's Interests",
        "microtheme": "Groupings involving Immediate and Extended neighbours"
    },
    "energy x foreign policy": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Global Policies & Politics: Effect of Policies & Politics of Developed & Developing Countries on India's Interests",
        "microtheme": "Energy X Foreign Policy"
    },
    "geo-politics affecting india's interest": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Global Policies & Politics: Effect of Policies & Politics of Developed & Developing Countries on India's Interests",
        "microtheme": "Geo-politics affecting India's Interest"
    },
    "miscelleneous (global geopolitics)": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Global Policies & Politics: Effect of Policies & Politics of Developed & Developing Countries on India's Interests",
        "microtheme": "Miscelleneous (Global Geopolitics)"
    },
    "indian diaspora": {
        "section": "Global Geopolitics & Indian Diaspora",
        "topic": "Indian Diaspora: Economic, Political & Social Impact of the Indian Diaspora",
        "microtheme": "Indian Diaspora"
    },
    "international funding agencies": {
        "section": "International Organizations",
        "topic": "International Institutions: Structure, Mandate & Functioning of Important Agencies & Fora",
        "microtheme": "International Funding Agencies"
    },
    "united nations and its agencies": {
        "section": "International Organizations",
        "topic": "International Institutions: Structure, Mandate & Functioning of Important Agencies & Fora",
        "microtheme": "United Nations and its Agencies"
    },
    "wto": {
        "section": "International Organizations",
        "topic": "International Institutions: Structure, Mandate & Functioning of Important Agencies & Fora",
        "microtheme": "WTO"
    }
}

# Normalizer for GS2 microthemes
def normalize_microtheme(mt):
    if not mt:
        return ""
    mt_clean = mt.replace("\n", " ").replace("\x07", "").strip()
    mt_clean = re.sub(r'\s+', ' ', mt_clean)
    
    mt_lower = mt_clean.lower()
    if "disqualification" in mt_lower or "dis- qualification" in mt_lower:
        return "Election Dispute and Disqualification"
    if "transaparency" in mt_lower or "transparency" in mt_lower:
        return "Transparency and Accountability"
    if "efficacy of welfare" in mt_lower:
        return "Efficacy of Welfare and Development Schemes"
    if "groupings involving" in mt_lower:
        return "Groupings involving Immediate and Extended neighbours"
    if "groupings beyond" in mt_lower:
        return "Groupings beyond South Asia"
    if "energy x" in mt_lower:
        return "Energy X Foreign Policy"
    if "geo-politics" in mt_lower:
        return "Geo-politics affecting India's Interest"
    if "united nations" in mt_lower:
        return "United Nations and its Agencies"
    if "informal associations" in mt_lower:
        return "Informal associations and their role in polity"
    if "disables" in mt_lower:
        return "Disabled and Vulnerable Sections"
    
    return mt_clean

# Bounding box coordinates logic to determine active topic
topic_pat = re.compile(r"\b(0[1-9]|1[0-9]|20)\b")

def determine_tags_and_directives(question):
    q_lower = question.lower()
    macrotags = []
    microtags = []
    
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
        
    def clean_tags(tag_list):
        seen = set()
        clean = []
        for t in tag_list:
            if t not in seen:
                seen.add(t)
                clean.append(t)
        return ", ".join(clean)
        
    return clean_tags(macrotags), clean_tags(microtags)

questions = []
active_topic_num = 1

with pdfplumber.open(pdf_path) as pdf:
    for page_num in range(26, 49):
        page = pdf.pages[page_num - 1]
        tables = page.find_tables()
        words = page.extract_words()
        
        for t_idx, table in enumerate(tables):
            # 1. Resolve Active Topic
            y_top = 0
            if t_idx > 0:
                y_top = tables[t_idx-1].bbox[3]
            y_bottom = table.bbox[1]
            
            words_in_range = [w for w in words if y_top <= w['top'] <= y_bottom]
            
            lines = {}
            for w in words_in_range:
                found = False
                for t in lines:
                    if abs(t - w['top']) < 3:
                        lines[t].append(w)
                        found = True
                        break
                if not found:
                    lines[w['top']] = [w]
                    
            header_text = ""
            for t in sorted(lines.keys()):
                line_words = sorted(lines[t], key=lambda x: x['x0'])
                header_text += " " + " ".join([w['text'] for w in line_words])
            
            match = topic_pat.search(header_text)
            if match:
                active_topic_num = int(match.group(1))
                
            resolved_topic_num = active_topic_num
            if page_num == 30:
                if t_idx == 0:
                    resolved_topic_num = 5
                elif t_idx == 1:
                    resolved_topic_num = 4
            
            # 2. Extract rows
            table_data = table.page.extract_tables()[t_idx]
            start_row = 0
            if table_data[0][0] == "Microthemes" or table_data[0][1] == "UPSC PYQs":
                start_row = 1
                
            current_microtheme = ""
            for row in table_data[start_row:]:
                if len(row) < 4:
                    continue
                
                mt = row[0]
                pyq = row[1]
                year = row[2]
                marks = row[3]
                
                if not pyq or pyq.strip() == "" or pyq.strip() == "UPSC PYQs":
                    continue
                
                pyq_clean = pyq.replace("\n", " ").replace("\x07", "").strip()
                year_clean = year.strip() if year else ""
                marks_clean = marks.strip() if marks else ""
                
                if mt and mt.strip():
                    current_microtheme = normalize_microtheme(mt)
                
                # Context-aware adjustments
                if current_microtheme == "Disabled and Vulnerable Sections":
                    current_microtheme = "Disables"
                elif current_microtheme in ["Miscellenous", "Miscelleneous"]:
                    if resolved_topic_num == 13:
                        current_microtheme = "Miscellenous (Social Sector)"
                    elif resolved_topic_num == 14:
                        current_microtheme = "Miscellenous (Poverty & Hunger)"
                    elif resolved_topic_num == 19:
                        current_microtheme = "Miscelleneous (Global Geopolitics)"
                
                mt_key = current_microtheme.lower().strip()
                if mt_key in governance_taxonomy_map:
                    subject = "Governance"
                elif mt_key in polity_taxonomy_map:
                    subject = "Polity"
                elif mt_key in social_justice_taxonomy_map:
                    subject = "Social Justice"
                elif mt_key in international_relations_taxonomy_map:
                    subject = "International Relations"
                else:
                    if resolved_topic_num in [9, 10, 11, 15, 16]:
                        subject = "Governance"
                    elif resolved_topic_num in [12, 13, 14]:
                        subject = "Social Justice"
                    elif resolved_topic_num in [17, 18, 19, 20]:
                        subject = "International Relations"
                    else:
                        subject = "Polity"
                    
                questions.append({
                    "page": page_num,
                    "table_index": t_idx,
                    "subject": subject,
                    "topic": gs2_topics[resolved_topic_num],
                    "microtheme": current_microtheme,
                    "question": pyq_clean,
                    "year": year_clean,
                    "marks": marks_clean
                })

print(f"Total GS2 questions extracted: {len(questions)}")

# Save database JSON
with open("gs2_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=4)
print("Saved to gs2_questions.json")


# ==================== COMPILE SINGLE GS2 HIERARCHY ====================

polity_sections_order = [
    "Constitutional Framework & Evolution",
    "Federal Structure & Local Governance",
    "Organs of Government & Dispute Redressal",
    "Elections & Political Dynamics"
]

governance_sections_order = [
    "Constitutional & Regulatory Bodies",
    "Development Processes & Policies",
    "Accountability & Civil Services"
]

social_justice_sections_order = [
    "Vulnerable Sections & Welfare",
    "Social Sector & Human Development",
    "Poverty & Hunger"
]

international_relations_sections_order = [
    "Neighborhood & Bilateral Engagements",
    "Global Geopolitics & Indian Diaspora",
    "International Organizations"
]

# Build Hierarchy Map
hierarchy_tree = {
    "POLITY": {},
    "GOVERNANCE": {},
    "SOCIAL_JUSTICE": {},
    "INTERNATIONAL_RELATIONS": {}
}

# 1. Populate Polity hierarchy tree
for mt_val in polity_taxonomy_map.values():
    sec = mt_val["section"]
    top = mt_val["topic"]
    mt = mt_val["microtheme"]
    if sec not in hierarchy_tree["POLITY"]:
        hierarchy_tree["POLITY"][sec] = {}
    if top not in hierarchy_tree["POLITY"][sec]:
        hierarchy_tree["POLITY"][sec][top] = []
    if mt not in hierarchy_tree["POLITY"][sec][top]:
        hierarchy_tree["POLITY"][sec][top].append(mt)

# 2. Populate Governance hierarchy tree
for mt_val in governance_taxonomy_map.values():
    sec = mt_val["section"]
    top = mt_val["topic"]
    mt = mt_val["microtheme"]
    if sec not in hierarchy_tree["GOVERNANCE"]:
        hierarchy_tree["GOVERNANCE"][sec] = {}
    if top not in hierarchy_tree["GOVERNANCE"][sec]:
        hierarchy_tree["GOVERNANCE"][sec][top] = []
    if mt not in hierarchy_tree["GOVERNANCE"][sec][top]:
        hierarchy_tree["GOVERNANCE"][sec][top].append(mt)

# 3. Populate Social Justice hierarchy tree
for mt_val in social_justice_taxonomy_map.values():
    sec = mt_val["section"]
    top = mt_val["topic"]
    mt = mt_val["microtheme"]
    if sec not in hierarchy_tree["SOCIAL_JUSTICE"]:
        hierarchy_tree["SOCIAL_JUSTICE"][sec] = {}
    if top not in hierarchy_tree["SOCIAL_JUSTICE"][sec]:
        hierarchy_tree["SOCIAL_JUSTICE"][sec][top] = []
    if mt not in hierarchy_tree["SOCIAL_JUSTICE"][sec][top]:
        hierarchy_tree["SOCIAL_JUSTICE"][sec][top].append(mt)

# 4. Populate International Relations hierarchy tree
for mt_val in international_relations_taxonomy_map.values():
    sec = mt_val["section"]
    top = mt_val["topic"]
    mt = mt_val["microtheme"]
    if sec not in hierarchy_tree["INTERNATIONAL_RELATIONS"]:
        hierarchy_tree["INTERNATIONAL_RELATIONS"][sec] = {}
    if top not in hierarchy_tree["INTERNATIONAL_RELATIONS"][sec]:
        hierarchy_tree["INTERNATIONAL_RELATIONS"][sec][top] = []
    if mt not in hierarchy_tree["INTERNATIONAL_RELATIONS"][sec][top]:
        hierarchy_tree["INTERNATIONAL_RELATIONS"][sec][top].append(mt)

# Generate combined Taxonomy Hierarchy markdown content
combined_tax_md = []
combined_tax_md.append("# UPSC GS Mains Paper 2 (GS-II) Syllabus Hierarchy")
combined_tax_md.append("")
combined_tax_md.append("This document outlines the structured 5-layer taxonomy of the GS-II syllabus, organizing Polity, Governance, Social Justice, and International Relations topics into logical section groups.")
combined_tax_md.append("")

# Subject: POLITY
combined_tax_md.append("## SUBJECT: POLITY")
combined_tax_md.append("")
for sec in polity_sections_order:
    combined_tax_md.append(f"### Section Group: {sec}")
    for top in hierarchy_tree["POLITY"].get(sec, {}):
        combined_tax_md.append(f"- {top}")
        for mt in sorted(hierarchy_tree["POLITY"][sec][top]):
            combined_tax_md.append(f"  - {mt}")
    combined_tax_md.append("")

# Subject: GOVERNANCE
combined_tax_md.append("## SUBJECT: GOVERNANCE")
combined_tax_md.append("")
for sec in governance_sections_order:
    combined_tax_md.append(f"### Section Group: {sec}")
    for top in hierarchy_tree["GOVERNANCE"].get(sec, {}):
        combined_tax_md.append(f"- {top}")
        for mt in sorted(hierarchy_tree["GOVERNANCE"][sec][top]):
            combined_tax_md.append(f"  - {mt}")
    combined_tax_md.append("")

# Subject: SOCIAL JUSTICE
combined_tax_md.append("## SUBJECT: SOCIAL JUSTICE")
combined_tax_md.append("")
for sec in social_justice_sections_order:
    combined_tax_md.append(f"### Section Group: {sec}")
    for top in hierarchy_tree["SOCIAL_JUSTICE"].get(sec, {}):
        combined_tax_md.append(f"- {top}")
        for mt in sorted(hierarchy_tree["SOCIAL_JUSTICE"][sec][top]):
            combined_tax_md.append(f"  - {mt}")
    combined_tax_md.append("")

# Subject: INTERNATIONAL RELATIONS
combined_tax_md.append("## SUBJECT: INTERNATIONAL RELATIONS")
combined_tax_md.append("")
for sec in international_relations_sections_order:
    combined_tax_md.append(f"### Section Group: {sec}")
    for top in hierarchy_tree["INTERNATIONAL_RELATIONS"].get(sec, {}):
        combined_tax_md.append(f"- {top}")
        for mt in sorted(hierarchy_tree["INTERNATIONAL_RELATIONS"][sec][top]):
            combined_tax_md.append(f"  - {mt}")
    combined_tax_md.append("")

combined_tax_md_content = "\n".join(combined_tax_md).strip() + "\n"

# Write combined taxonomy hierarchy files
with open(os.path.join(out_dir, "GS2_Syllabus_Hierarchy.md"), "w", encoding="utf-8") as f:
    f.write(combined_tax_md_content)
with open(os.path.join(artifact_dir, "GS2_Syllabus_Hierarchy.md"), "w", encoding="utf-8") as f:
    f.write(combined_tax_md_content)
print("Saved GS2_Syllabus_Hierarchy.md")

# ==================== COMPILE SINGLE FORMATTED QUESTIONS ====================

polity_questions = []
governance_questions = []
social_justice_questions = []
international_relations_questions = []

for q in questions:
    mt_key = q["microtheme"].lower().strip()
    
    if q["subject"] == "Polity":
        tax_info = polity_taxonomy_map.get(mt_key)
        if not tax_info:
            tax_info = {
                "section": "Constitutional Framework & Evolution",
                "topic": q["topic"],
                "microtheme": q["microtheme"]
            }
        polity_questions.append({
            "question": q["question"],
            "year": q["year"],
            "marks": q["marks"],
            "section": tax_info["section"],
            "topic": tax_info["topic"],
            "microtheme": tax_info["microtheme"]
        })
        
    elif q["subject"] == "Governance":
        tax_info = governance_taxonomy_map.get(mt_key)
        if not tax_info:
            tax_info = {
                "section": "Constitutional & Regulatory Bodies" if "bodies" in mt_key or "enforcement" in mt_key else "Development Processes & Policies",
                "topic": q["topic"],
                "microtheme": q["microtheme"]
            }
        governance_questions.append({
            "question": q["question"],
            "year": q["year"],
            "marks": q["marks"],
            "section": tax_info["section"],
            "topic": tax_info["topic"],
            "microtheme": tax_info["microtheme"]
        })
        
    elif q["subject"] == "Social Justice":
        tax_info = social_justice_taxonomy_map.get(mt_key)
        if not tax_info:
            tax_info = {
                "section": "Vulnerable Sections & Welfare",
                "topic": q["topic"],
                "microtheme": q["microtheme"]
            }
        social_justice_questions.append({
            "question": q["question"],
            "year": q["year"],
            "marks": q["marks"],
            "section": tax_info["section"],
            "topic": tax_info["topic"],
            "microtheme": tax_info["microtheme"]
        })
        
    elif q["subject"] == "International Relations":
        tax_info = international_relations_taxonomy_map.get(mt_key)
        if not tax_info:
            tax_info = {
                "section": "Neighborhood & Bilateral Engagements",
                "topic": q["topic"],
                "microtheme": q["microtheme"]
            }
        international_relations_questions.append({
            "question": q["question"],
            "year": q["year"],
            "marks": q["marks"],
            "section": tax_info["section"],
            "topic": tax_info["topic"],
            "microtheme": tax_info["microtheme"]
        })

print(f"Polity: {len(polity_questions)} questions, Governance: {len(governance_questions)} questions, Social Justice: {len(social_justice_questions)} questions, IR: {len(international_relations_questions)} questions.")

combined_q_md = []
combined_q_md.append("# Paper: GS-II")
combined_q_md.append("")

q_counter = 1

# 1. Output SUBJECT: POLITY
combined_q_md.append("## Subject: POLITY")
combined_q_md.append("")

polity_grouped = {}
for q in polity_questions:
    sec = q["section"]
    top = q["topic"]
    mt = q["microtheme"]
    if sec not in polity_grouped:
        polity_grouped[sec] = {}
    if top not in polity_grouped[sec]:
        polity_grouped[sec][top] = {}
    if mt not in polity_grouped[sec][top]:
        polity_grouped[sec][top][mt] = []
    polity_grouped[sec][top][mt].append(q)

for sec in polity_sections_order:
    if sec not in polity_grouped:
        continue
    combined_q_md.append(f"### Section Group: {sec}")
    combined_q_md.append("")
    for top in hierarchy_tree["POLITY"].get(sec, {}):
        if top not in polity_grouped[sec]:
            continue
        combined_q_md.append(f"#### Microtopic: {top}")
        combined_q_md.append("")
        for mt in sorted(hierarchy_tree["POLITY"][sec][top]):
            if mt not in polity_grouped[sec][top]:
                continue
            combined_q_md.append(f"##### Subtopic: {mt}")
            combined_q_md.append("")
            sorted_qs = sorted(polity_grouped[sec][top][mt], key=lambda x: x["year"], reverse=True)
            for q in sorted_qs:
                text = q["question"]
                yr = q["year"]
                macro, micro = determine_tags_and_directives(text)
                combined_q_md.append(f"Q{q_counter}. {text}")
                combined_q_md.append(f"[Year: {yr}] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 2]")
                combined_q_md.append(f"[Subject: POLITY]")
                combined_q_md.append(f"[Section Group: {sec}]")
                combined_q_md.append(f"[Microtopic: {top}]")
                combined_q_md.append(f"[Subtopic: {mt}]")
                combined_q_md.append(f"[Macrotag: {macro}]")
                combined_q_md.append(f"[Microtag: {micro}]")
                combined_q_md.append("")
                q_counter += 1
            combined_q_md.append("")

# 2. Output SUBJECT: GOVERNANCE
combined_q_md.append("## Subject: GOVERNANCE")
combined_q_md.append("")

gov_grouped = {}
for q in governance_questions:
    sec = q["section"]
    top = q["topic"]
    mt = q["microtheme"]
    if sec not in gov_grouped:
        gov_grouped[sec] = {}
    if top not in gov_grouped[sec]:
        gov_grouped[sec][top] = {}
    if mt not in gov_grouped[sec][top]:
        gov_grouped[sec][top][mt] = []
    gov_grouped[sec][top][mt].append(q)

for sec in governance_sections_order:
    if sec not in gov_grouped:
        continue
    combined_q_md.append(f"### Section Group: {sec}")
    combined_q_md.append("")
    for top in hierarchy_tree["GOVERNANCE"].get(sec, {}):
        if top not in gov_grouped[sec]:
            continue
        combined_q_md.append(f"#### Microtopic: {top}")
        combined_q_md.append("")
        for mt in sorted(hierarchy_tree["GOVERNANCE"][sec][top]):
            if mt not in gov_grouped[sec][top]:
                continue
            combined_q_md.append(f"##### Subtopic: {mt}")
            combined_q_md.append("")
            sorted_qs = sorted(gov_grouped[sec][top][mt], key=lambda x: x["year"], reverse=True)
            for q in sorted_qs:
                text = q["question"]
                yr = q["year"]
                macro, micro = determine_tags_and_directives(text)
                combined_q_md.append(f"Q{q_counter}. {text}")
                combined_q_md.append(f"[Year: {yr}] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 2]")
                combined_q_md.append(f"[Subject: GOVERNANCE]")
                combined_q_md.append(f"[Section Group: {sec}]")
                combined_q_md.append(f"[Microtopic: {top}]")
                combined_q_md.append(f"[Subtopic: {mt}]")
                combined_q_md.append(f"[Macrotag: {macro}]")
                combined_q_md.append(f"[Microtag: {micro}]")
                combined_q_md.append("")
                q_counter += 1
            combined_q_md.append("")

# 3. Output SUBJECT: SOCIAL JUSTICE
combined_q_md.append("## Subject: SOCIAL JUSTICE")
combined_q_md.append("")

sj_grouped = {}
for q in social_justice_questions:
    sec = q["section"]
    top = q["topic"]
    mt = q["microtheme"]
    if sec not in sj_grouped:
        sj_grouped[sec] = {}
    if top not in sj_grouped[sec]:
        sj_grouped[sec][top] = {}
    if mt not in sj_grouped[sec][top]:
        sj_grouped[sec][top][mt] = []
    sj_grouped[sec][top][mt].append(q)

for sec in social_justice_sections_order:
    if sec not in sj_grouped:
        continue
    combined_q_md.append(f"### Section Group: {sec}")
    combined_q_md.append("")
    for top in hierarchy_tree["SOCIAL_JUSTICE"].get(sec, {}):
        if top not in sj_grouped[sec]:
            continue
        combined_q_md.append(f"#### Microtopic: {top}")
        combined_q_md.append("")
        for mt in sorted(hierarchy_tree["SOCIAL_JUSTICE"][sec][top]):
            if mt not in sj_grouped[sec][top]:
                continue
            combined_q_md.append(f"##### Subtopic: {mt}")
            combined_q_md.append("")
            sorted_qs = sorted(sj_grouped[sec][top][mt], key=lambda x: x["year"], reverse=True)
            for q in sorted_qs:
                text = q["question"]
                yr = q["year"]
                macro, micro = determine_tags_and_directives(text)
                combined_q_md.append(f"Q{q_counter}. {text}")
                combined_q_md.append(f"[Year: {yr}] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 2]")
                combined_q_md.append(f"[Subject: SOCIAL JUSTICE]")
                combined_q_md.append(f"[Section Group: {sec}]")
                combined_q_md.append(f"[Microtopic: {top}]")
                combined_q_md.append(f"[Subtopic: {mt}]")
                combined_q_md.append(f"[Macrotag: {macro}]")
                combined_q_md.append(f"[Microtag: {micro}]")
                combined_q_md.append("")
                q_counter += 1
            combined_q_md.append("")

# 4. Output SUBJECT: INTERNATIONAL RELATIONS
combined_q_md.append("## Subject: INTERNATIONAL RELATIONS")
combined_q_md.append("")

ir_grouped = {}
for q in international_relations_questions:
    sec = q["section"]
    top = q["topic"]
    mt = q["microtheme"]
    if sec not in ir_grouped:
        ir_grouped[sec] = {}
    if top not in ir_grouped[sec]:
        ir_grouped[sec][top] = {}
    if mt not in ir_grouped[sec][top]:
        ir_grouped[sec][top][mt] = []
    ir_grouped[sec][top][mt].append(q)

for sec in international_relations_sections_order:
    if sec not in ir_grouped:
        continue
    combined_q_md.append(f"### Section Group: {sec}")
    combined_q_md.append("")
    for top in hierarchy_tree["INTERNATIONAL_RELATIONS"].get(sec, {}):
        if top not in ir_grouped[sec]:
            continue
        combined_q_md.append(f"#### Microtopic: {top}")
        combined_q_md.append("")
        for mt in sorted(hierarchy_tree["INTERNATIONAL_RELATIONS"][sec][top]):
            if mt not in ir_grouped[sec][top]:
                continue
            combined_q_md.append(f"##### Subtopic: {mt}")
            combined_q_md.append("")
            sorted_qs = sorted(ir_grouped[sec][top][mt], key=lambda x: x["year"], reverse=True)
            for q in sorted_qs:
                text = q["question"]
                yr = q["year"]
                macro, micro = determine_tags_and_directives(text)
                combined_q_md.append(f"Q{q_counter}. {text}")
                combined_q_md.append(f"[Year: {yr}] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 2]")
                combined_q_md.append(f"[Subject: INTERNATIONAL RELATIONS]")
                combined_q_md.append(f"[Section Group: {sec}]")
                combined_q_md.append(f"[Microtopic: {top}]")
                combined_q_md.append(f"[Subtopic: {mt}]")
                combined_q_md.append(f"[Macrotag: {macro}]")
                combined_q_md.append(f"[Microtag: {micro}]")
                combined_q_md.append("")
                q_counter += 1
            combined_q_md.append("")

combined_q_md_content = "\n".join(combined_q_md).strip() + "\n"

# Write combined questions formatted files
with open(os.path.join(out_dir, "GS2_Syllabus_Questions_Formatted.md"), "w", encoding="utf-8") as f:
    f.write(combined_q_md_content)
with open(os.path.join(artifact_dir, "GS2_Syllabus_Questions_Formatted.md"), "w", encoding="utf-8") as f:
    f.write(combined_q_md_content)
print("Saved GS2_Syllabus_Questions_Formatted.md")

# ==================== CLEAN UP OLD SEPARATED FILES ====================
old_files = [
    "GS2_Polity_Syllabus_Taxonomy_Hierarchy.md",
    "GS2_Polity_Syllabus_Questions_Formatted.md",
    "GS2_Governance_Syllabus_Taxonomy_Hierarchy.md",
    "GS2_Governance_Syllabus_Questions_Formatted.md"
]

for filename in old_files:
    # Delete from workspace
    p_dest = os.path.join(out_dir, filename)
    if os.path.exists(p_dest):
        os.remove(p_dest)
        print(f"Deleted workspace old file: {filename}")
        
    # Delete from artifact dir
    p_art = os.path.join(artifact_dir, filename)
    if os.path.exists(p_art):
        os.remove(p_art)
        print(f"Deleted artifact old file: {filename}")

print("ALL CONSOLIDATION TASKS COMPLETED SUCCESSFULLY!")
