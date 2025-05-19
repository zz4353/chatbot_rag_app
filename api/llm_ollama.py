import os
import json
import requests

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class OllamaResponse:
    def __init__(self, content):
        self.content = content

class ChatOllama:
    def __init__(self, model, streaming=True, temperature=0):
        self.model = model
        self.streaming = streaming
        self.temperature = temperature

    def stream(self, prompt):
        instructed_prompt = f"Please answer the following question using the same language as the question itself: {prompt}"
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/generate",
            json={
                "model": self.model,
                "prompt": instructed_prompt,
                "stream": True,
                "temperature": self.temperature,
            },
            stream=True
        )
        response.raise_for_status()
        for line in response.iter_lines(decode_unicode=True):
            if line:
                data = json.loads(line)
                chunk = data.get("response", "")
                if chunk:
                    yield OllamaResponse(chunk)

if __name__ == "__main__":
    # Example usage
    question = "Thành phố nào là thủ đô của việt nam?"
    ollama = ChatOllama(model="gemma3")

    answer = ""
    for i in ollama.stream(question):
        answer += i.content
    print("Final Answer:", answer)