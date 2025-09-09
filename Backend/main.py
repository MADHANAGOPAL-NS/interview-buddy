from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.register import router as register_router
from routers.hr_questions import router as hr_router
from routers.technical_questions import router as technical_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(register_router, prefix="/api")
app.include_router(hr_router , prefix = "/api")
app.include_router(technical_router , prefix = "/api")