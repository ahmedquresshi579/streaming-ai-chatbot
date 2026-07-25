

https://github.com/user-attachments/assets/72f1cca0-abb3-4ed3-9b95-84759145ba34

# AI Chat API

A lightweight chat application built with **FastAPI** and the **Mistral AI API**, featuring real-time streaming responses, in-memory conversation history, and a custom-designed frontend.

---

## Features

- **`POST /chat`** — send a prompt, get a full response back as JSON
- **`POST /chat/stream`** — same thing, but streamed token-by-token via Server-Sent Events (SSE)
- **Conversation memory** — the backend keeps track of the last 20 messages so the AI has context across turns
- **`POST /reset`** — clear the conversation history
- **`GET /history`** — inspect the current conversation state
- **Graceful error handling** — API failures (auth errors, rate limits, timeouts) return clean HTTP error responses instead of crashing
- **Custom frontend** — a single-page chat UI with streaming text, no framework required

---

## Tech Stack

| Layer         | Choice                                   |
|---------------|-------------------------------------------|
| Backend       | FastAPI (Python)                          |
| LLM Provider  | [Mistral AI](https://mistral.ai) (`mistral-small-latest`) |
| Streaming     | Server-Sent Events (SSE)                  |
| Frontend      | Vanilla HTML / CSS / JS (no build step)   |
| Secrets       | `.env` via `python-dotenv`                |

---

## Project Structure

```
AI CHATBOT/
├── main.py              # FastAPI backend — routes, streaming, history
├── static/
│   └── index.html        # Frontend chat UI (served at "/")
├── test_key.py            # Standalone script to verify the API key works
├── .env                    # MISTRAL_API_KEY (not committed)
├── .gitignore
└── README.md
```

---

## Setup

### 1. Clone the repo

```bash
git clone https://github.com/tcintern-013/AI-ChatBot-using-python.git
cd AI-ChatBot-using-python
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it:

```bash
# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install fastapi uvicorn mistralai python-dotenv
```

### 4. Add your API key

Create a `.env` file in the project root:

```
MISTRAL_API_KEY=your_key_here
```

Get a free key at [console.mistral.ai](https://console.mistral.ai) (requires phone verification, no credit card needed).

### 5. (Optional) Verify the key works

```bash
python test_key.py
```

You should see `API key works` printed.

### 6. Run the server

```bash
python -m uvicorn main:app --reload
```

> If `uvicorn main:app --reload` fails with an "Application Control policy" error on Windows, use `python -m uvicorn main:app --reload` instead — it routes through `python.exe` rather than the standalone `uvicorn.exe` binary.

### 7. Open the app

Go to **http://127.0.0.1:8000** in your browser.

---

## API Reference

### `POST /chat`

Non-streaming chat completion.

**Request body:**
```json
{ "message": "Hello, how are you?" }
```

**Response:**
```json
{ "reply": "I'm doing well, thanks for asking!" }
```

### `POST /chat/stream`

Streaming chat completion via SSE. Emits events like:

```
data: {"content": "I'm"}
data: {"content": " doing"}
data: {"content": " well"}
data: [DONE]
```

### `POST /reset`

Clears the in-memory conversation history.

### `GET /history`

Returns the full conversation history currently held in memory.

---

## Known Limitations

- **Conversation history is in-memory and global** — it resets when the server restarts, and is shared across all users/tabs rather than being per-session. Fine for local/single-user use; would need session IDs for multi-user support.
- **No rate limiting** — if deployed publicly, the `/chat` endpoints could be hit repeatedly and burn through API quota. Worth adding before any public deployment.
- **No authentication** — anyone with access to the running server can use the chat endpoints.

---

## License

MIT
