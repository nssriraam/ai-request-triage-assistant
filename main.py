"""
AI Request Triage Assistant — Backend (FastAPI)
Exposes a single POST /triage endpoint that accepts raw client text
and returns structured JSON via the Fireworks AI API.
"""

import os
import json

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from openai import OpenAI

# ── Load environment variables ──────────────────────────────────────
load_dotenv()
API_KEY = os.getenv("FIREWORKS_API_KEY")
if not API_KEY:
    raise RuntimeError("FIREWORKS_API_KEY not found in .env file")

# ── Fireworks client (OpenAI-compatible) ────────────────────────────
client = OpenAI(
    base_url="https://api.fireworks.ai/inference/v1",
    api_key=API_KEY,
)

# ── System prompt with strict classification rules ──────────────────
SYSTEM_PROMPT = """You are an expert AI Request Triage Assistant for a professional services company.
Your job is to read an incoming client request and return structured triage information.

Classification rules:
- category: exactly one of [Sales, Support, Billing, Technical, Other]
- priority: exactly one of [Low, Medium, High, Urgent]
  • Urgent — security / data incidents, outages, or anything with imminent client / financial risk.
  • High — severe issues impacting work but not a complete outage.
  • Medium — standard requests, questions, or issues with a reasonable deadline.
  • Low — feature requests with no deadline, general feedback, or nice-to-haves.
- owner: exactly one of [Sales Team, Client Success, Finance, Engineering]
  • Sales Team — new business inquiries, pricing, demos.
  • Client Success — account management, general questions, non-technical setup.
  • Finance — billing, invoices, payments.
  • Engineering — technical issues, outages, bugs, data leaks.

Return ONLY valid JSON with exactly these six keys:
{
  "summary": "1-2 sentence summary of the request",
  "category": "one of the allowed categories",
  "priority": "one of the allowed priorities",
  "priority_reason": "one sentence explaining the priority",
  "owner": "one of the allowed owners",
  "draft_response": "a professional first-response email a team member could review and send"
}
Do NOT wrap in markdown. Do NOT add extra keys."""

# ── FastAPI app ─────────────────────────────────────────────────────
app = FastAPI(title="AI Request Triage Assistant")

# Serve the frontend
app.mount("/static", StaticFiles(directory="static"), name="static")


class TriageInput(BaseModel):
    text: str


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.post("/triage")
async def triage(payload: TriageInput):
    text = payload.text.strip()
    if not text:
        raise HTTPException(status_code=400, detail="Request text cannot be empty.")

    try:
        response = client.chat.completions.create(
            model="accounts/fireworks/models/deepseek-v4p1-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": text},
            ],
            response_format={"type": "json_object"},
            temperature=0.1,
        )
        raw = response.choices[0].message.content
        result = json.loads(raw)

        # Validate that all expected keys exist
        required = ["summary", "category", "priority", "priority_reason", "owner", "draft_response"]
        for key in required:
            if key not in result:
                result[key] = "N/A"

        return result

    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="The AI model returned invalid JSON. Please try again.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"API error: {str(e)}")


# ── Run with: python main.py ────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
