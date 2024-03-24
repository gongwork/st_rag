from langchain_community.vectorstores import FAISS

# from langchain.llms import GooglePalm
# from langchain.llms import OpenAI
from langchain_community.llms import (
    Ollama, GooglePalm, OpenAI
)

# from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings


from langchain.document_loaders.csv_loader import CSVLoader

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

import os
from pathlib import Path
import streamlit as st

from dotenv import load_dotenv
load_dotenv()  # take environment variables from .env (especially openai api key)

# # Initialize instructor embeddings using the Hugging Face model
# embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# @st.cache_resource
def create_llm(llm_provider="Ollama", model_name="", temperature=0.1):
    llm = None

    if llm_provider == "Google":
        # Create Google Palm LLM model
        model_name = "models/text-bison-001" if not model_name else model_name
        llm = GooglePalm(google_api_key=os.environ["API_KEY_GOOGLE_PALM"], model=model_name, temperature=temperature)
    elif llm_provider == "OpenAI":
        # Create OpenAI LLM model
        model_name = 'gpt-3.5-turbo-instruct' if not model_name else model_name
        llm = OpenAI(api_key=os.environ["API_KEY_OPENAI"], model=model_name, temperature=temperature)
    elif llm_provider == "Ollama":
        # Create Ollama LLM model locally
        base_url = 'http://localhost:11434'
        model_name = "llama2" if not model_name else model_name
        llm = Ollama(base_url=base_url, model=model_name, temperature=temperature)
    else:
        raise Exception(f"Unknown LLM: {llm_provider}")

    return llm

def create_vector_db(file_path='codebasics_faqs.csv', vectordb_file_path="faiss_index"):
    if Path(vectordb_file_path).exists():
        st.info(f"vector_db {vectordb_file_path} exists, skip")
        return

    # Load data from FAQ sheet
    loader = CSVLoader(file_path=file_path, source_column="prompt")
    data = loader.load()

    # Create a FAISS instance for vector database from 'data'
    vectordb = FAISS.from_documents(documents=data,
                                    embedding=embeddings)

    # Save vector database locally
    vectordb.save_local(vectordb_file_path)

def get_vector_db(vectordb_file_path="faiss_index"):
    # Load the vector database from the local folder
    return FAISS.load_local(vectordb_file_path, embeddings)

# # @st.cache_resource
# def get_qa_chain(vectordb_file_path="faiss_index"):
#     # Load the vector database from the local folder
#     vectordb = FAISS.load_local(vectordb_file_path, embeddings)

#     # Create a retriever for querying the vector database
#     retriever = vectordb.as_retriever(score_threshold=0.7)

#     prompt_template = """Given the following context and a question, generate an answer based on this context only.
#     In the answer try to provide as much text as possible from "response" section in the source document context without making much changes.
#     If the answer is not found in the context, kindly state "I don't know." Don't try to make up an answer.

#     CONTEXT: {context}

#     QUESTION: {question}"""

#     PROMPT = PromptTemplate(
#         template=prompt_template, input_variables=["context", "question"]
#     )

#     llm = create_llm(llm_provider="Google")

#     chain = RetrievalQA.from_chain_type(llm=llm,
#                                         chain_type="stuff",
#                                         retriever=retriever,
#                                         input_key="query",
#                                         return_source_documents=True,
#                                         chain_type_kwargs={"prompt": PROMPT})

#     return chain


@st.cache_resource
def create_rag_chain(llm_provider="Ollama"):
    llm = create_llm(llm_provider=llm_provider)
    vectordb = get_vector_db()
    retriever = vectordb.as_retriever()

    template = """Answer the question based only on the following context:
    {context}

    Question: {question}
    """
    prompt = ChatPromptTemplate.from_template(template)

    # Combine LLM and retriever into RetrievalQA chain
    chain = (
        {"context": retriever, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    return chain

if __name__ == "__main__":
    create_vector_db()
    chain = create_rag_chain()
    query = "Do you have javascript course?"
    print(chain.invoke(query))
