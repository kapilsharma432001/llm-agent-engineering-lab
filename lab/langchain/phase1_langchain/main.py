"""Command-line entry point for the Phase 1 assistant."""

import argparse
import os
from collections.abc import Sequence

from langchain_core.documents import Document

from lab.langchain.src.config import CHAT_MODEL, EMBEDDING_MODEL
from lab.langchain.phase1_langchain.agent import run_study_agent
from lab.langchain.phase1_langchain.knowledge import build_retriever
from lab.langchain.phase1_langchain.models import (
    InterviewAnswer,
    create_chat_model,
    create_embedding_model,
)
from lab.langchain.phase1_langchain.rag import (
    answer_knowledge_question,
    build_rag_chain,
)


def parse_args(arguments: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask a Phase 1 interview-preparation question."
    )
    parser.add_argument(
        "question",
        nargs="?",
        help="A knowledge question or study-planning request.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print the chunks retrieved for a knowledge question.",
    )
    return parser.parse_args(arguments)


def main(arguments: Sequence[str] | None = None) -> int:
    args = parse_args(arguments)
    question = (args.question or input("Question: ")).strip()

    if not question:
        print("A non-empty question is required.")
        return 2

    if _openai_key_is_missing():
        print(
            "OPENAI_API_KEY is not set. Copy .env.example to .env and add your key."
        )
        return 2

    model = create_chat_model()
    agent_answer, tool_called = run_study_agent(model, question)

    if tool_called:
        _print_result(
            answer=agent_answer,
            sources=[],
            tool_called=True,
            rag_answer=None,
            documents=[],
            debug=args.debug,
        )
        return 0

    embeddings = create_embedding_model()
    retriever = build_retriever(embeddings)
    rag_chain = build_rag_chain(model)
    rag_answer, documents = answer_knowledge_question(
        question,
        retriever,
        rag_chain,
    )
    _print_result(
        answer=rag_answer.answer,
        sources=rag_answer.sources,
        tool_called=False,
        rag_answer=rag_answer,
        documents=documents,
        debug=args.debug,
    )
    return 0


def _openai_key_is_missing() -> bool:
    uses_openai = CHAT_MODEL.startswith("openai:") or EMBEDDING_MODEL.startswith(
        "openai:"
    )
    return uses_openai and not os.getenv("OPENAI_API_KEY")


def _print_result(
    *,
    answer: str,
    sources: list[str],
    tool_called: bool,
    rag_answer: InterviewAnswer | None,
    documents: list[Document],
    debug: bool,
) -> None:
    print("\nFinal answer")
    print(answer)

    print("\nSources")
    print(", ".join(sources) if sources else "None")

    print("\nTool called")
    print("Yes" if tool_called else "No")

    if rag_answer is not None:
        print("\nConfidence")
        print(f"{rag_answer.confidence:.2f}")
        print("\nInsufficient context")
        print("Yes" if rag_answer.insufficient_context else "No")

    if debug:
        print("\nRetrieved chunks")
        if not documents:
            print("None")
        for index, document in enumerate(documents, start=1):
            source = document.metadata.get("source", "unknown")
            print(f"\n[{index}] {source}")
            print(document.page_content)


if __name__ == "__main__":
    raise SystemExit(main())
