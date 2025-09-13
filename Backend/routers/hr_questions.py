from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from DB.db_connection import get_resume_by_id
import requests
import time
import traceback

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "mistral"
MAX_RETRIES = 2
RETRY_DELAY = 1.5  # seconds

# -------------------------------
# Route 1: Generate HR Questions
# -------------------------------
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

    # ✅ Updated prompt for fresher-level candidates
    prompt = (
        "You are an HR interviewer preparing questions for a fresher candidate "
        "who is joining a company in an entry-level role. Based on the following personal skills: "
        f"{', '.join(personal_skills)}, generate 5 realistic HR interview questions. "
        "Use simple, beginner-friendly language. Avoid abstract or philosophical phrasing. "
        "Each question should clearly relate to one of the listed skills and be suitable for someone "
        "with little or no prior work experience."
    )

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        raw_output = response.json().get("response", "")

        questions = [
            q.strip("-• ").strip()
            for q in raw_output.split("\n")
            if q.strip()
        ][:5]

        return JSONResponse(content={"questions": questions})
    except Exception as e:
        print("Error during HR question generation:", traceback.format_exc())
        return JSONResponse(
            content={"error": f"Ollama request failed: {str(e)}"},
            status_code=500
        )

# -------------------------------
# Route 2: Evaluate HR Answer
# -------------------------------
class FeedbackRequest(BaseModel):
    question: str
    answer: str

@router.post("/hr_questions/feedback")
def evaluate_answer(payload: FeedbackRequest):
    prompt = (
        f"Evaluate the following answer to the HR question below.\n\n"
        f"Question: \"{payload.question}\"\n"
        f"Answer: \"{payload.answer}\"\n\n"
        "First, say whether the answer is strong and relevant for a fresher candidate. "
        "Then, suggest one or two concrete improvements—better phrasing, missing points, or keywords to include. "
        "Keep it concise and beginner-friendly."
    )

    for attempt in range(MAX_RETRIES + 1):
        try:
            response = requests.post(
                OLLAMA_URL,
                json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
                timeout=60
            )
            response.raise_for_status()
            feedback = response.json().get("response", "").strip()

            if feedback:
                return JSONResponse(content={"feedback": feedback})
        except Exception as e:
            print("Error during HR answer evaluation:", traceback.format_exc())
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
            else:
                return JSONResponse(
                    content={"feedback": "LLM evaluation failed. Please try again later."},
                    status_code=500
                )
