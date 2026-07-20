import os
import streamlit as st
from dotenv import load_dotenv

from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from langchain_groq import (
    ChatGroq,
)

from langchain_huggingface import (
    HuggingFaceEmbeddings,
)

from langchain_community.vectorstores import (
    FAISS,
)

from langchain_classic.memory import (
    ConversationBufferMemory,
)

from langchain_classic.chains import (
    ConversationalRetrievalChain,
)

load_dotenv()

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")


# ==========================================
# CREATE RAG CHAIN
# ==========================================

def create_rag_chain(document_path, index_path):

    print("\nLoading documents...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ==========================================
    # LOAD EXISTING FAISS INDEX
    # ==========================================

    if os.path.exists(index_path):

        print("Loading FAISS index...")

        vectorstore = FAISS.load_local(
            index_path,
            embeddings,
            allow_dangerous_deserialization=True
        )

    else:

        print("FAISS index not found.")

        return None

    # ==========================================
    # GEMINI MODEL
    # ==========================================

    llm = ChatGroq(
        groq_api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0
    )

    # ==========================================
    # MEMORY
    # ==========================================

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # ==========================================
    # RETRIEVER
    # ==========================================

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    # ==========================================
    # QA CHAIN
    # ==========================================

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )

    return qa_chain


# ==========================================
# GET QA CHAIN
# ==========================================

def get_qa_chain(document_path, index_path):

    try:
        return create_rag_chain(
            document_path,
            index_path
        )

    except Exception as e:

        print(
            "QA CHAIN ERROR:",
            str(e)
        )

        return None


# ==========================================
# CREATE VECTOR STORE
# ==========================================

def create_vector_store(document_path, index_path):

    loader = DirectoryLoader(
        document_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    docs = loader.load()

    if len(docs) == 0:
        raise Exception(
            "No PDF documents found."
        )

    print(
        f"Loaded {len(docs)} pages"
    )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(
        docs
    )

    print(
        f"Created {len(chunks)} chunks"
    )

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    os.makedirs(
        os.path.dirname(index_path),
        exist_ok=True
    )

    vector_store.save_local(
        index_path
    )

    print(
        f"FAISS saved to {index_path}"
    )
