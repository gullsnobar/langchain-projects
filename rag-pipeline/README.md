# RAG Pipeline (ChromaDB + FAISS, local Ollama)

A retrieval-augmented generation pipeline that indexes local `.txt` documents and answers questions grounded strictly in those documents. Uses LangChain, Ollama (`llama3.2` + `nomic-embed-text`), and supports ChromaDB or FAISS as the vector store.

## What it does

- Loads every `.txt` file from `data/`
- Splits them into overlapping chunks (~500 characters)
- Embeds the chunks with `nomic-embed-text` (local, no API key needed)
- Stores vectors in ChromaDB by default, or FAISS via config
- Answers questions using `llama3.2`, restricted to retrieved context (no hallucination)

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running (https://ollama.com/download)
3. Pull the two required models (once):

   ```bash
   ollama pull llama3.2
   ollama pull nomic-embed-text
   ```

## Quick start

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Confirm Ollama is running
ollama list

# 4. Build the vector index from your documents
python -c "from src.loaders import load_documents; from src.splitter import split_documents; from src.vectorstores import build_store; build_store(split_documents(load_documents()))"

# 5. Ask a question
python -m src.cli "What is artificial intelligence?"
```

## Usage

Ask a question:

```bash
python -m src.cli "Your question here"
```

Show the retrieved chunks used to build the answer (useful for debugging retrieval):

```bash
python -m src.cli "Your question here" --show-chunks
```

## Switch vector store

Set the `VECTOR_STORE` value in `.env` to `faiss` (default is `chroma`), rebuild the index, then query.

## Example output

```
> python -m src.cli "What is artificial intelligence?"

=== ANSWER ===
Artificial intelligence (AI) is a branch of computer science focused on
developing systems capable of performing tasks that normally require human
intelligence, such as understanding natural language, recognizing images,
solving problems, making decisions, and learning from data.

=== SOURCES ===
- data\sample.txt
```

Out-of-scope question — the model refuses rather than inventing:

```
> python -m src.cli "What is the capital of France?"

=== ANSWER ===
I don't know based on the provided documents.

=== SOURCES ===
- data\sample.txt
```

## Project structure

```
rag-pipeline/
├── data/                  # Your source documents (.txt)
├── src/
│   ├── config.py          # Env-driven settings (model names, chunk size, top-K)
│   ├── loaders.py         # Load .txt files as LangChain Documents
│   ├── splitter.py        # Chunk documents into overlapping pieces
│   ├── embeddings.py      # Ollama embedding model factory
│   ├── vectorstores.py    # Chroma + FAISS build/load helpers
│   ├── chain.py           # Retrieval + grounded generation
│   └── cli.py             # Command-line entrypoint
├── .env.example
├── requirements.txt
└── README.md
```

## Configuration (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `VECTOR_STORE` | `chroma` | `chroma` or `faiss` |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local Ollama server |
| `CHAT_MODEL` | `llama3.2` | Chat model for answer generation |
| `EMBEDDING_MODEL` | `nomic-embed-text` | Embedding model for chunks and queries |

Chunk size, overlap, and top-K are set in `src/config.py`.

## Author

Gull Snobar — [GitHub](https://github.com/gullsnobar)