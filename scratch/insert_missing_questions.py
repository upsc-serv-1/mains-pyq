import re
import os

path = r"C:\Users\Dr. Yogesh\Desktop\mains\neet and upsc cms\upsc\syllabus hierarchy\gs3\GS3_Syllabus_Questions_Formatted.md"
backup_path = path + ".bak"

# 1. Read file
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# Make backup
with open(backup_path, "w", encoding="utf-8") as f:
    f.write(content)
print(f"Created backup at {backup_path}")

# 2. Define target replacements (metadata lines we append our new questions to)
targets = {
    "fdi": (
        "[Year: 2013] [Marks: 5] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: INDIAN ECONOMY] [Section Group: Industrial Dynamics & Reforms] [Microtopic: Effects of Liberalisation on the economy; Changes in Industrial policy & their effects on industrial growth] [Subtopic: FDI] [Macrotag: Analytical] [Microtag: Discuss]",
        "\n\nQNEW. Though India allowed foreign direct investment (FDI) in what is called multibrand retail through joint venture route in September 2012, the FDI even after a year, has not picked up. Discuss the reasons.\n\n[Year: 2013] [Marks: 5] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: INDIAN ECONOMY] [Section Group: Industrial Dynamics & Reforms] [Microtopic: Effects of Liberalisation on the economy; Changes in Industrial policy & their effects on industrial growth] [Subtopic: FDI] [Macrotag: Analytical] [Microtag: Discuss]"
    ),
    "ppp": (
        "[Year: 2014] [Marks: 12.5] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: INDIAN ECONOMY] [Section Group: Physical Infrastructure & Capital] [Microtopic: Capital investment models and public-private frameworks] [Subtopic: PPP X Infrastructure] [Macrotag: Descriptive] [Microtag: Explain, What, How]",
        "\n\nQNEW. Adaptation of the PPP model for infrastructure development of the country has not been free from criticism. Critically discuss the pros and cons of the model.\n\n[Year: 2013] [Marks: 10] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: INDIAN ECONOMY] [Section Group: Physical Infrastructure & Capital] [Microtopic: Capital investment models and public-private frameworks] [Subtopic: PPP X Infrastructure] [Macrotag: Analytical] [Microtag: Critically discuss, Pros, Cons]"
    ),
    "msp": (
        "[Year: 2022] [Marks: 15] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: AGRICULTURE] [Section Group: Agriculture & Farm Dynamics] [Microtopic: Issues related to direct and indirect farm subsidies and minimum support prices (MSP)] [Subtopic: Agriculture Subsidy] [Macrotag: Descriptive, Analytical, Applied] [Microtag: Explain, How, Do you think, Justify, India]",
        "\n\nQNEW. What do you mean by Minimum Support Price (MSP)? How will MSP rescue the farmers from the low-income trap?\n\n[Year: 2018] [Marks: 10] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: AGRICULTURE] [Section Group: Agriculture & Farm Dynamics] [Microtopic: Issues related to direct and indirect farm subsidies and minimum support prices (MSP)] [Subtopic: Agriculture Subsidy] [Macrotag: Descriptive, Analytical] [Microtag: What, How]"
    ),
    "health": (
        "[Year: 2022] [Marks: 15] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: SCIENCE & TECHNOLOGY] [Section Group: Everyday Science & Innovations] [Microtopic: Science and Technology- applications in health, industry, and crisis management] [Subtopic: Medical and Health Technologies] [Macrotag: Descriptive, Applied] [Microtag: What is, How, Covid, India, Indian]",
        "\n\nQNEW. The increase in life expectancy in the country has led to newer health challenges in the community. What are those challenges and what steps need to be taken to meet them?\n\n[Year: 2022] [Marks: 10] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: SCIENCE & TECHNOLOGY] [Section Group: Everyday Science & Innovations] [Microtopic: Science and Technology- applications in health, industry, and crisis management] [Subtopic: Medical and Health Technologies] [Macrotag: Descriptive, Applied] [Microtag: What]"
    ),
    "biotech": (
        "##### Subtopic: Bio-Technology",
        "##### Subtopic: Bio-Technology\n\nQNEW. How can India achieve energy independence through clean technology by 2047? How can biotechnology play a crucial role in this endeavour?\n\n[Year: 2025] [Marks: 10] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: SCIENCE & TECHNOLOGY] [Section Group: Frontier Technologies & IPR] [Microtopic: Awareness in the fields of nano-technology, bio-technology and issues relating to intellectual property rights] [Subtopic: Bio-Technology] [Macrotag: Descriptive, Analytical, Applied] [Microtag: How, India]"
    )
}

# Perform replacements
for key, (target_str, append_str) in targets.items():
    if target_str in content:
        content = content.replace(target_str, target_str + append_str)
        print(f"Successfully inserted question for {key}")
    else:
        print(f"Error: Target not found for {key}!")

# 3. Renumber all Q\d+\. and QNEW\. sequentially
# We can find all matches of Q\d+\. or QNEW\. and replace them in order
# Let's do this by splitting the content by Q\d+\. or QNEW\. and then rebuilding
parts = re.split(r'\r?\n(?=Q\d+\.|QNEW\.)', content)
print(f"Total parts split: {len(parts)}")

new_parts = []
q_counter = 1

for part in parts:
    part_strip = part.strip()
    if part_strip.startswith("Q"):
        # Replace the first Q\d+\. or QNEW\. in this part with Q{q_counter}.
        # Wait, the part starts with either Q\d+. or QNEW.
        updated_part = re.sub(r'^(?:Q\d+|QNEW)\.', f"Q{q_counter}.", part)
        new_parts.append(updated_part)
        q_counter += 1
    else:
        new_parts.append(part)

final_content = "\n".join(new_parts)

# Verify count
print(f"Renumbered {q_counter - 1} questions.")

# 4. Save updated file
with open(path, "w", encoding="utf-8") as f:
    f.write(final_content)
print(f"Saved updated file to {path}")
