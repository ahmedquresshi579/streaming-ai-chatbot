import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv
from mistralai.client import Mistral

load_dotenv()

API_KEY = os.getenv("MISTRAL_API_KEY")
if not API_KEY:
    raise RuntimeError("MISTRAL_API_KEY not found in .env")

client = Mistral(api_key=API_KEY)
MODEL = "mistral-small-latest"

app = FastAPI()

# Allow the frontend to call this API. "*" is fine for local dev only —
# lock this down to your actual frontend origin before deploying anywhere public.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Simple in-memory conversation history.
# Lives only as long as the server process runs — restart wipes it.
# Fine for a single-user demo. Not fine for multi-user without adding
# per-session keys (e.g. a session_id from the frontend) instead of one global list.
conversation_history = []

MAX_HISTORY_MESSAGES = 20  # keep last N messages so we don't blow the context window


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conversation_history.append({"role": "user", "content": request.message})
    trimmed_history = conversation_history[-MAX_HISTORY_MESSAGES:]

    try:
        response = client.chat.complete(
            model=MODEL,
            messages=trimmed_history,
        )
    except Exception as e:
        # Catches auth errors, rate limits, timeouts, model errors — all of it.
        # In production you'd branch on error type/status code for cleaner messages.
        raise HTTPException(status_code=502, detail=f"LLM API error: {str(e)}")

    reply = response.choices[0].message.content
    conversation_history.append({"role": "assistant", "content": reply})

    return {"reply": reply}


@app.post("/chat/stream")
def chat_stream(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conversation_history.append({"role": "user", "content": request.message})
    trimmed_history = conversation_history[-MAX_HISTORY_MESSAGES:]

    def event_generator():
        full_reply = ""
        try:
            stream_response = client.chat.stream(
                model=MODEL,
                messages=trimmed_history,
                stream=True,
            )
            with stream_response as event_stream:
                for event in event_stream:
                    delta = event.data.choices[0].delta.content
                    if delta:
                        full_reply += delta
                        yield f"data: {json.dumps({'content': delta})}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            return

        conversation_history.append({"role": "assistant", "content": full_reply})
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.post("/reset")
def reset_conversation():
    conversation_history.clear()
    return {"status": "conversation reset"}


@app.get("/history")
def get_history():
    return {"history": conversation_history}


# Serve the frontend. Put index.html inside a "static" folder next to this file.
app.mount("/", StaticFiles(directory="static", html=True), name="static")