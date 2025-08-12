from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.register import router as register_router
app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins = ['*'], allow_credentials = True , allow_methods = ['*'] , allow_headers = ['*'])

app.include_router(register_router , prefix = "/api")
