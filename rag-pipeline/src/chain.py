from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.config import CHAT_MODEL, OLLAMA_BASE_URL, TOP_K
from src.vectorstores import load_store

SYSTEM_PROMPT = """You are a helpful assistant answering questions strictly from the provided context.

Rules:
- Answer ONLY using the context below.
- If the answer is not in the context, reply exactly: "I don't know based on the provided documents."
- Do not use outside knowledge.
- Be concise.

Context:
{context}
"""

USER_PROMPT = "{question}"


def build_chain():
    """Return a callable that answers a question using retrieved chunks."""
    store = load_store()
    retriever = store.as_retriever(search_kwargs={"k": TOP_K})
    llm = ChatOllama(model=CHAT_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", USER_PROMPT),
    ])

    def answer(question: str) -> dict:
        docs = retriever.invoke(question)
        context = "\n\n---\n\n".join(d.page_content for d in docs)
        messages = prompt.format_messages(context=context, question=question)
        response = llm.invoke(messages)
        return {
            "answer": response.content,
            "sources": [d.metadata.get("source", "unknown") for d in docs],
            "chunks": [d.page_content for d in docs],
        }

    return answer