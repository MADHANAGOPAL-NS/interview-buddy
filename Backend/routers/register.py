from fastapi import APIRouter, Form, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from .resume import extract_text, parse_resume
from DB.db_connection import store_resume, get_resume_by_id  # ✅ Import MongoDB helpers

router = APIRouter()

@router.post("/register")
async def register_user(
    name: str = Form(...),
    resume_file: UploadFile = File(...)
):
    file_bytes = await resume_file.read()
    resume_text = extract_text(file_bytes, resume_file.filename)
    parsed_data = parse_resume(resume_text)

    parsed_data["name"] = name
    parsed_data["resume_filename"] = resume_file.filename

    resume_id = store_resume(parsed_data)  # ✅ Store in MongoDB

    if "_id" in parsed_data:
        parsed_data["_id"] = str(parsed_data["_id"])

    return JSONResponse(content=jsonable_encoder({
        "message": "Registration successful",
        "resume_id": str(resume_id),
        "parsed_resume": parsed_data
    }))

@router.get("/parsed_resume/{resume_id}")
def get_parsed_resume(resume_id: str):
    resume = get_resume_by_id(resume_id)  # ✅ Retrieve from MongoDB
    if not resume:
        return JSONResponse(content={"error": "Resume not found"}, status_code=404)

    if "_id" in resume:
        resume["_id"] = str(resume["_id"])

    return JSONResponse(content=jsonable_encoder(resume))
