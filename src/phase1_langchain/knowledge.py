"""Load, split, embed, and retrieve the local interview notes."""

from pathlib import Path

from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_core.retrievers import BaseRetriever
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    KNOWLEDGE_DIRECTORY,
    RETRIEVER_K,
)


def load_knowledge_documents(
    directory: Path = KNOWLEDGE_DIRECTORY,
) -> list[Document]:
    """Load Markdown files and preserve each filename as source metadata."""

    paths = sorted(directory.glob("*.md"))
    if not paths:
        raise FileNotFoundError(f"No Markdown knowledge files found in {directory}.")

    return [
        Document(
            page_content=path.read_text(encoding="utf-8"),
            metadata={"source": path.name},
        )
        for path in paths
    ]


def split_documents(documents: list[Document]) -> list[Document]:
    """Split documents into overlapping chunks for retrieval."""

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        add_start_index=True,
    )
    return splitter.split_documents(documents)


def build_vector_store(
    documents: list[Document],
    embeddings: Embeddings,
) -> InMemoryVectorStore:
    """Embed documents and store their vectors in memory."""

    if not documents:
        raise ValueError("At least one document is required to build the vector store.")

    vector_store = InMemoryVectorStore(embedding=embeddings)

    # Embedding API call: consumes embedding input tokens for every chunk.
    vector_store.add_documents(documents=documents)
    return vector_store


def build_retriever(embeddings: Embeddings) -> BaseRetriever:
    """Build a retriever over the local Markdown knowledge base."""

    documents = load_knowledge_documents()
    chunks = split_documents(documents)
    vector_store = build_vector_store(chunks, embeddings)
    return vector_store.as_retriever(search_kwargs={"k": RETRIEVER_K})
