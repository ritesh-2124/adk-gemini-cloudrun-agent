from fastapi import FastAPI
from pydantic import BaseModel
from .agent import run_agent

app = FastAPI()


class Request(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "ADK Gemini Agent running"}


@app.post("/summarize")
async def summarize(req: Request):
    summary = run_agent(req.text)
    return {"summary": summary}