from langchain_chroma import Chroma
from langchain_community.vectorstores import FAISS
from src.config import VECTOR_STORE
from src.embeddings import get_embeddings

CHROMA_DIR = "chroma_db"
FAISS_DIR = "faiss_index"


def build_store(chunks, store_type: str = None):
    """Embed chunks and store them in the chosen vector store."""
    store_type = (store_type or VECTOR_STORE).lower()
    embeddings = get_embeddings()

    if store_type == "chroma":
        return Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=CHROMA_DIR,
        )
    elif store_type == "faiss":
        store = FAISS.from_documents(chunks, embeddings)
        store.save_local(FAISS_DIR)
        return store
    else:
        raise ValueError(f"Unknown VECTOR_STORE: {store_type}. Use 'chroma' or 'faiss'.")


def load_store(store_type: str = None):
    """Load the persisted vector store from disk."""
    store_type = (store_type or VECTOR_STORE).lower()
    embeddings = get_embeddings()

    if store_type == "chroma":
        return Chroma(
            persist_directory=CHROMA_DIR,
            embedding_function=embeddings,
        )
    elif store_type == "faiss":
        return FAISS.load_local(
            FAISS_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )
    else:
        raise ValueError(f"Unknown VECTOR_STORE: {store_type}. Use 'chroma' or 'faiss'.")