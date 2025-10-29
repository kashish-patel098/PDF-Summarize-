"""PDF ingestion: extract sections using pdfplumber with simple heuristics.
Produces a list of sections: {title, text, page}
"""
import pdfplumber
import re

def is_heading_line(line: str) -> bool:
    if not line: return False
    # heuristics: short line, Title Case or ALL CAPS, numeric prefix
    words = line.strip()
    if len(words.split()) <= 6:
        if re.match(r'^\d+\.?\s+', words):
            return True
        # ALL CAPS
        if words.upper() == words and sum(c.isalpha() for c in words) > 0:
            return True
        # Title case heuristic (most words capitalized)
        caps = sum(1 for w in words.split() if w[:1].isupper())
        if caps >= max(1, len(words.split()) // 2):
            return True
    return False


def extract_sections(pdf_path: str):
    sections = []
    with pdfplumber.open(pdf_path) as pdf:
        current = {"title": "Introduction", "text": "", "page": 0}
        for i, page in enumerate(pdf.pages, start=1):
            text = page.extract_text() or ""
            lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
            for line in lines:
                if is_heading_line(line):
                    # start new section
                    if current["text"].strip():
                        sections.append(current)
                    current = {"title": line.strip(), "text": "", "page": i}
                else:
                    current["text"] += " " + line
        if current["text"].strip():
            sections.append(current)
    return sections
