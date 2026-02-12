from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends
from fastapi.middleware.cors import CORSMiddleware
import json, os
from dotenv import load_dotenv
from rag_engine import should_escalate_and_handoff, get_query_engine
from ingestion import vector_store   # reuse the same store
import httpx

load_dotenv()
app = FastAPI(title="SupportRAG")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

# In-memory sessions (use Redis in production)
sessions = {}

index = VectorStoreIndex.from_vector_store(vector_store)
query_engine = get_query_engine(index)

async def call_support_webhook(summary: str, history: list):
    webhook = os.getenv("SUPPORT_WEBHOOK_URL")
    if webhook:
        payload = {"summary": summary, "conversation": history}
        async with httpx.AsyncClient() as client:
            await client.post(webhook, json=payload, timeout=10)

@app.post("/chat")
async def chat_endpoint(message: str, session_id: str = "default"):
    if session_id not in sessions:
        sessions[session_id] = []
    
    history = sessions[session_id]
    history.append({"role": "user", "content": message})

    result = should_escalate_and_handoff(history, message, index)

    if result.get("action") == "escalate":
        await call_support_webhook(result["summary"], history)
        response_msg = result["message"]
        sessions[session_id].append({"role": "assistant", "content": response_msg})
        return {"response": response_msg, "escalate": True, "summary": result["summary"]}
    else:
        response_msg = result["content"]
        sessions[session_id].append({"role": "assistant", "content": response_msg})
        return {"response": response_msg, "escalate": False}