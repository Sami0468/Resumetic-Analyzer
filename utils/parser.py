import os
import re

def extract_text_from_pdf(filepath):
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                t = page.extract_text()
                if t:
                    text += t + "\n"
    except Exception as e:
        try:
            import PyPDF2
            with open(filepath, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e2:
            text = f"Error extracting PDF: {str(e2)}"
    return text.strip()

def extract_text_from_docx(filepath):
    try:
        from docx import Document
        doc = Document(filepath)
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        return f"Error extracting DOCX: {str(e)}"

def parse_resume(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(filepath)
    elif ext in ['.docx', '.doc']:
        return extract_text_from_docx(filepath)
    else:
        return "Unsupported file format"

def extract_name(text):
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    if lines:
        first = lines[0]
        if len(first.split()) <= 5 and not any(c.isdigit() for c in first):
            return first
    return "Candidate"

def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else ""

def extract_phone(text):
    pattern = r'(\+?\d[\d\s\-().]{7,}\d)'
    matches = re.findall(pattern, text)
    return matches[0].strip() if matches else ""