from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from src.config import EMBEDDING_MODEL, OLLAMA_BASE_URL, CHROMA_DIR, COLLECTION_NAME

def build_book_index(df):
    """Embed book descriptions and store them in ChromaDB."""
    print(f"Embedding {len(df)} books...")
    
    # 1. Set up the embedding model
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    # 2. Convert DataFrame rows into LangChain Documents
    documents = []
    for _, row in df.iterrows():
        # Prepend the prefix manually
        text = "search_document: " + row["tagged_description"]
        doc = Document(
            page_content=text,
            metadata={"title": row["title"], "authors": row["authors"]}
        )
        documents.append(doc)
        
    # 3. Embed and store in ChromaDB
    vectorstore = Chroma.from_documents(
        documents=documents,
        embedding=embeddings,
        persist_directory=CHROMA_DIR,
        collection_name=COLLECTION_NAME
    )
    
    print("Index built successfully.")
    return vectorstore