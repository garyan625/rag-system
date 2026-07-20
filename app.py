import os
import shutil
import requests
import streamlit as st

from auth import (
    oauth2,
    GOOGLE_REDIRECT_URI
)

from rag_engine import (
    get_qa_chain,
    create_vector_store
)

from chat_history import (
    save_message,
    load_chat_history
)
# ==========================================
# PAGE CONFIG
# ==========================================

# ==========================================
# PAGE CONFIG
# ==========================================

st.set_page_config(
    page_title="RAG PDF Assistant",
    page_icon="📚",
    layout="wide"
)

if "user" not in st.session_state:
    st.session_state.user = None

# ==========================================
# GOOGLE LOGIN
# ==========================================

if st.session_state.user is None:

    st.title("🔐 Login")

    result = oauth2.authorize_button(
        "Continue with Google",
        GOOGLE_REDIRECT_URI,
        scope="openid email profile",
        icon="https://www.google.com.tw/favicon.ico",
        key="google_oauth",
        use_container_width=True,
    )
    st.write("OAuth Result:", result)

    if result and "token" in result:

        access_token = result["token"]["access_token"]

        userinfo = requests.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={
                "Authorization":
                f"Bearer {access_token}"
            },
        ).json()

        st.session_state.user = {
            "email": userinfo["email"],
            "localId": userinfo["sub"],
            "displayName": userinfo.get(
                "name",
                ""
            ),
        }

        st.rerun()

    st.stop()

# ==========================================
# SESSION STATE
# ==========================================

if "messages" not in st.session_state:
    st.session_state.messages = []
if "history_loaded" not in st.session_state:
    st.session_state.history_loaded = False

if "qa_chain" not in st.session_state:
    st.session_state.qa_chain = None


# ==========================================
# USER DIRECTORIES
# ==========================================

user_email = (
    st.session_state.user["email"]
    .replace("@", "_")
    .replace(".", "_")
)

DOCUMENT_DIR = f"documents/{user_email}"
INDEX_DIR = f"faiss_indexes/{user_email}"

os.makedirs(DOCUMENT_DIR, exist_ok=True)
os.makedirs(INDEX_DIR, exist_ok=True)

# ==========================================
# LOAD CHAT HISTORY
# ==========================================

if not st.session_state.history_loaded:

    st.session_state.messages = load_chat_history(
        st.session_state.user["email"]
    )

    st.session_state.history_loaded = True

# ==========================================
# LOAD EXISTING INDEX
# ==========================================

if (
    st.session_state.qa_chain is None
    and os.path.isdir(INDEX_DIR)
    and len(os.listdir(INDEX_DIR)) > 0
):
    try:

        st.session_state.qa_chain = (
            get_qa_chain(
                document_path=DOCUMENT_DIR,
                index_path=INDEX_DIR
            )
        )

    except Exception:
        pass

# ==========================================
# MAIN UI
# ==========================================

st.title("📚 PDF Chat Assistant")

st.markdown(
    f"Welcome **{st.session_state.user['displayName']}**"
)

# ==========================================
# FILE UPLOAD
# ==========================================

uploaded_files = st.file_uploader(
    "Upload PDFs",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    uploaded_count = 0

    for uploaded_file in uploaded_files:

        file_path = os.path.join(
            DOCUMENT_DIR,
            uploaded_file.name
        )

        if not os.path.exists(file_path):

            with open(file_path, "wb") as f:
                f.write(
                    uploaded_file.getbuffer()
                )

            uploaded_count += 1

    if uploaded_count > 0:

        st.success(
            f"{uploaded_count} PDF(s) uploaded"
        )

# ==========================================
# PROCESS DOCUMENTS
# ==========================================

if st.button("Process Documents"):

    try:

        pdf_files = [
            f for f in os.listdir(
                DOCUMENT_DIR
            )
            if f.endswith(".pdf")
        ]

        if not pdf_files:

            st.warning(
                "Upload PDFs first."
            )

        else:

            if os.path.exists(INDEX_DIR):
                shutil.rmtree(INDEX_DIR)

            create_vector_store(
                document_path=DOCUMENT_DIR,
                index_path=INDEX_DIR
            )

            st.session_state.qa_chain = (
                get_qa_chain(
                    document_path=DOCUMENT_DIR,
                    index_path=INDEX_DIR
                )
            )

            st.success(
                "Documents processed."
            )

    except Exception as e:

        st.error(str(e))

# ==========================================
# SIDEBAR
# ==========================================

with st.sidebar:

    st.success(
        st.session_state.user["email"]
    )

    st.header("Uploaded PDFs")

    pdf_files = [
        f for f in os.listdir(DOCUMENT_DIR)
        if f.endswith(".pdf")
    ]

    st.metric(
        "Total PDFs",
        len(pdf_files)
    )

    for pdf in pdf_files:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write("📄", pdf)

        with col2:

            if st.button(
                "❌",
                key=f"delete_{pdf}"
            ):

                try:

                    pdf_path = os.path.join(
                        DOCUMENT_DIR,
                        pdf
                    )

                    if os.path.exists(pdf_path):
                        os.remove(pdf_path)

                    # Remove old index
                    if os.path.exists(INDEX_DIR):
                        shutil.rmtree(INDEX_DIR)

                    remaining_pdfs = [
                        f for f in os.listdir(
                            DOCUMENT_DIR
                        )
                        if f.endswith(".pdf")
                    ]

                    if remaining_pdfs:

                        create_vector_store(
                            document_path=DOCUMENT_DIR,
                            index_path=INDEX_DIR
                        )

                        st.session_state.qa_chain = (
                            get_qa_chain(
                                document_path=DOCUMENT_DIR,
                                index_path=INDEX_DIR
                            )
                        )

                    else:

                        st.session_state.qa_chain = None

                    st.success(
                        f"{pdf} deleted successfully"
                    )

                    st.rerun()

                except Exception as e:

                    st.error(
                        f"Delete failed: {e}"
                    )
    if st.button("➕ New Chat"):
        st.session_state.messages = []
        st.session_state.history_loaded = True
        st.rerun()

    if st.button("Logout"):

        st.session_state.user = None
        st.session_state.messages = []
        st.session_state.qa_chain = None
        st.session_state.qa_chain = None
        st.session_state.history_loaded = False
        st.rerun()
# ==========================================
# CHAT HISTORY
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
    "Ask about your PDFs..."
)

if prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt
        }
    )

    save_message(
        st.session_state.user["email"],
        "user",
        prompt
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    try:

        if st.session_state.qa_chain is None:

            final_response = (
                "⚠️ Process documents first."
            )

        else:

            result = (
                st.session_state.qa_chain.invoke(
                    {
                        "question": prompt
                    }
                )
            )

            answer = result["answer"]

            sources = []

            for doc in result[
                "source_documents"
            ]:

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

                sources.append(
                    f"{source} (Page {page})"
                )

            sources = list(set(sources))

            final_response = answer

            if sources:

                final_response += (
                    "\n\n### Sources\n"
                )

                for src in sources:

                    final_response += (
                        f"- {src}\n"
                    )

    except Exception as e:

        final_response = str(e)

    with st.chat_message(
        "assistant"
    ):
        st.markdown(
            final_response
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": final_response
        }
    )

    save_message(
        st.session_state.user["email"],
        "assistant",
        final_response
    )
