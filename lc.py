import os
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings

from dotenv import load_dotenv

load_dotenv()
persist_directory = os.path.join(os.getcwd(), "db")
embeddings = OpenAIEmbeddings()

db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)

def get_relevant_info_from_question(query):
    relevant_info = []
    docs = db.similarity_search_with_score(query, k=5)

    for doc in docs:
        relevant_info.append({
                "snippet": doc[0].page_content,
                "podcast_title": doc[0].metadata["title"],
                "link": doc[0].metadata["description"] 
            })
    return relevant_info
