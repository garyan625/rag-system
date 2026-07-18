import os
from dotenv import load_dotenv

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

from langchain_community.vectorstores import FAISS

from langchain_classic.memory import (
    ConversationBufferMemory,
)

from langchain_classic.chains import (
    ConversationalRetrievalChain,
)

# ==========================================
# 1. ENVIRONMENT VARIABLES
# ==========================================

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

os.environ["GOOGLE_API_KEY"] = api_key

# ==========================================
# 2. LOAD DOCUMENTS
# ==========================================


# ==========================================
# 10. CHAT LOOP
# ==========================================

print("\nRAG System Ready")
print("Type 'exit' to quit\n")

while True:

    query = input("Ask a question: ")

    if query.lower() == "exit":
        print("\nGoodbye!")
        break

    try:

        result = qa_chain.invoke(
            {"question": query}
        )

        print("\n" + "=" * 70)

        print("\nAnswer:\n")
        print(result["answer"])

        print("\nSources Used:\n")

        seen = set()

        for doc in result["source_documents"]:

            source = os.path.basename(
                doc.metadata.get("source", "Unknown")
            )

            page = doc.metadata.get("page", 0)

            citation = f"{source} (Page {page + 1})"

            if citation not in seen:
                seen.add(citation)
                print(f"[{len(seen)}] {citation}")

        print("\nRetrieved Evidence:\n")

        for i, doc in enumerate(
            result["source_documents"],
            start=1
        ):

            source = os.path.basename(
                doc.metadata.get("source", "Unknown")
            )

            page = doc.metadata.get("page", 0)

            preview = (
                doc.page_content[:200]
                .replace("\n", " ")
            )

            print(
                f"[{i}] {source} | Page {page + 1}"
            )

            print(preview)
            print()

        print("=" * 70)

    except Exception as e:

        print("\nError:")
        print(str(e))