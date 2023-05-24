import os
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from dotenv import load_dotenv

load_dotenv()

persist_directory = os.path.join(os.getcwd(), "db")

# create the embeddings
embeddings = OpenAIEmbeddings()

db = Chroma(persist_directory=persist_directory, embedding_function=embeddings) # Load the vector store

def search_relevant_info(question):
    relevant_info = []
    docs = db.similarity_search_with_score(question, k=10)
    for doc, score in docs:
        if score > 0.2:
            relevant_info.append({
                "snippet": doc.page_content[:600],
                "podcast_title": doc.metadata['source'],
                "link": doc.metadata['link']
            })
    return relevant_info
docs = db.similarity_search_with_score("investing", k=10)

# Print the results
for doc, score in docs:
    print(f"Page {doc.metadata['page']}: {doc.page_content[:300]}")
    print(f"Score: {score}")
    print("-----------------------------------------")
