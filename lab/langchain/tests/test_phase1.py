from langchain_core.documents import Document
from langchain_core.embeddings import DeterministicFakeEmbedding
from langchain_core.runnables import RunnableLambda

from lab.langchain.phase1_langchain.knowledge import build_vector_store
from lab.langchain.phase1_langchain.models import InterviewAnswer
from lab.langchain.phase1_langchain.rag import answer_knowledge_question
from lab.langchain.phase1_langchain.tools import create_study_plan


def test_study_plan_distributes_remainder() -> None:
    daily_topics = create_study_plan.invoke(
        {"total_topics": 17, "available_days": 5}
    )

    assert daily_topics == [4, 4, 3, 3, 3]
    assert sum(daily_topics) == 17
    assert max(daily_topics) - min(daily_topics) <= 1


def test_unrelated_question_returns_insufficient_context() -> None:
    document = Document(
        page_content="FastAPI validates request data with Pydantic models.",
        metadata={"source": "fastapi.md"},
    )
    vector_store = build_vector_store(
        [document],
        DeterministicFakeEmbedding(size=32),
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 1})

    def fake_structured_model(inputs: dict[str, str]) -> InterviewAnswer:
        question = inputs["question"].lower()
        context = inputs["context"].lower()
        insufficient = "sourdough" in question and "sourdough" not in context
        return InterviewAnswer(
            answer="The interview notes do not contain enough information.",
            sources=[],
            confidence=0.05,
            insufficient_context=insufficient,
        )

    rag_chain = RunnableLambda(fake_structured_model)
    answer, retrieved_documents = answer_knowledge_question(
        "How do I maintain a sourdough starter?",
        retriever,
        rag_chain,
    )

    assert retrieved_documents[0].metadata["source"] == "fastapi.md"
    assert answer.insufficient_context is True
    assert answer.sources == []
    assert answer.confidence <= 0.2
