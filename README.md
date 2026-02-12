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
    ** How to Install Ollama llama3.2**
    