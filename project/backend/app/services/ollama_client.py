"""
Ollama LLM Client.
Sends prompts to locally running Ollama instance and streams responses.
"""

import httpx
import json
from typing import List, Dict
from loguru import logger
from app.core.config import settings


SYSTEM_PROMPT = """You are an AI administrative assistant for the {department} department.

Your role:
- Answer questions ONLY about department matters: courses, procedures, faculty, schedules, deadlines, notices, academic policies, fees, and related topics.
- Use ONLY the provided context to answer. Do NOT fabricate information.
- If the context doesn't contain the answer, say so honestly and suggest contacting the department office.
- Be concise, helpful, and professional.
- Format responses clearly with bullet points or numbered lists when listing steps.
- Always cite the source when referencing specific documents.

Department: {department}
"""

def _build_prompt(query: str, context: str, conversation_history: List[Dict], department: str) -> List[Dict]:
    """Build the messages array for Ollama chat API."""
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(department=department)
        }
    ]

    # Add recent conversation history (last 6 turns)
    for turn in conversation_history[-6:]:
        if turn.get("role") in ("user", "assistant"):
            messages.append({"role": turn["role"], "content": turn["content"]})

    # Add context as a system message before the user query
    if context:
        messages.append({
            "role": "system",
            "content": f"## Retrieved Context (use this to answer)\n\n{context[:4000]}"
        })

    messages.append({"role": "user", "content": query})
    return messages


class OllamaClient:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def generate(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict],
        department: str,
    ) -> str:
        """Generate a response using Ollama chat API."""
        messages = _build_prompt(query, context, conversation_history, department)

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,       # Lower = more factual
                        "top_p": 0.9,
                        "num_ctx": 4096,
                        "stop": ["<|im_end|>", "[INST]"],
                    },
                },
            )
            response.raise_for_status()
            data = response.json()
            content = data.get("message", {}).get("content", "")
            if not content:
                raise ValueError("Empty response from Ollama")
            logger.debug(f"Ollama response length: {len(content)} chars")
            return content.strip()

    async def health_check(self) -> bool:
        """Check if Ollama is running and the model is available."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                models = [m["name"] for m in resp.json().get("models", [])]
                available = any(self.model in m for m in models)
                if not available:
                    logger.warning(
                        f"Model '{self.model}' not found in Ollama. "
                        f"Available: {models}. Run: ollama pull {self.model}"
                    )
                return available
        except Exception as e:
            logger.warning(f"Ollama health check failed: {e}")
            return False

    async def list_models(self) -> List[str]:
        """List all available Ollama models."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                return [m["name"] for m in resp.json().get("models", [])]
        except Exception:
            return []


ollama_client = OllamaClient()
