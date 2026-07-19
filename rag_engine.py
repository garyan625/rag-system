from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found")
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
)

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
)

from langchain_google_genai import (
    ChatGoogleGenerativeAI,
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
def create_rag_chain():
    print("\nLoading documents...")

    loader = DirectoryLoader(
        "documents",
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    documents = loader.load()

    print(f"Loaded {len(documents)} pages")

    # ==========================================
    # 3. CHUNK DOCUMENTS
    # ==========================================

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(documents)

    print(f"Created {len(chunks)} chunks")

    # ==========================================
    # 4. EMBEDDING MODEL
    # ==========================================

    print("\nLoading embedding model...")

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    # ==========================================
    # 5. CREATE / LOAD FAISS
    # ==========================================

    INDEX_PATH = "faiss_index"

    if os.path.exists(INDEX_PATH):

        print("Loading existing FAISS index...")

        vectorstore = FAISS.load_local(
            INDEX_PATH,
            embeddings,
            allow_dangerous_deserialization=True
        )

    else:

        print("Creating FAISS index...")

        vectorstore = FAISS.from_documents(
            chunks,
            embeddings
        )

        vectorstore.save_local(INDEX_PATH)

        print("FAISS index saved")

    # ==========================================
    # 6. GEMINI MODEL
    # ==========================================

    print("\nUsing Gemini 2.5 Flash")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0
    )

    # ==========================================
    # 7. MEMORY
    # ==========================================

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True,
        output_key="answer"
    )

    # ==========================================
    # 8. RETRIEVER
    # ==========================================

    retriever = vectorstore.as_retriever(
        search_kwargs={"k": 3}
    )

    # ==========================================
    # 9. CONVERSATIONAL RAG CHAIN
    # ==========================================

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        return_source_documents=True
    )
    return qa_chain

def get_qa_chain():
    return create_rag_chain()


def create_vector_store():
    loader = DirectoryLoader(
        "documents",
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )

    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )

    chunks = splitter.split_documents(docs)

    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vector_store = FAISS.from_documents(
        chunks,
        embeddings
    )

    vector_store.save_local("faiss_index")  
