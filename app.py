import os
import shutil
import streamlit as st

from rag_engine import (
    get_qa_chain,
    create_vector_store
)

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="RAG PDF Assistant",
    page_icon="📚",
    layout="wide"
)

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None

# ==========================================
# CREATE DOCUMENT DIRECTORY
# ==========================================

os.makedirs("documents", exist_ok=True)

# ==========================================
# TITLE
# ==========================================

st.title("📚 PDF Chat Assistant")
st.markdown("Upload PDFs and ask questions about them.")

# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_files = st.file_uploader(
    "Upload PDF Files",
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

        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        uploaded_count += 1

    st.success(
        f"{uploaded_count} PDF(s) uploaded successfully!"
    )

# ==========================================
# PROCESS DOCUMENTS
# ==========================================

if st.button("Process Documents"):

    try:

        pdf_files = [
            f for f in os.listdir("documents")
            if f.endswith(".pdf")
        ]

        if len(pdf_files) == 0:
            st.warning(
                "Please upload at least one PDF."
            )
            st.stop()

        if os.path.exists("faiss_index"):
            shutil.rmtree("faiss_index")

        with st.spinner(
            "Creating vector database..."
        ):
            create_vector_store()

        with st.spinner(
            "Creating QA chain..."
        ):
            st.session_state.qa_chain = get_qa_chain()

        if st.session_state.qa_chain is None:
            st.error(
                "QA chain creation failed."
            )
        else:
            st.success(
                "Documents processed successfully!"
            )

    except Exception as e:

        st.error(
            f"Processing Error:\n\n{str(e)}"
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
        st.info(
            "No PDFs uploaded yet."
        )

# ==========================================
# DISPLAY CHAT HISTORY
# ==========================================

for message in st.session_state.messages:

    with st.chat_message(
        message["role"]
    ):
        st.markdown(
            message["content"]
        )

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

        if st.session_state.qa_chain is None:

            final_response = (
                "⚠️ Please upload PDFs and click "
                "'Process Documents' first."
            )

        else:

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

                source = os.path.basename(
                    doc.metadata.get(
                        "source",
                        "Unknown"
                    )
                )

                page = (
                    doc.metadata.get(
                        "page",
                        0
                    ) + 1
                )

                citation = (
                    f"{source} (Page {page})"
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
            "❌ Error while querying documents:\n\n"
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
