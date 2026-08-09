"""Direct model tool calling and a simple LangChain study agent."""

from langchain.agents import create_agent
from langchain.chat_models import BaseChatModel
from langchain.messages import AIMessage, ToolMessage

from lab.langchain.phase1_langchain.tools import create_study_plan


AGENT_SYSTEM_PROMPT = """You route requests for an interview preparation assistant.

If the user asks to distribute a numeric number of topics across a numeric
number of days, call create_study_plan exactly once. After the tool returns,
present the result clearly as Day 1, Day 2, and so on.

For every other request, do not answer from your own knowledge and do not call
a tool. Reply with exactly: KNOWLEDGE_QUESTION
"""


def request_study_plan_tool_call(
    model: BaseChatModel,
    question: str,
) -> AIMessage:
    """Ask a tool-bound model whether it wants to call the study-plan tool."""

    model_with_tools = model.bind_tools([create_study_plan])

    # LLM API call: returns a requested tool call but does not execute the tool.
    response = model_with_tools.invoke(question)
    if not isinstance(response, AIMessage):
        raise TypeError(f"Expected AIMessage, received {type(response).__name__}.")
    return response


def run_study_agent(
    model: BaseChatModel,
    question: str,
) -> tuple[str, bool]:
    """Run the agent and report its final text and whether a tool executed."""

    agent = create_agent(
        model=model,
        tools=[create_study_plan],
        system_prompt=AGENT_SYSTEM_PROMPT,
    )

    # LLM API calls: the agent may call the model before and after tool execution.
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]}
    )
    messages = result["messages"]
    tool_called = any(isinstance(message, ToolMessage) for message in messages)

    for message in reversed(messages):
        if isinstance(message, AIMessage) and message.text.strip():
            return message.text.strip(), tool_called

    raise RuntimeError("The study agent did not return a final text response.")
