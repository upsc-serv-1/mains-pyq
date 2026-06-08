import pdfplumber
import json
import re

pdf_path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\Civilsdaily GS Mains Microthemes_2025 Edition.pdf"

# Normalizer for GS2 microthemes
def normalize_microtheme(mt):
    if not mt:
        return ""
    mt_clean = mt.replace("\n", " ").replace("\x07", "").strip()
    # Replace multiple spaces
    mt_clean = re.sub(r'\s+', ' ', mt_clean)
    
    # Specific normalization matches
    mt_lower = mt_clean.lower()
    if "disqualification" in mt_lower:
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

# Subject mapping
# 1-9: Polity, 10-11: Governance, 12-14: Social Justice, 15-16: Governance, 17-20: International Relations
# We will define a function or dictionary to map page default subjects:
page_default_subjects = {
    26: "Polity",
    27: "Polity",
    28: "Polity",
    29: "Polity",
    30: "Polity",
    31: "Polity",
    32: "Polity",
    33: "Polity",
    34: "Polity",
    35: "Polity", # Constitutional Bodies, Enforcement Agencies, Quasi Judicial (Topic 9 is Polity)
    36: "Polity", # Sectoral Regulatory, Statutory (Topic 9 is Polity)
    37: "Governance", # Topic 10
    38: "Governance", # Topic 11
    39: "Governance", # Topic 15
    40: "Governance", # Topic 15/16
    41: "Social Justice", # Topic 12
    42: "Social Justice", # Topic 13
    43: "Social Justice", # Topic 14/16 (Civil services or poverty/hunger)
    44: "International Relations", # Topic 17
    45: "International Relations", # Topic 18
    46: "International Relations", # Topic 18
    47: "International Relations", # Topic 19
    48: "International Relations"  # Topic 20
}

# Verbatim GS2 topics from page 23
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

# Function to map microtheme and page to correct Topic Number (1 to 20)
def map_to_topic_num(page, mt, question_text):
    mt_lower = mt.lower()
    q_lower = question_text.lower()
    
    # Page 26
    if page == 26:
        return 1
    # Page 27
    if page == 27:
        return 1
    # Page 28
    if page == 28:
        # Devolution/local government (Panchayati Raj, Municipalities) are Topic 4
        if any(w in q_lower for w in ["local body", "panchayat", "local government", "municipal", "devolution", "urban local", "grassroot"]):
            return 4
        return 2
    # Page 29
    if page == 29:
        return 3
    # Page 30
    if page == 30:
        return 5
    # Page 31
    if page == 31:
        return 6
    # Page 32: Alternate Dispute Resolution, Informal associations, Judiciary
    if page == 32:
        if "dispute" in mt_lower or "resolution" in mt_lower:
            return 3
        if "informal" in mt_lower:
            return 7
        if "judiciary" in mt_lower:
            return 7
    # Page 33: Pressure Groups (Topic 7), Tribunal (Topic 9 - Quasi-judicial), Union Executive (Topic 7)
    if page == 33:
        if "tribunal" in mt_lower:
            return 9
        return 7
    # Page 34: Election Dispute (Topic 8), Electoral reforms (Topic 8), MCC (Topic 8), Political Parties (Topic 7 or 8)
    if page == 34:
        return 8
    # Page 35: Constitutional Bodies (Topic 9), Quasi judicial (Topic 9), Enforcement Agencies (Topic 7 or 9)
    if page == 35:
        if "enforcement" in mt_lower:
            return 7
        return 9
    # Page 36: Sectoral Regulatory (Topic 9), Statutory (Topic 9)
    if page == 36:
        return 9
    # Page 37: Government Schemes and Policies (Topic 10), Structural reforms (Topic 10)
    if page == 37:
        return 10
    # Page 38: Civil Society, Donor Agencies, SHGs (Topic 11)
    if page == 38:
        return 11
    # Page 39: Citizens Charter, Transparency (Topic 15)
    if page == 39:
        return 15
    # Page 40: E-governance (Topic 15)
    if page == 40:
        return 15
    # Page 41: Children, Disables, Efficacy of welfare (Topic 12)
    if page == 41:
        return 12
    # Page 42: Education, Health (Topic 13)
    if page == 42:
        return 13
    # Page 43: Hunger, Poverty, Miscellenous
    if page == 43:
        # Hunger/Poverty are Topic 14. Let's see what is in Miscellenous.
        # Often Topic 16 (Civil services in democracy) or Topic 13 (Human resources).
        # We will check question text for civil services
        if "civil services" in q_lower or "civil servant" in q_lower or "bureaucra" in q_lower:
            return 16
        if "human resource" in q_lower:
            return 13
        return 14
    # Page 44: Neighbourhood (Topic 17)
    if page == 44:
        return 17
    # Page 45: Bilateral Relations (Topic 18)
    if page == 45:
        return 18
    # Page 46: Groupings (Topic 18)
    if page == 46:
        return 18
    # Page 47: Energy, Geo-politics, Diaspora, Miscelleneous
    if page == 47:
        if "diaspora" in mt_lower:
            return 19
        return 19
    # Page 48: Funding Agencies, UN, WTO (Topic 20)
    if page == 48:
        return 20
        
    return 1 # Fallback

questions = []
current_microtheme = ""

with pdfplumber.open(pdf_path) as pdf:
    for page_num in range(26, 49): # Pages 26 to 48
        page = pdf.pages[page_num - 1]
        table = page.extract_table()
        if not table:
            continue
        
        # Skip header row if it exists
        start_row = 0
        if table[0][0] == "Microthemes" or table[0][1] == "UPSC PYQs":
            start_row = 1
            
        for row in table[start_row:]:
            if len(row) < 4:
                continue
            
            mt = row[0]
            pyq = row[1]
            year = row[2]
            marks = row[3]
            
            # Skip empty rows or footer noise
            if not pyq or pyq.strip() == "" or pyq.strip() == "UPSC PYQs":
                continue
            
            # Clean elements
            pyq_clean = pyq.replace("\n", " ").replace("\x07", "").strip()
            year_clean = year.strip() if year else ""
            marks_clean = marks.strip() if marks else ""
            
            # Keep track of microtheme
            if mt and mt.strip():
                current_microtheme = normalize_microtheme(mt)
            
            # Resolve Subject and Topic
            topic_num = map_to_topic_num(page_num, current_microtheme, pyq_clean)
            topic = gs2_topics[topic_num]
            
            # For Topic 16 (Civil Services), subject should be Governance, not Social Justice
            if topic_num in [10, 11, 15, 16]:
                subject = "Governance"
            elif topic_num in [12, 13, 14]:
                subject = "Social Justice"
            elif topic_num in [17, 18, 19, 20]:
                subject = "International Relations"
            else:
                subject = "Polity"
            
            questions.append({
                "page": page_num,
                "subject": subject,
                "topic": topic,
                "microtheme": current_microtheme,
                "question": pyq_clean,
                "year": year_clean,
                "marks": marks_clean
            })

print(f"Extracted {len(questions)} GS-II questions.")

with open("gs2_questions.json", "w", encoding="utf-8") as f:
    json.dump(questions, f, indent=4)
print("Done writing to gs2_questions.json")
