from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from .resume import extract_text, parse_resume

router = APIRouter()

# Temporary in-memory store (for testing without DB)
parsed_resume_data = {}

@router.post("/register")
async def register_user(
    name: str = Form(...),
    resume_file: UploadFile = File(...)
):
    file_bytes = await resume_file.read()
    resume_text = extract_text(file_bytes, resume_file.filename)
    parsed_data = parse_resume(resume_text)

    parsed_data["name"] = name

    parsed_resume_data["parsed_resume"] = parsed_data
    parsed_resume_data["resume_filename"] = resume_file.filename

    return JSONResponse(content={
        "message": "Registration successful",
        "parsed_resume": parsed_data,
        "resume_filename": resume_file.filename
    })

@router.get("/parsed_resume")
def get_parsed_resume():
    if not parsed_resume_data:
        return JSONResponse(content={"error": "No resume data found"}, status_code=404)
    
    return JSONResponse(content=parsed_resume_data["parsed_resume"])