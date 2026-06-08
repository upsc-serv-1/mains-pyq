import fitz
import sys

def get_column(x0):
    if 20 < x0 < 58:
        return "qn_no"
    elif 58 <= x0 < 100:
        return "year"
    elif 100 <= x0 < 465:
        return "question"
    elif 465 <= x0 < 535:
        return "topic"
    elif 535 <= x0 < 600:
        return "marks"
    return None

def test_parse():
    path = r"C:\Users\Dr. Yogesh\Downloads\Telegram Desktop\GS 1 PYQs.pdf"
    doc = fitz.open(path)
    page = doc[0]
    words = page.get_text("words")
    
    # 1. Find all question numbers in this page
    page_qns = []
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4].replace('\u200b', '').strip()
        if 20 < x0 < 58 and text.isdigit():
            page_qns.append((int(text), y0, y1))
            
    # Deduplicate
    page_qns.sort(key=lambda x: x[1])
    unique_qns = []
    for q in page_qns:
        if not unique_qns or abs(q[1] - unique_qns[-1][1]) > 5:
            unique_qns.append(q)
            
    unique_qns.sort(key=lambda x: x[1])
    
    # Create intervals
    intervals = []
    for idx in range(len(unique_qns)):
        num, y0, y1 = unique_qns[idx]
        if idx == 0:
            start_y = 170
        else:
            start_y = (unique_qns[idx-1][1] + y0) / 2.0
            
        if idx == len(unique_qns) - 1:
            end_y = 900
        else:
            end_y = (y0 + unique_qns[idx+1][1]) / 2.0
            
        intervals.append({
            "qn_no": num,
            "start_y": start_y,
            "end_y": end_y,
            "words": {
                "qn_no": [],
                "year": [],
                "question": [],
                "topic": [],
                "marks": []
            }
        })
        
    # Distribute words
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4].replace('\u200b', '')
        if y0 < 170:
            continue
        col = get_column(x0)
        if not col:
            continue
            
        for inv in intervals:
            if inv["start_y"] <= y0 < inv["end_y"]:
                inv["words"][col].append(w)
                break
                
    # Reconstruct
    for inv in intervals:
        year_w = sorted(inv["words"]["year"], key=lambda x: (x[1], x[0]))
        year_str = " ".join(w[4].replace('\u200b', '') for w in year_w).strip()
        
        q_w = sorted(inv["words"]["question"], key=lambda x: (x[1], x[0]))
        q_str = " ".join(w[4].replace('\u200b', '') for w in q_w).strip()
        
        topic_w = sorted(inv["words"]["topic"], key=lambda x: (x[1], x[0]))
        topic_str = " ".join(w[4].replace('\u200b', '') for w in topic_w).strip()
        
        marks_w = sorted(inv["words"]["marks"], key=lambda x: (x[1], x[0]))
        marks_str = " ".join(w[4].replace('\u200b', '') for w in marks_w).strip()
        
        print(f"Q{inv['qn_no']} ({year_str}) | Marks: {marks_str} | Topic: {topic_str}")
        print(f"  QText: {q_str[:120]}...")
        print("-" * 50)

if __name__ == "__main__":
    test_parse()
