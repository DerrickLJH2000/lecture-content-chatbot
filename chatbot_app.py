from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain.chains import RetrievalQA

import streamlit as st
from dotenv import load_dotenv
import glob

load_dotenv()

PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')
PINECONE_ENV = os.getenv('PINECONE_ENV')
PINECONE_INDEX_NAME = os.getenv('PINECONE_INDEX_NAME')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

os.environ['OPENAI_API_KEY'] = OPENAI_API_KEY

def doc_preprocessing():
    documents = []

    # List all folders in the 'data' directory
    folder_paths = glob.glob('./data/*/')

    for folder_path in folder_paths:
        # Get the name of the folder (course name)
        folder_name = os.path.basename(os.path.normpath(folder_path))

        # List all PDF files in the folder
        file_paths = glob.glob(folder_path + '*.pdf')

        for file_path in file_paths:
            loader = PyPDFLoader(file_path)
            doc = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=0,
                separators=["\n\n", "\n", " ", ""]
            )
            docs_split = text_splitter.split_documents(documents=doc)

def doc_preprocessing():
    documents = []

    # List all folders in the 'data' directory
    folder_paths = glob.glob('./data/*/')

    for folder_path in folder_paths:
        # Get the name of the folder (course name)
        folder_name = os.path.basename(os.path.normpath(folder_path))

        # List all PDF files in the folder
        file_paths = glob.glob(folder_path + '*.pdf')

        for file_path in file_paths:
            loader = PyPDFLoader(file_path)
            doc = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=0,
                separators=["\n\n", "\n", " ", ""]
            )
            docs_split = text_splitter.split_documents(documents=doc)

            # Add the processed documents to the list
            documents.extend(docs_split)

    return documents


    return documents

@st.cache_resource
def embedding_db():
    embeddings = OpenAIEmbeddings()
    pc = Pinecone(api_key=PINECONE_API_KEY)

    docs_split = doc_preprocessing()
    doc_db = PineconeVectorStore.from_documents(documents=docs_split, embedding=embeddings, index_name=PINECONE_INDEX_NAME)
    return doc_db

llm = ChatOpenAI()
doc_db = embedding_db()

def retrieval_answer(query):
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=doc_db.as_retriever(),
    )
    result = qa.run(query)
    return result

def main():
    st.title("Lecture Content Question Answering Bot")
    text_input = st.text_input("Ask your query...")
    if st.button("Ask Query"):
        if len(text_input) > 0:
            st.info("Your query: " + text_input)
            answer = retrieval_answer(text_input)
            st.success(answer)

if __name__ == "__main__":
    main()
