from langchain_ollama import OllamaEmbeddings
from src.config import EMBEDDING_MODEL, OLLAMA_BASE_URL


def get_embeddings():
    """Return an Ollama embedding model pointed at the local server."""
    return OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL,
    )