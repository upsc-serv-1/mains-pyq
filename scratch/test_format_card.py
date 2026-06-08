import re
import os
import sys

sys.path.append(os.getcwd())
from compile_master_gs3 import parse_institute_files, format_compiled_card

institute_data = parse_institute_files()

statement = "Q149. How can India achieve energy independence through clean technology by 2047? How can biotechnology play a crucial role in this endeavour?"
metadata = "[Year: 2025] [Marks: 10] [Group: UPSC CSE] [Exam: Mains] [Stage: Mains] [Paper: Mains - GS 3] [Subject: SCIENCE & TECHNOLOGY] [Section Group: Frontier Technologies & IPR] [Microtopic: Awareness in the fields of nano-technology, bio-technology and issues relating to intellectual property rights] [Subtopic: Bio-Technology] [Macrotag: Descriptive, Analytical, Applied] [Microtag: How, India]"

card = format_compiled_card(statement, metadata, institute_data)
print("="*60)
print(card)
print("="*60)
