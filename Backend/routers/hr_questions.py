from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from DB.db_connection import get_resume_by_id
import requests

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"

@router.get("/hr_questions/start")
def generate_hr_questions(request: Request):
    resume_id = request.query_params.get("resume_id")
    if not resume_id:
        return JSONResponse(content={"error": "Missing resume_id"}, status_code=400)

    resume = get_resume_by_id(resume_id)
    if not resume:
        return JSONResponse(content={"error": "Resume not found"}, status_code=404)

    personal_skills = resume.get("personal_skills", [])
    if not personal_skills:
        return JSONResponse(content={"error": "No personal skills found"}, status_code=400)

    # Medium-level prompt for realistic, skill-reflective questions
    prompt = (
        f"Generate 5 realistic HR interview questions that reflect the following personal skills: "
        f"{', '.join(personal_skills)}. "
        f"Use simple language and avoid abstract or philosophical phrasing. "        
        f"Avoid excessive jargon, but ensure each question clearly relates to one of the listed skills."
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_output = response.json()["response"]

        questions = [q.strip("-• ").strip() for q in raw_output.split("\n") if q.strip()]
        questions = questions[:5] if len(questions) > 5 else questions

        return JSONResponse(content={"questions": questions})
    except Exception as e:
        return JSONResponse(content={"error": f"Ollama request failed: {str(e)}"}, status_code=500)
