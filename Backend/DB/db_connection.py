from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["interview_app"]
resume_collection = db["resumes"]

def store_resume(data: dict) -> str:
    data["created_at"] = datetime.utcnow()
    result = resume_collection.insert_one(data)
    return str(result.inserted_id)

def get_resume_by_id(resume_id: str) -> dict:
    resume = resume_collection.find_one({"_id": ObjectId(resume_id)})
    if resume:
        resume["_id"] = str(resume["_id"])
    return resume
