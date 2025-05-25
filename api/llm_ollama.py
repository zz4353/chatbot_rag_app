import os
import requests
from typing import List, Dict, Any, Generator, Optional
import json

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

class OllamaResponse:
    def __init__(self, content=None, model="gemma3", base_url=OLLAMA_BASE_URL, temperature=0.7):
        self.content = content
        self.model = model
        self.base_url = base_url
        self.temperature = temperature

    def invoke(self, prompt: str) -> 'OllamaResponse':
        """
        Send a prompt to Ollama and get a response
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "temperature": self.temperature
            }
        )
        response.raise_for_status()
        content = response.json()["response"]
        return OllamaResponse(content=content, model=self.model, base_url=self.base_url)
    
    def stream(self, prompt: str) -> Generator['OllamaResponse', None, None]:
        """
        Stream responses from Ollama for compatibility with LangChain's .stream()
        """
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": True,
                "temperature": self.temperature
            },
            stream=True
        )
        response.raise_for_status()
        
        # For incremental streaming
        buffer = ""
        for line in response.iter_lines():
            if not line:
                continue
                
            chunk = line.decode('utf-8')
            if chunk.startswith('data: '):
                chunk = chunk[6:]  # Remove 'data: ' prefix
                
            try:
                data = json.loads(chunk)
                if 'response' in data:
                    buffer += data['response']
                    yield OllamaResponse(content=data['response'], model=self.model, base_url=self.base_url)
                if data.get('done', False):
                    break
            except json.JSONDecodeError:
                continue
                
    def __str__(self):
        return self.content if self.content else ""