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
Step 1: Install Ollama
Go to: https://ollama.com/download
Choose your OS:
** Windows **
→ Download OllamaSetup.exe
→ Double-click → install (no admin rights needed anymore)
→ It starts a background service automatically
** macOS **
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
Step 2: Download + Run Llama 3.2 (easiest & recommended way)
Just run one of these commands:
```
# Most popular choice — 3B model, good quality + speed
ollama run llama3.2
```
Or if you want the tiny/fast one:
```
ollama run llama3.2:1b
```
What happens:
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
Step 3: Common useful commands
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
