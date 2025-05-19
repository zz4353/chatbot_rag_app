import os

from langchain_aws import ChatBedrock
from langchain_cohere import ChatCohere
from langchain_google_vertexai import ChatVertexAI
from langchain_mistralai import ChatMistralAI
from langchain_openai import AzureChatOpenAI, ChatOpenAI
from langchain_ollama import OllamaLLM  # Assuming langchain-ollama is installed

LLM_TYPE = os.getenv("LLM_TYPE", "ollama")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3")  # Or your preferred Ollama model


def init_openai_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return ChatOpenAI(
        model=os.getenv("CHAT_MODEL"),
        streaming=True,
        temperature=temperature,
        model_kwargs={"stream_options": {"include_usage": True}},
    )


def init_vertex_chat(temperature):
    # opentelemetry-instrumentation-vertexai is included by EDOT, but does not
    # yet not support streaming. Use the Langtrace Python SDK instead.
    from langtrace_python_sdk.instrumentation import VertexAIInstrumentation

    VertexAIInstrumentation().instrument()
    return ChatVertexAI(
        model_name=os.getenv("CHAT_MODEL"), streaming=True, temperature=temperature
    )


def init_azure_chat(temperature):
    # Include streaming usage as this allows recording of LLM metrics
    return AzureChatOpenAI(
        model=os.getenv("CHAT_DEPLOYMENT"),
        streaming=True,
        temperature=temperature,
        model_kwargs={"stream_options": {"include_usage": True}},
    )


def init_bedrock(temperature):
    return ChatBedrock(
        model_id=os.getenv("CHAT_MODEL"),
        streaming=True,
        model_kwargs={"temperature": temperature},
    )


def init_mistral_chat(temperature):
    return ChatMistralAI(
        model=os.getenv("CHAT_MODEL"), streaming=True, temperature=temperature
    )


def init_cohere_chat(temperature):
    # Cohere is not yet in EDOT. Use the Langtrace Python SDK instead
    from langtrace_python_sdk.instrumentation import CohereInstrumentation

    CohereInstrumentation().instrument()
    return ChatCohere(model=os.getenv("CHAT_MODEL"), temperature=temperature)


def init_ollama_chat(temperature):
    # Note: OllamaLLM might not use temperature in the same way or at all via its constructor.
    # Refer to LangChain documentation for specific OllamaLLM parameters.
    # For basic use, model and base_url are key.
    return OllamaLLM(
        model=OLLAMA_MODEL,
        base_url=OLLAMA_BASE_URL,
        temperature=temperature,  # Pass temperature if supported, otherwise it might be ignored or handled differently
    )


MAP_LLM_TYPE_TO_CHAT_MODEL = {
    "azure": init_azure_chat,
    "bedrock": init_bedrock,
    "openai": init_openai_chat,
    "vertex": init_vertex_chat,
    "mistral": init_mistral_chat,
    "cohere": init_cohere_chat,
    "ollama": init_ollama_chat,  # Add Ollama to the map
}


def get_llm(temperature=0):
    if LLM_TYPE not in MAP_LLM_TYPE_TO_CHAT_MODEL:
        raise Exception(
            "LLM type not found. Please set LLM_TYPE to one of: "
            + ", ".join(MAP_LLM_TYPE_TO_CHAT_MODEL.keys())
            + "."
        )

    return MAP_LLM_TYPE_TO_CHAT_MODEL[LLM_TYPE](temperature=temperature)
