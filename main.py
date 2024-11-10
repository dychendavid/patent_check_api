from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import app.infrastructure.logger
from app.domain.analysis.routes import router as AnalysisRouter


app = FastAPI()

app.include_router(AnalysisRouter)

# allow cors
origins = [
    "http://localhost",

    # frontend
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}
