from datetime import datetime
import jsonlines
from pathlib import Path
from time import time

from langchain_helper import (
    create_vector_db, create_rag_chain
)


import streamlit as st

def load_jsonl(file_path):
    if not file_path.exists():
        return
    
    chats = []
    with jsonlines.open(file_path) as reader:
        for obj in reader:
            chats.append(obj)
        st.session_state["chat_records"] = chats

def dump_jsonl(file_path):
    if "chat_records" not in st.session_state:
        return 
    
    with jsonlines.open(file_path, mode='w') as writer:
        for obj in st.session_state["chat_records"]:
            writer.write(obj)  

# init
file_chat_records = Path("chat_record.jsonl")
if "chat_records" not in st.session_state:
    st.session_state["chat_records"] = [] # ts : ts, Q: query, A: answer
    load_jsonl(file_chat_records)

st.header("Codebasics 🌱")

c1, c2, c3 = st.columns([5,3,3])
with c1:
    btn_create = st.button("Create Knowledgebase")
    if btn_create:
        create_vector_db()

with c2:
    btn_save = st.button("Save chats")
    if btn_save:
        dump_jsonl(file_chat_records)

with c3:
    btn_clear = st.button("Clear chat history")
    if btn_clear:
        st.session_state["chat_records"] = []

def update_chat_records(ts, rag_query, answer):
    rec = st.session_state.get("chat_records")
    rec.append({"ts": ts,  "Q": rag_query, "A": answer})
    st.session_state["chat_records"] = rec


st.subheader("Q&A")

chain = create_rag_chain(llm_provider="Ollama")

rag_query = st.text_input("Ask me question: ", value="", key="key_rag_query")
c_1, _, c_2, _ = st.columns(4)
with c_1:
    submit = st.button("Submit")
with c_2:
    clear = st.button("Clear")

if rag_query and submit:
    ts1 = time()
    answer = chain.invoke(rag_query)
    ts2 = time()

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"### Answer: \t\t [took {(ts2-ts1):.3f} sec]")
    st.write(answer)
    update_chat_records(ts, rag_query, answer)

if clear:
    st.session_state["rag_query"] = ""

if "chat_records" in st.session_state and len(st.session_state["chat_records"]):
    st.subheader("Chat History")
    chats = st.session_state["chat_records"]
    st.write(chats)













