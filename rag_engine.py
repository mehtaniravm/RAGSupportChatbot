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