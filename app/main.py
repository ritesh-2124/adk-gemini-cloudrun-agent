from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import run_agent

app = FastAPI(
    title="ADK Summarizer Agent",
    description="AI-powered text summarization agent built with Google ADK and Gemini",
    version="1.0.0",
)

# CORS — allow all origins for demo; restrict in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummarizeRequest(BaseModel):
    text: str


@app.get("/")
def home():
    return {"message": "ADK Summarizer Agent is running", "status": "healthy"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/summarize")
async def summarize(req: SummarizeRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text field cannot be empty")
    try:
        summary = await run_agent(req.text)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")