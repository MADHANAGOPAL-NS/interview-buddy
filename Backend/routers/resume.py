import pdfplumber
import docx
import re
import io
#import spacy

#lp = spacy.load("en_core_web_sm")

def extract_text(file_bytes: bytes, filename: str) -> str:
    
    ext = filename.lower().split('.')[-1]

    if ext == "pdf":
        return extract_text_from_pdf(file_bytes)
    elif ext == "docx":
        return extract_text_from_docx(file_bytes)
    else:
        raise ValueError(f"Unsupported file type: {ext}")

def extract_text_from_pdf(file_bytes: bytes) -> str:
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        return "\n".join(
            page.extract_text() for page in pdf.pages if page.extract_text()
        )

def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join([para.text for para in doc.paragraphs])

def parse_resume(text: str) -> dict:

    technical_skills = re.findall(
        r"\b(Python|FastAPI|HTML|CSS|JavaScript|SQL|DSA|Web Development|Machine Learning)\b", text
    )
    personal_skills = re.findall(
        r"\b(communication|leadership|teamwork|adaptability|problem-solving|creativity|time management|empathy|critical thinking|collaboration)\b",
        text,
        flags=re.IGNORECASE
    )


    return {
        
        "technical_skills": list(set(technical_skills)),
        "personal_skills": list(set([skill.lower() for skill in personal_skills]))

    }