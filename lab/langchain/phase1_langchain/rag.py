"""A basic two-step retrieval-augmented generation pipeline."""

from langchain.chat_models import BaseChatModel
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.runnables import Runnable
from langchain_core.prompts import ChatPromptTemplate

from lab.langchain.phase1_langchain.models import InterviewAnswer


RAG_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """You are an interview preparation assistant.

Answer only from the retrieved context below. Do not use outside knowledge.
If the context does not directly support an answer:
- say that the interview notes do not contain enough information,
- set insufficient_context to true,
- return an empty sources list,
- and use a confidence no greater than 0.2.

When context is sufficient, cite only the exact source filenames shown in it.

Retrieved context:
{context}""",
        ),
        ("human", "{question}"),
    ]
)


def build_rag_chain(
    model: BaseChatModel,
) -> Runnable[dict[str, str], InterviewAnswer]:
    """Compose the grounded prompt with Pydantic structured output."""

    structured_model = model.with_structured_output(InterviewAnswer)
    return RAG_PROMPT | structured_model


def answer_knowledge_question(
    question: str,
    retriever: BaseRetriever,
    rag_chain: Runnable[dict[str, str], InterviewAnswer],
) -> tuple[InterviewAnswer, list[Document]]:
    """Retrieve relevant notes, then generate one grounded answer."""

    # Embedding API call: consumes embedding tokens for the query.
    documents = retriever.invoke(question)
    context = format_documents(documents)

    # LLM API call: consumes the question, context, schema, and generated output.
    answer = rag_chain.invoke({"question": question, "context": context})
    if not isinstance(answer, InterviewAnswer):
        raise TypeError("The RAG chain did not return an InterviewAnswer.")

    return _filter_sources(answer, documents), documents


def format_documents(documents: list[Document]) -> str:
    """Format retrieved chunks with visible source filenames."""

    if not documents:
        return "No relevant context was retrieved."

    return "\n\n".join(
        f"Source: {document.metadata.get('source', 'unknown')}\n"
        f"{document.page_content}"
        for document in documents
    )


def _filter_sources(
    answer: InterviewAnswer,
    documents: list[Document],
) -> InterviewAnswer:
    allowed_sources = {
        str(document.metadata["source"])
        for document in documents
        if "source" in document.metadata
    }
    sources: list[str] = []

    for source in answer.sources:
        if source in allowed_sources and source not in sources:
            sources.append(source)

    if answer.insufficient_context:
        sources = []

    return answer.model_copy(update={"sources": sources})
