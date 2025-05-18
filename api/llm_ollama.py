import os
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class OllamaResponse:
    def __init__(self, content):
        self.content = content

    @staticmethod
    def stream(prompt, model="gemma3"):
        # For compatibility with LangChain's .stream()
        instructed_prompt = f"Please answer the following question using only Vietnamese. Absolutely do not use any English words or any other language: {prompt}"
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": model,
                "prompt": instructed_prompt,
                "stream": False
            },
            stream=False
        )
        response.raise_for_status()
        content = response.json()["response"]
        # Yield a single chunk for now (no real streaming)
        yield OllamaResponse(content)

def ask_ollama(question, model="gemma3"):
    # For direct calls (not streaming)
    instructed_question = f"Please answer the following question using only Vietnamese. Absolutely do not use any English words or any other language: {question}"
    response = requests.post(
        f"{OLLAMA_BASE_URL}/api/generate",
        json={
            "model": model,
            "prompt": instructed_question,
            "stream": False
        }
    )
    response.raise_for_status()
    return OllamaResponse(response.json()["response"])