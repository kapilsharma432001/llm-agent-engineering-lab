"""Chat-model setup, structured output, and model invocation examples."""

from collections.abc import Iterator

from langchain.chat_models import BaseChatModel, init_chat_model
from langchain.embeddings import init_embeddings
from langchain.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.embeddings import Embeddings
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from lab.langchain.src.config import CHAT_MODEL, EMBEDDING_MODEL


class InterviewAnswer(BaseModel):
    """A grounded answer produced from the interview notes."""

    answer: str = Field(description="The answer supported by the retrieved notes.")
    sources: list[str] = Field(
        description="Source filenames that directly support the answer."
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence that the retrieved notes support the answer.",
    )
    insufficient_context: bool = Field(
        description="True when the retrieved notes cannot answer the question."
    )


DEMO_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an interview coach. Explain the concept in at most two sentences.",
        ),
        ("human", "{question}"),
    ]
)


def create_chat_model() -> BaseChatModel:
    """Initialize the configured chat model without making an API call."""

    return init_chat_model(CHAT_MODEL)


def create_embedding_model() -> Embeddings:
    """Initialize the configured embedding model without making an API call."""

    return init_embeddings(EMBEDDING_MODEL)


def build_message_history(question: str) -> list[BaseMessage]:
    """Build an example conversation with system, human, and AI messages."""

    return [
        SystemMessage("You are a concise interview coach."),
        HumanMessage("Which subjects can you help me study?"),
        AIMessage("I can help with Python, FastAPI, and system design."),
        HumanMessage(question),
    ]


def invoke_message_example(model: BaseChatModel, question: str) -> AIMessage:
    """Call a model synchronously with explicit message objects."""

    # LLM API call: consumes input and output tokens.
    response = model.invoke(build_message_history(question))
    return _require_ai_message(response)


async def ainvoke_prompt_example(
    model: BaseChatModel,
    question: str,
) -> AIMessage:
    """Call a prompt-and-model chain asynchronously."""

    chain = DEMO_PROMPT | model

    # LLM API call: consumes input and output tokens.
    response = await chain.ainvoke({"question": question})
    return _require_ai_message(response)


def stream_prompt_example(
    model: BaseChatModel,
    question: str,
) -> Iterator[str]:
    """Yield text chunks from a prompt-and-model chain."""

    chain = DEMO_PROMPT | model

    # LLM API call: consumes input and output tokens as chunks are generated.
    for chunk in chain.stream({"question": question}):
        if chunk.text:
            yield chunk.text


def _require_ai_message(message: BaseMessage) -> AIMessage:
    if not isinstance(message, AIMessage):
        raise TypeError(f"Expected AIMessage, received {type(message).__name__}.")
    return message
