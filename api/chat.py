import json
import os
from grade_documents import document_relevant, YES, NO, AMBIGUOUS
from web_search import web_search

from elasticsearch_client import (
    elasticsearch_client,
    get_elasticsearch_chat_message_history,
)
from flask import current_app, render_template, stream_with_context
from functools import cache
from langchain_elasticsearch import (
    ElasticsearchStore,
    SparseVectorStrategy,
)
from llm_integrations import get_llm

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


@stream_with_context
def ask_question(question, session_id):
    llm = get_lazy_llm()

    yield f"data: {SESSION_ID_TAG} {session_id}\n\n"
    current_app.logger.debug("Chat session ID: %s", session_id)

    chat_history = get_elasticsearch_chat_message_history(
        INDEX_CHAT_HISTORY, session_id
    )

    if len(chat_history.messages) > 0:
        # create a condensed question
        condense_question_prompt = render_template(
            "condense_question_prompt.txt",
            question=question,
            chat_history=chat_history.messages,
        )
        condensed_question = llm.invoke(condense_question_prompt).content
    else:
        condensed_question = question

    current_app.logger.debug("Condensed question: %s", condensed_question)
    current_app.logger.debug("Question: %s", question)

    docs = store.as_retriever().invoke(condensed_question)
    
    is_relevant = document_relevant(question=question, docs=docs, chat_history=chat_history.messages)


    if is_relevant == YES:
        yield f"data: <b>Using internal data</b> <br><br>\n\n"
    elif is_relevant == NO:
        docs = web_search(condensed_question)
        yield f"data: <b>Searching online</b> <br><br>\n\n"
    else:
        docs.extend(web_search(condensed_question))
        yield f"data: <b>Using internal data & online search</b> <br><br>\n\n"


    for doc in docs:
        doc_source = {**doc.metadata, "page_content": doc.page_content}
        current_app.logger.debug(
            "Retrieved document passage from: %s", doc.metadata["name"]
        )
        yield f"data: {SOURCE_TAG} {json.dumps(doc_source)}\n\n"

    qa_prompt = render_template(
        "rag_prompt.txt",
        question=question,
        docs=docs,
        chat_history=chat_history.messages,
    )

    answer = ""
    for chunk in llm.stream(qa_prompt):
        current_chunk_content = ""
        if hasattr(chunk, 'content'):
            current_chunk_content = chunk.content
        elif isinstance(chunk, str):
            current_chunk_content = chunk
        else:
            # Fallback for unexpected chunk type, log this if it happens
            current_app.logger.warning(f"Unexpected chunk type in qa_prompt stream: {type(chunk)}")
            current_chunk_content = str(chunk)

        # Replace newlines in the content intended for display/SSE
        display_content = current_chunk_content.replace("\n", " ")
        yield f"data: {display_content}\n\n"
        
        # Append the original chunk content (with newlines) to the full answer
        answer += current_chunk_content

    yield f"data: {DONE_TAG}\n\n"

    chat_history.add_user_message(question)
    chat_history.add_ai_message(answer)
