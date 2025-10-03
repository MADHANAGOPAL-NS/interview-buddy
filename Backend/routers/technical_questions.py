from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from DB.db_connection import get_resume_by_id
import requests

router = APIRouter()

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "codellama"

@router.get("/technical_questions/start")
def generate_hr_questions(request: Request):
    resume_id = request.query_params.get("resume_id")
    if not resume_id:
        return JSONResponse(content={"error": "Missing resume_id"}, status_code=400)

    resume = get_resume_by_id(resume_id)
    if not resume:
        return JSONResponse(content={"error": "Resume not found"}, status_code=404)

    technical_skills = resume.get("technical_skills", [])
    if not technical_skills:
        return JSONResponse(content={"error": "No technical skills found"}, status_code=400)

    # Medium-level prompt for realistic, skill-reflective questions
    prompt = (
    f"Generate 5 direct and knowledge-based technical interview questions that test the following skills: "
    f"{', '.join(technical_skills)}. "
    f"Ask clear, precise, and technical questions that check the candidate's understanding of key concepts. "
    f"Do not include coding challenges, scenarios, or long problem statements. "
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

@router.post("/technical_questions/score")
async def evaluate_answer(request: Request):
    body = await request.json()
    question = body.get("question")
    answer = body.get("answer")

    if not question or not answer:
        return JSONResponse(content={"error": "Missing question or answer"}, status_code=400)

    # Ask LLM to check correctness only
    prompt = (
        f"Question: {question}\n"
        f"Candidate's Answer: {answer}\n\n"
        f"Determine if the answer is correct or incorrect,even if keywords are not used "
        f"but the meaning is conveyed. Respond strictly in JSON format with fields:\n"
        f"{{\"correct\": true/false, \"feedback\": \"1-2 sentences max  explanation\"}}"
    )

    payload = {"model": MODEL_NAME, "prompt": prompt, "stream": False}

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        raw_output = response.json()["response"].strip()

        import json,re
        try:
            result = json.loads(raw_output)
        except Exception:
            # fallback: try to extract {...} part
            import re
            match = re.search(r"\{.*\}", raw_output, re.DOTALL)
            if match:
                result = json.loads(match.group(0))
            else:
                result = {"correct": False, "feedback": raw_output.strip()[:200]}
            
            
        # Add user's answer into feedback result
        result["user_answer"] = answer

        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(content={"error": f"Ollama request failed: {str(e)}"}, status_code=500)

