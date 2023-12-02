import streamlit as st
from langchain_helper import get_qa_chain, create_vector_db

from datetime import datetime
import jsonlines
from pathlib import Path

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
    st.session_state["chat_records"] = [] # ts : ts, Q: question, A: answer
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

def update_chat_records(ts, question, answer):
    rec = st.session_state.get("chat_records")
    rec.append({"ts": ts,  "Q": question, "A": answer})
    st.session_state["chat_records"] = rec
    # st.write(rec)
    # st.write(st.session_state["chat_records"])

st.subheader("Q&A")

question = st.text_input("Do you have a question? ")
if question:
    chain = get_qa_chain()
    response = chain(question)

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown("### Answer:")
    answer = response["result"]
    st.write(answer)
    update_chat_records(ts, question, answer)


if "chat_records" in st.session_state and len(st.session_state["chat_records"]):
    st.subheader("Chat History")
    chats = st.session_state["chat_records"]
    st.write(chats)













