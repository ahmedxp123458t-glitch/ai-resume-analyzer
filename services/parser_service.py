import io
import re
from PyPDF2 import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        text_parts = []
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
        return "\n".join(text_parts)
    except Exception as e:
        raise ValueError(f"Failed to parse PDF: {str(e)}")


def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,;:!?()\-@/#]', '', text)
    return text.strip()


def extract_sections(text: str) -> dict:
    sections = {
        "contact": "",
        "summary": "",
        "experience": "",
        "education": "",
        "skills": "",
        "projects": "",
        "certifications": "",
    }

    section_patterns = {
        "contact": r"(?i)(contact|personal\s*info)",
        "summary": r"(?i)(summary|profile|objective|about\s*me)",
        "experience": r"(?i)(experience|work\s*history|employment|professional\s*experience)",
        "education": r"(?i)(education|academic|qualifications|degrees)",
        "skills": r"(?i)(skills|technical\s*skills|competencies|expertise)",
        "projects": r"(?i)(projects|project\s*experience)",
        "certifications": r"(?i)(certifications|certificates|licenses)",
    }

    lines = text.split("\n")
    current_section = "other"
    section_texts = {k: [] for k in sections}
    section_texts["other"] = []

    for line in lines:
        line_stripped = line.strip()
        found = False
        for sec_name, pattern in section_patterns.items():
            if re.match(pattern, line_stripped):
                current_section = sec_name
                found = True
                break
        if not found:
            section_texts[current_section].append(line_stripped)

    for sec_name in sections:
        sections[sec_name] = "\n".join(
            [l for l in section_texts[sec_name] if l]
        )

    return sections


def extract_emails(text: str) -> list:
    return re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text)


def extract_phones(text: str) -> list:
    pattern = r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}'
    return re.findall(pattern, text)


def extract_names(text: str) -> list:
    lines = text.strip().split("\n")
    if lines:
        first_line = lines[0].strip()
        if first_line and len(first_line.split()) <= 4:
            return [first_line]
    return []
