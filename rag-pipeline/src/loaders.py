from pathlib import Path
from langchain_community.document_loaders import TextLoader


def load_documents(data_dir: str = "data"):
    """Load every .txt file in data_dir as LangChain Document objects."""
    documents = []
    for path in Path(data_dir).glob("*.txt"):
        loader = TextLoader(str(path), encoding="utf-8")
        documents.extend(loader.load())
    if not documents:
        raise FileNotFoundError(f"No .txt files found in {data_dir}/")
    return documents