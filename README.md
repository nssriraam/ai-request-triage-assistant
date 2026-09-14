# AI Request Triage Assistant

▶️ **[Watch the Demo Video](https://youtu.be/nLhp8glK49E)**

A working prototype built for the Node Solutions technical challenge. It takes an unstructured client request (email, form, chat) and returns a structured triage: summary, category, priority with reasoning, routing owner, and a ready-to-send draft response.

## What it does

Given raw text input, the assistant returns:
- **Summary**: a 1-2 sentence recap of the request
- **Category**: Sales, Support, Billing, Technical, or Other
- **Priority**: Low, Medium, High, or Urgent, with a one-line reason
- **Owner**: Sales Team, Client Success, Finance, or Engineering
- **Draft response**: a professional first reply a team member can review and send

## Stack

- **Backend:** FastAPI (Python)
- **AI:** Fireworks AI (DeepSeek model) via an OpenAI-compatible client
- **Frontend:** Static HTML/CSS/JS served directly from FastAPI. No framework, kept intentionally simple.
- **Output:** Enforced strict JSON response format from the model, with key validation as a fallback

## How it works

1. User pastes a request into the textarea and clicks **Triage Request**.
2. The frontend sends the text to a single `POST /triage` endpoint.
3. The backend sends it to the LLM with a system prompt that encodes explicit classification rules (what counts as Urgent vs Medium, how category maps to owner, etc.).
4. The model returns strict JSON, which is validated (missing keys are filled with `"N/A"` so the UI never breaks) and returned to the frontend.
5. Results render as color-coded priority/category/owner badges plus the summary, reasoning, and draft response.

## Key design decisions

- **Single LLM call instead of a multi-step pipeline**: keeps the prototype fast, simple, and easy to explain, at the cost of less robustness on ambiguous inputs than a multi-agent approach would offer.
- **Hardcoded classification rules in the system prompt** (e.g., security/data incidents and outages = Urgent; no-deadline feature requests = Low) rather than leaving categorization fully open-ended, for consistency across runs.
- **Low temperature (0.1)** to favor consistent, predictable classification over creative variation.
- **Strict JSON output + key validation** so a malformed model response degrades gracefully instead of crashing the UI.

## Limitations

- No authentication, persistence, or request history. Out of scope for a 48-hour functional prototype.
- No confidence score or human-review flag for borderline classifications.
- Routing is a label only. It doesn't actually notify or assign anything in a real system.

## What I'd improve next

- Add a confidence score / "needs human review" flag for ambiguous cases.
- Persist past triages for auditing and to refine prompt rules over time using real outcomes.
- Add real routing — Slack or email webhook to actually notify the assigned team.
- Add few-shot examples to the prompt to handle edge cases as they're discovered.

## Running locally

1. Clone the repo and install dependencies: `pip install fastapi uvicorn openai python-dotenv`
2. Create a `.env` file with `FIREWORKS_API_KEY=your_key_here`
3. Run: `python main.py`
4. Open `http://127.0.0.1:8000`

## Demo requests tested

Includes all 6 mock requests from the challenge, including the accidental data-leak scenario (#05), which the assistant correctly flags as Urgent/Engineering due to the security exposure, despite the calm tone of the message.
