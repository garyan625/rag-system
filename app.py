import os
import shutil
import streamlit as st

# ==========================================
# PAGE CONFIG (MUST BE FIRST STREAMLIT CALL)
# ==========================================

st.set_page_config(
    page_title="RAG PDF Assistant",
    page_icon="📚",
    layout="wide"
)

from rag_engine import (
    get_qa_chain,
    create_vector_store
)

# ==========================================
# CACHE QA CHAIN
# ==========================================

@st.cache_resource
def load_chain():
    return get_qa_chain()

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []
os.makedirs("documents", exist_ok=True)
if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# ==========================================
# TITLE
# ==========================================

st.title("📚 PDF Chat Assistant")
st.markdown("Upload PDFs and ask questions about them.")

# ==========================================
# DOCUMENT DIRECTORY
# ==========================================



# ==========================================
# PDF UPLOAD
# ==========================================

uploaded_files = st.file_uploader(
    "Upload PDF files",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    uploaded_count = 0

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            "documents",
            uploaded_file.name
        )

        if not os.path.exists(file_path):

            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            uploaded_count += 1

        else:
            st.warning(
                f"{uploaded_file.name} already exists."
            )

    if uploaded_count > 0:
        st.success(
            f"{uploaded_count} PDF(s) uploaded successfully!"
        )

# ==========================================
# PROCESS DOCUMENTS
# ==========================================

if st.button("Process Documents"):

    try:

        if os.path.exists("faiss_index"):
            shutil.rmtree("faiss_index")

        with st.spinner(
            "Creating embeddings and FAISS index..."
        ):
            create_vector_store()

        load_chain.clear()

        st.session_state.qa_chain = load_chain()

        st.success(
            "Documents processed successfully!"
        )

    except Exception as e:

        st.error(
            f"Error while processing documents:\n{str(e)}"
        )

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.header("📄 Uploaded Documents")

    pdf_files = [
        f for f in os.listdir("documents")
        if f.endswith(".pdf")
    ]

    st.metric(
        "Total PDFs",
        len(pdf_files)
    )

    if pdf_files:

        for file in pdf_files:
            st.write("📄", file)

    else:
        st.info("No PDFs uploaded yet.")

# ==========================================
# CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# ==========================================
# CHAT INPUT
# ==========================================

prompt = st.chat_input(
    "Ask a question about your PDFs..."
)

if prompt:

    with st.chat_message("user"):
        st.markdown(prompt)

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    try:

        with st.spinner(
            "Searching documents..."
        ):

            result = (
                st.session_state.qa_chain.invoke(
                    {
                        "question": prompt
                    }
                )
            )

        answer = result["answer"]

        sources_text = "\n\n### Sources\n"

        seen = set()

        for doc in result["source_documents"]:

            source = doc.metadata.get(
                "source",
                "Unknown"
            )

            page = doc.metadata.get(
                "page",
                0
            )

            citation = (
                f"{os.path.basename(source)} "
                f"(Page {page + 1})"
            )

            if citation not in seen:

                seen.add(citation)

                sources_text += (
                    f"- {citation}\n"
                )

        final_response = (
            answer + sources_text
        )

    except Exception as e:

        final_response = (
            f"❌ Error while querying documents:\n\n"
            f"{str(e)}"
        )

    with st.chat_message("assistant"):
        st.markdown(final_response)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final_response
        }
    )
