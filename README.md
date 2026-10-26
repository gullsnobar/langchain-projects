# LangChain Projects Portfolio

This repository contains two separate, fully functional AI applications built with LangChain, running entirely on local models via **Ollama** (no paid API keys required).

## Projects

### 1. [RAG Pipeline](./rag-pipeline/)
A retrieval-augmented generation pipeline that indexes local `.txt` documents and answers questions grounded strictly in those documents. Supports both ChromaDB and FAISS as vector stores.

*   **Tech Stack:** Python, LangChain, Ollama (`llama3.2`), ChromaDB, FAISS.
*   **Key Feature:** Grounded generation (refuses to answer if the answer is not in the document).
*   **How to run:** See the [RAG Pipeline README](./rag-pipeline/README.md).

### 2. [Semantic Book Recommender](./book-recommender/)
A semantic search engine that recommends books based on the meaning of a user's query, wrapped in a modern Gradio web interface.

*   **Tech Stack:** Python, LangChain, Ollama (`nomic-embed-text`), ChromaDB, Gradio.
*   **Key Feature:** Uses `nomic-embed-text` prefixes (`search_query:` / `search_document:`) for highly accurate similarity matching.
*   **How to run:** See the [Book Recommender README](./book-recommender/README.md).

## Prerequisites (For both projects)

1.  **Python 3.10+**
2.  **Ollama** installed and running ([download here](https://ollama.com/download)).
3.  Pull the required models:
    ```bash
    ollama pull llama3.2
    ollama pull nomic-embed-text
    ```

## Repository Structure

```text
langchain-projects/
├── rag-pipeline/          # Project 1: Document Q&A
│   ├── data/
│   ├── src/
│   ├── README.md
│   └── requirements.txt
├── book-recommender/      # Project 2: Semantic Book Search
│   ├── data/
│   ├── src/
│   ├── assets/
│   ├── app.py
│   ├── README.md
│   └── requirements.txt
└── .gitignore
```
