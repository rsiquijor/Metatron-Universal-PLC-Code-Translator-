import os
import secrets
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from .translator import translate, TranslationError

app = FastAPI(title="Metatron Cube PLC Translator", version="0.1.0", docs_url=None, redoc_url=None)
API_KEY = os.getenv("METATRON_API_KEY", "")
class Job(BaseModel):
    source: str = Field(min_length=1, max_length=20000)
    target_language: str = "st"
    target_platform: str = "generic"
@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = "no-store"
    response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'; style-src 'self'; base-uri 'none'; frame-ancestors 'none'"
    return response
@app.get("/healthz")
def health():
    return {"status": "ok"}
@app.post("/api/translate")
def api_translate(job: Job, x_api_key: str | None = Header(default=None)):
    if not API_KEY or not x_api_key or not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(401, "Valid API key required")
    try:
        return translate(job.source, job.target_language, job.target_platform)
    except TranslationError as e:
        raise HTTPException(422, str(e))
app.mount("/", StaticFiles(directory=str(Path(__file__).parent / "static"), html=True), name="static")
