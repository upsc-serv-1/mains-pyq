import fitz

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
    
    # Extract horizontal lines
    drawings = page.get_drawings()
    y_lines = []
    for d in drawings:
        rect = d["rect"]
        if rect.y1 - rect.y0 < 2:
            y_lines.append(rect.y0)
            
    # Deduplicate and sort
    y_lines = sorted(list(set(round(y, 1) for y in y_lines)))
    
    # Filter for table area lines
    table_lines = [y for y in y_lines if y > 165]
    
    print(f"Table lines on page 1: {table_lines}")
    
    # Generate intervals
    intervals = []
    for i in range(len(table_lines) - 1):
        intervals.append({
            "start_y": table_lines[i],
            "end_y": table_lines[i+1],
            "words": {
                "qn_no": [],
                "year": [],
                "question": [],
                "topic": [],
                "marks": []
            }
        })
        
    # Distribute words
    words = page.get_text("words")
    for w in words:
        x0, y0, x1, y1, text = w[0], w[1], w[2], w[3], w[4].replace('\u200b', '')
        col = get_column(x0)
        if not col:
            continue
            
        for inv in intervals:
            if inv["start_y"] <= y0 < inv["end_y"]:
                inv["words"][col].append(w)
                break
                
    # Reconstruct rows
    for inv in intervals:
        year_w = sorted(inv["words"]["year"], key=lambda x: (x[1], x[0]))
        year_str = " ".join(w[4].replace('\u200b', '') for w in year_w).strip()
        
        qn_w = sorted(inv["words"]["qn_no"], key=lambda x: (x[1], x[0]))
        qn_str = " ".join(w[4].replace('\u200b', '') for w in qn_w).strip()
        
        q_w = sorted(inv["words"]["question"], key=lambda x: (x[1], x[0]))
        q_str = " ".join(w[4].replace('\u200b', '') for w in q_w).strip()
        
        topic_w = sorted(inv["words"]["topic"], key=lambda x: (x[1], x[0]))
        topic_str = " ".join(w[4].replace('\u200b', '') for w in topic_w).strip()
        
        marks_w = sorted(inv["words"]["marks"], key=lambda x: (x[1], x[0]))
        marks_str = " ".join(w[4].replace('\u200b', '') for w in marks_w).strip()
        
        # Skip header row
        if qn_str.lower() == "qn no." or qn_str.lower() == "qn.no":
            continue
            
        print(f"Row Q{qn_str} ({year_str}) | Marks: {marks_str} | Topic: {topic_str}")
        print(f"  QText: {q_str}")
        print("-" * 60)

if __name__ == "__main__":
    test_parse()
