# Semantic Book Recommender (OpenAI-style embeddings via Ollama)

A semantic search engine that recommends books based on the meaning of a user's query, not just keyword matches. Built with LangChain, ChromaDB, local Ollama embeddings (`nomic-embed-text`), and a Gradio web UI.

## What it does

- Loads a CSV of books (title, author, description).
- Embeds the descriptions locally using Ollama (`nomic-embed-text`).
- Stores the vectors in ChromaDB.
- Provides a Gradio UI where you can describe a mood, plot, or theme.
- Returns the most semantically similar books.

## Prerequisites

1. **Python 3.10+** installed
2. **Ollama** installed and running (https://ollama.com/download)
3. Pull the embedding model (once):

   ```bash
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

# 3. Build the vector index (only needed once)
python -c "from src.data import load_books; from src.indexer import build_book_index; build_book_index(load_books())"

# 4. Launch the web app
python app.py
```

Open the URL printed in the terminal (usually `http://127.0.0.1:7860`).

## Screenshot

![Gradio UI](assets/gradio_ui.png)

## Project structure

```
book-recommender/
├── app.py                 # Entry point to launch Gradio
├── data/
│   └── books_sample.csv   # Sample dataset (10 books)
├── src/
│   ├── config.py          # Settings (model names, top-K)
│   ├── data.py            # Loads and preps the CSV
│   ├── indexer.py         # Embeds descriptions and saves to Chroma
│   ├── recommender.py     # Similarity search and mapping back to books
│   └── ui.py              # Gradio UI layout
├── .env.example
├── requirements.txt
└── README.md
```

## How it works

1. We prepend the book's ISBN to its description before embedding (e.g., `9780141439518 A classic novel...`).
2. The vector store indexes this text. When a user searches, we prepend `search_query: ` to their prompt.
3. The database returns chunks. We extract the ISBN from the first word of each chunk.
4. We look up those ISBNs in the original DataFrame to return the full book details.

## Author

Gull — [GitHub](https://github.com/gullsnobar)