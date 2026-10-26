import pandas as pd
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from src.config import EMBEDDING_MODEL, OLLAMA_BASE_URL, CHROMA_DIR, COLLECTION_NAME, TOP_K

def recommend_books(query: str, df, k: int = TOP_K):
    """Find semantically similar books based on a query."""
    
    embeddings = OllamaEmbeddings(
        model=EMBEDDING_MODEL,
        base_url=OLLAMA_BASE_URL
    )
    
    vectorstore = Chroma(
        persist_directory=CHROMA_DIR,
        embedding_function=embeddings,
        collection_name=COLLECTION_NAME
    )
    
    # Prepend the search_query prefix manually
    prefixed_query = "search_query: " + query
    
    results = vectorstore.similarity_search(prefixed_query, k=k)
    
    # Extract ISBNs from results, remembering they start with "search_document: "
    # Example: "search_document: 9780141439518 A classic novel..."
    # We split by space and take the 2nd element (index 1) to get the ISBN.
    matched_isbns = [doc.page_content.split()[1] for doc in results]
    
    # Build the DataFrame in the SAME order as the search results
    ordered_rows = []
    for isbn in matched_isbns:
        row = df[df["isbn13"] == isbn]
        if not row.empty:
            ordered_rows.append(row.iloc[0])
    
    recommended_df = pd.DataFrame(ordered_rows).reset_index(drop=True)
    return recommended_df[["title", "authors", "description"]]