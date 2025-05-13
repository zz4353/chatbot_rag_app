import os
from datetime import datetime
from langchain_core.documents import Document
from langchain_community.tools.tavily_search import TavilySearchResults


TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

def web_search(question):
    documents = []
    now = datetime.now().strftime("%Y-%m-%d")

    try:
        search = TavilySearchResults(tavily_api_key=TAVILY_API_KEY, max_results=5)
        
        docs = search.invoke({"query": question})
        for d in docs:
            metadata = {
                "summary": d['title'],
                "name": d['title'],
                "url": [d['url']],
                "created_on": now,
                "updated_at": now,
                "category": "None",
                "_run_ml_inference": True,
                "rolePermissions": []
            }

            doc = Document(
                page_content=d["content"],
                metadata=metadata
            )

            documents.append(doc)

    except Exception as error:
        print(error)

    return documents

if __name__ == "__main__":
    t = web_search("cách làm bánh mì thổ nhĩ kì")
    print(t)