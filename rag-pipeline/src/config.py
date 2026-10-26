import os
from dotenv import load_dotenv

load_dotenv()

VECTOR_STORE = os.getenv("VECTOR_STORE", "chroma")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
TOP_K = 3