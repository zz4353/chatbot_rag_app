import os
from grade_documents import document_relevant, YES, NO, AMBIGUOUS
from web_search import web_search

from elasticsearch_client import (
    elasticsearch_client,
)
from flask import render_template
from functools import cache
from langchain_elasticsearch import (
    ElasticsearchStore,
    SparseVectorStrategy,
)
from llm_integrations import get_llm
from app import app

INDEX = os.getenv("ES_INDEX", "workplace-app-docs")
INDEX_CHAT_HISTORY = os.getenv(
    "ES_INDEX_CHAT_HISTORY", "workplace-app-docs-chat-history"
)
ELSER_MODEL = os.getenv("ELSER_MODEL", ".elser_model_2")
SESSION_ID_TAG = "[SESSION_ID]"
SOURCE_TAG = "[SOURCE]"
DONE_TAG = "[DONE]"

store = ElasticsearchStore(
    es_connection=elasticsearch_client,
    index_name=INDEX,
    strategy=SparseVectorStrategy(model_id=ELSER_MODEL),
)


@cache
def get_lazy_llm():
    return get_llm()


def ask_question(question):
    llm = get_lazy_llm()

    condensed_question = question

    docs = store.as_retriever().invoke(condensed_question)
    
    is_relevant = document_relevant(question=question, docs=docs, chat_history=[])

    if is_relevant == YES:
        pass
    elif is_relevant == NO:
        docs = web_search(condensed_question)
    else:
        docs.extend(web_search(condensed_question))

    qa_prompt = render_template(
        "rag_batch_prompt.txt",
        question=question,
        docs=docs,
    )

    answer = ""
    for chunk in llm.stream(qa_prompt):
        answer += chunk.content
    
    return answer


# lưu kết quả vào file
def save_answer_to_file(path, question, answer):
    with open(path, "a", encoding="utf-8") as file:
        file.write(f"Question: {question}\n")
        file.write(f"Answer: {answer}\n")


if __name__ == "__main__":
    path = os.path.join(os.path.dirname(__file__), "..", "data", "questions1.txt")
    questions = []
    with open(path, "r", encoding="utf-8") as file:
        questions = [line.strip() for line in file]
    
    save_path = os.path.join(os.path.dirname(__file__), "..", "data", "answers.txt")

    with app.app_context():
        for question in questions:
            answer = ask_question(question)
            answer = answer.replace('\n', ' ')
            
            save_answer_to_file(save_path, question, answer)
            print("-" * 50)
            print(f"Question: {question}")
            print(f"Answer: {answer}")



    
