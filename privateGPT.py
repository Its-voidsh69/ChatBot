#!/usr/bin/env python3
import requests
from langchain.chains import RetrievalQA
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.vectorstores import Chroma
from langchain.llms import Ollama
import chromadb
import os
import argparse
import time

model = os.environ.get("MODEL", "mistral")
embeddings_model_name = os.environ.get("EMBEDDINGS_MODEL_NAME", "all-MiniLM-L6-v2")
persist_directory = os.environ.get("PERSIST_DIRECTORY", "db")
target_source_chunks = int(os.environ.get('TARGET_SOURCE_CHUNKS', 4))

from constants import CHROMA_SETTINGS

INGEST_URL = "http://localhost:8000/ingest"

def send_feedback(query: str, corrected_answer: str):
    """Send the query and corrected answer to the given URL in the required JSON format."""
    content = f"Query: {query}\n Answer: {corrected_answer}"
    payload = {
        "content": content,
        "source": "user"
    }
    try:
        response = requests.post(INGEST_URL, json=payload)
        response.raise_for_status()
        print("Server response:", response.text)
    except requests.RequestException as e:
        print("Error sending feedback:", e)

def main():
    args = parse_arguments()
    embeddings = HuggingFaceEmbeddings(model_name=embeddings_model_name)
    db = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = db.as_retriever(search_kwargs={"k": target_source_chunks})
    callbacks = [] if args.mute_stream else [StreamingStdOutCallbackHandler()]
    llm = Ollama(model=model, callbacks=callbacks)
    
    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever, return_source_documents=not args.hide_source
    )
    
    while True:
        query = input("\nEnter a query: ")
        if query.lower() == "exit":
            break
        if query.strip() == "":
            continue

        start = time.time()
        res = qa(query)
        answer, docs = res['result'], [] if args.hide_source else res['source_documents']
        end = time.time()

        print("\n\n> Question:")
        print(query)
        print(answer)

        for document in docs:
            print("\n> " + document.metadata["source"] + ":")
            print(document.page_content)
        
        while True:
            feedback = input("\nAre you satisfied with the answer? (yes/no): ").strip().lower()
            if feedback == "yes":
                break
            elif feedback == "no":
                corrected_answer = input("Enter the correct answer: ")
                send_feedback(query, corrected_answer)
                break
            else:
                print("Please enter 'yes' or 'no'.")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description='privateGPT: Ask questions to your documents without an internet connection, using the power of LLMs.'
    )
    parser.add_argument("--hide-source", "-S", action='store_true',
                        help='Use this flag to disable printing of source documents used for answers.')
    parser.add_argument("--mute-stream", "-M",
                        action='store_true',
                        help='Use this flag to disable the streaming StdOut callback for LLMs.')
    return parser.parse_args()

if __name__ == "__main__":
    main()
