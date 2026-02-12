# project SupportRAG. RAGSupportChatbot
## What You’ll Get

Answers strictly grounded in your documentation (RAG)

“I don’t know” or fallback when info is missing

Smart detection of “talk to agent / human / support” requests

Automatic handoff: sends full conversation history + issue summary to your internal support app via webhook

Easy-to-embed chat widget for any website (HTML/JS, works with React, Next.js, WordPress, etc.)

Local-first (free) for development, easy to switch to Grok / Claude / GPT in production

## Recommended Tech Stack (2026 Best Practice)

Backend: FastAPI (fast, modern)

RAG Framework: LlamaIndex (best-in-class for accurate retrieval & grounding)

Vector DB: Chroma (simple, persistent, local)

LLM for dev: Ollama (local, free — use Llama 3.2 or similar)

LLM for production: Grok (via xAI API — OpenAI-compatible) or Claude 3.5/GPT-4o

Frontend: Lightweight embeddable JS widget (no heavy framework required)

## Step-by-Step Guide
### Step 1: Prerequisites

Python 3.11+

Ollama installed and running → ollama pull llama3.2 (or llama3.2:3b for faster testing)

Git

**How to Install Ollama llama3.2**

**Step 1.1: Install Ollama**

Go to: https://ollama.com/download

Choose your OS:

**Windows**

> → Download OllamaSetup.exe
> → Double-click → install (no admin rights needed anymore)
> → It starts a background service automatically

**macOS**

→ Download the .zip or use Homebrew:
```
brew install ollama
```

→ or drag Ollama.app to Applications

After install, open a new terminal (or PowerShell / cmd on Windows) and type:
```
ollama --version
```

You should see something like ollama version 0.3.x or newer.

**Step 1.2: Download + Run Llama 3.2 (easiest & recommended way)**

Just run one of these commands:
```
# Most popular choice — 3B model, good quality + speed
ollama run llama3.2
```

Or if you want the tiny/fast one:
```
ollama run llama3.2:1b
```

_What happens:_

Ollama checks if the model exists locally

Downloads it automatically (~2 GB for 3B, takes 1–10 min depending on internet)

Loads it into memory

Opens an interactive chat right in your terminal

**You can now type questions:**
```
>>> What is the capital of Georgia (the country)?
>>> Write a funny haiku about AI developers
>>> /bye    ← to exit
```
**Step 1.3: Common useful commands**

List what you have downloaded:
```
ollama list
```

Download without immediately running (useful for later):
```
ollama pull llama3.2:1b
ollama pull llama3.2       # 3B
```

Run in background + talk via API (very common for apps / VS Code / Open WebUI):
```
# Terminal 1: start server (stays running)
ollama serve
# Terminal 2: test it
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue? Answer in one short sentence."
}'
```

To stop / exit the Ollama CLI interactive chat (the one you get after running ollama run llama3.2), here are the cleanest & most common ways (as of early 2026):

1. Easiest & recommended (inside the chat)

   Just type one of these at the prompt (exactly like this — including the slash):
```
/bye
```

or

```
exit
```

###Step 2: Project Setup

```
mkdir supportrag && cd supportrag
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-multipart python-dotenv
pip install llama-index llama-index-llms-ollama llama-index-embeddings-huggingface llama-index-vector-stores-chroma chromadb pypdf
```

Create these files/folders:
```
supportrag/
├── main.py                 # FastAPI app
├── ingestion.py            # Load knowledge base
├── rag_engine.py           # Core RAG logic
├── .env                    # Configuration
├── data/                   # Put your PDFs, .txt, .md, Notion exports here
├── chroma_db/              # Auto-created persistent vector store
└── requirements.txt
```

.env file:
```
LLM_MODEL=llama3.2
EMBED_MODEL=BAAI/bge-small-en-v1.5
COLLECTION_NAME=support_docs
SUPPORT_WEBHOOK_URL=https://your-internal-support-app.com/api/handoff   # ← Change this
API_KEY=your-secret-widget-key   # For production security
```

###Step 3: Ingestion Script (ingestion.py)
```
import os
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import chromadb

load_dotenv()

# Settings
Settings.embed_model = HuggingFaceEmbedding(model_name=os.getenv("EMBED_MODEL"))

# Chroma
db = chromadb.PersistentClient(path="./chroma_db")
chroma_collection = db.get_or_create_collection(os.getenv("COLLECTION_NAME"))
vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

# Load documents
documents = SimpleDirectoryReader("data").load_data()

# Create or update index
index = VectorStoreIndex.from_documents(documents, vector_store=vector_store, show_progress=True)
print("✅ Knowledge base ingested!")
```

Run once (or whenever docs change):
```
python ingestion.py
```

###Step 4: RAG Engine with Escalation (rag_engine.py)
```
import json
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.llms import ChatMessage, MessageRole

Settings.llm = Ollama(model="llama3.2", request_timeout=120.0)

# For production Grok swap:
# from llama_index.llms.openai_like import OpenAILike
# Settings.llm = OpenAILike(model="grok-4", api_base="https://api.x.ai/v1", api_key="xai-...")

def get_query_engine(index):
    return index.as_query_engine(similarity_top_k=6)

def should_escalate_and_handoff(history: list, user_message: str, index) -> dict:
    system_prompt = """
    You are a helpful support chatbot. Answer ONLY using the provided knowledge base.
    If the user explicitly asks for a human/agent/support/escalation, respond EXACTLY in this JSON format and nothing else:
    {"action": "escalate", "message": "Connecting you to a support agent...", "summary": "Brief 1-sentence summary of the issue"}
    
    Otherwise, give a normal helpful answer grounded in the knowledge base.
    """

    messages = [ChatMessage(role=MessageRole.SYSTEM, content=system_prompt)]
    messages.extend([ChatMessage(role=msg["role"], content=msg["content"]) for msg in history])
    messages.append(ChatMessage(role=MessageRole.USER, content=user_message))

    response = Settings.llm.chat(messages)
    content = response.message.content.strip()

    try:
        if content.startswith("{") and "action" in content:
            data = json.loads(content)
            if data.get("action") == "escalate":
                return data
    except:
        pass
    return {"action": "answer", "content": content}
```

###Step 5: FastAPI Backend (main.py)
```
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
```

Run the server:
```
uvicorn main:app --reload --port 8000
```

###Step 6: Embeddable Chat Widget (for any web app)

Create widget.html (or add this script to your site):

```
<div id="support-chat" style="position:fixed;bottom:20px;right:20px;z-index:9999;">
  <button onclick="toggleChat()" style="background:#000;color:white;padding:12px 20px;border-radius:9999px;border:none;cursor:pointer;">
    💬 Need help?
  </button>
  
  <div id="chat-window" style="display:none;background:white;width:380px;height:520px;border-radius:12px;box-shadow:0 10px 30px rgba(0,0,0,0.2);margin-top:10px;overflow:hidden;flex-direction:column;">
    <div id="chat-messages" style="flex:1;padding:15px;overflow-y:auto;"></div>
    <input id="chat-input" placeholder="Type your message..." style="padding:12px;border:none;border-top:1px solid #eee;" onkeypress="if(event.key==='Enter') sendMessage()">
  </div>
</div>

<script>
const API_URL = "http://localhost:8000/chat";   // Change to your deployed URL
const SESSION_ID = "user-" + Math.random().toString(36).slice(2);

function toggleChat() {
  const win = document.getElementById("chat-window");
  win.style.display = win.style.display === "flex" ? "none" : "flex";
}

async function sendMessage() {
  const input = document.getElementById("chat-input");
  const msg = input.value.trim();
  if (!msg) return;
  
  addMessage("user", msg);
  input.value = "";

  const res = await fetch(API_URL, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({message: msg, session_id: SESSION_ID})
  });
  const data = await res.json();

  addMessage("bot", data.response);

  if (data.escalate) {
    addMessage("bot", "✅ A support agent has been notified with full context.");
    // Optional: window.open(your_internal_support_url);
  }
}

function addMessage(sender, text) {
  const div = document.createElement("div");
  div.style.marginBottom = "10px";
  div.style.padding = "8px";
  div.style.borderRadius = "8px";
  div.style.maxWidth = "80%";
  div.style.background = sender === "user" ? "#007bff" : "#f1f1f1";
  div.style.color = sender === "user" ? "white" : "black";
  div.style.alignSelf = sender === "user" ? "flex-end" : "flex-start";
  div.innerHTML = text;
  document.getElementById("chat-messages").appendChild(div);
  div.scrollIntoView();
}
</script>
```

###Step 7: Running & Testing

1. Put sample docs in /data
2. Run python ingestion.py
3. Run uvicorn main:app --reload
4. Open widget.html or embed the script
5. Test normal questions → should be grounded
6. Type “I want to speak to a human” → should escalate and call your webhook

Test the webhook by setting a simple test URL (e.g., webhook.site) in .env.

###Step 8: Production & Integration Tips

Swap LLM: Replace Ollama with Grok using OpenAILike (see comment in rag_engine.py)

Sessions: Replace dict with Redis

Security: Add API key check in /chat

Deployment: Render, Railway, Fly.io, or Vercel (with FastAPI)

Scaling: Switch Chroma → Pinecone or Weaviate

Better Escalation: Add LangGraph for multi-step routing if needed

Analytics: Log conversations
