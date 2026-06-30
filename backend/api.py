from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.rag.summarizer import generate_summary
from backend.rag.chain import rag_chain
from backend.rag.ingestion import ingest_single_file
from backend.rag.history import get_chat_history
from backend.rag.loader import load_documents
from langsmith import traceable
from pathlib import Path
import json

app = FastAPI()

# =========================
# CORS
# =========================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# PATHS
# =========================

DOCS_DIR = Path("backend/data/docs")
CHAT_FILE = Path("backend/db/chat_history.json")

DOCS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

CHAT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# =========================
# SCHEMA
# =========================

class ChatRequest(BaseModel):
    user_query: str

class SummaryRequest(BaseModel):
    filename: str

# =========================
# HOME
# =========================

@app.get("/")
def home():

    return {
        "message": "RAG API Running"
    }

# =========================
# CHAT
# =========================
@traceable(name="chat", run_type="chain")
@app.post("/chat")
def chat(req: ChatRequest):

    history = get_chat_history()

    # save user message
    history.add_user_message(req.user_query)
    messages_to_send = history.messages[-12:]

    response = rag_chain.invoke({
        "input": req.user_query,
        "chat_history": messages_to_send
    })

    answer = response["answer"]

    # save assistant message
    history.add_ai_message(answer)

    return {
        "answer": answer
    }

# =========================
# GET CHAT
# =========================

@app.get("/chat")
def get_chat():

    if not CHAT_FILE.exists():

        return {
            "messages": []
        }

    with open(CHAT_FILE, "r", encoding="utf-8") as f:

        data = json.load(f)

    messages = []

    for msg in data:

        msg_type = msg.get("type")

        if msg_type == "human":

            role = "user"

        elif msg_type == "ai":

            role = "assistant"

        else:
            continue

        messages.append({
            "role": role,
            "content": msg["data"]["content"]
        })

    return {
        "messages": messages
    }

# =========================
# CLEAR CHAT
# =========================

@app.delete("/chat")
def clear_chat():

    if CHAT_FILE.exists():

        CHAT_FILE.unlink()

    return {
        "message": "Chat cleared"
    }

# =========================
# UPLOAD
# =========================
@traceable(name="upload_file", run_type="tool")
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    file_path = DOCS_DIR / file.filename

    if file_path.exists():

        return {
            "message": f"{file.filename} already exists"
        }

    with open(file_path, "wb") as f:

        f.write(await file.read())

    ingest_single_file(str(file_path))

    return {
        "message": f"{file.filename} uploaded"
    }

# =========================
# FILES
# =========================

@app.get("/files")
def get_files():

    files = []

    for file in DOCS_DIR.iterdir():

        if file.is_file():

            files.append({
                "name": file.name
            })

    return files

# =========================
# SUMMARIZE FILE
# =========================
@traceable(name="summarize_file", run_type="tool")
@app.post("/summarize-file")
async def summarize_file(req: SummaryRequest):

    file_path = DOCS_DIR / req.filename

    if not file_path.exists():

        return {
            "summary": "File not found"
        }

    # =========================
    # LOAD DOCUMENTS PROPERLY
    # =========================

    documents = load_documents(
        str(file_path)
    )

    # =========================
    # GENERATE SUMMARY
    # =========================

    summary = await generate_summary(
        filename=req.filename,
        documents=documents
    )

    return {
        "summary": summary
    }