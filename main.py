import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.infrastructure.logger
from app.domain.analysis.routes import router as AnalysisRouter
from app.infrastructure.database import engine

load_dotenv()

app = FastAPI()

app.include_router(AnalysisRouter)

# allow cors
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message":"Hello world"}

@app.get("/env_test")
def get_env():
    return {"DB_HOST": os.getenv('DB_HOST'), "DB_NAME": os.getenv('DB_NAME')}

@app.get("/db_test")
def db_test():
    engine.connect()
    return {"message":"db_test ok"}

@app.get("/seeds")
def seeder():
    import seeder
    return {"message":"seeds ok"}
