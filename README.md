# LLM Agent Engineering Lab

This is a learning repository for building an Interview Preparation
Multi-Agent Assistant one phase at a time.

Phase 1 focuses only on LangChain fundamentals and a small retrieval-augmented
generation (RAG) application. It does not use LangGraph directly, MCP, RAGAS, a
web API, a database, or a frontend.

## What Phase 1 demonstrates

- Initializing chat and embedding models
- System, human, and AI messages
- Prompt templates and prompt/model composition
- Synchronous, asynchronous, batch, and streaming model concepts
- Pydantic structured output
- LangChain documents and text splitting
- Embeddings, an in-memory vector store, and a retriever
- A two-step RAG pipeline
- LangChain tools and direct model tool calling
- A simple LangChain agent

## Setup

The project requires Python 3.12 or later.

```bash
python3.12 -m venv venv
source venv/bin/activate
python -m pip install -r requirements.txt
```

The `.env` file belongs in the repository root, beside this README:

```text
llm-agent-engineering-lab/
├── .env
├── README.md
├── requirements.txt
├── knowledge/
└── src/
```

Create it from the committed template:

```bash
cp .env.example .env
```

Then replace the placeholder value:

```dotenv
OPENAI_API_KEY=your-real-api-key
INTERVIEW_CHAT_MODEL=openai:gpt-5.6-luna
INTERVIEW_EMBEDDING_MODEL=openai:text-embedding-3-small
```

The real `.env` file is ignored by Git and must not be committed.

## Run the CLI

Pass a question directly:

```bash
python -m src.phase1_langchain.main \
  "How does FastAPI dependency injection work?"
```

Or run without a positional question and enter it at the prompt:

```bash
python -m src.phase1_langchain.main
```

Show the retrieved chunks for a knowledge question:

```bash
python -m src.phase1_langchain.main \
  "What is the difference between threading and multiprocessing?" \
  --debug
```

Study-planning example:

```bash
python -m src.phase1_langchain.main \
  "I have 17 topics and 5 days. Create a study plan."
```

The CLI first lets the study agent decide whether to call the planning tool. If
no tool executes, the question is sent through the two-step RAG pipeline.

```text
Question
   |
   v
Study agent ---- tool called ----> Python study-plan function ----> answer
   |
   no tool
   |
   v
retrieve note chunks ----> grounded structured model call ----> answer + sources
```

## Model invocation examples

The main CLI uses synchronous invocation. The focused helpers in
`src/phase1_langchain/models.py` make the three invocation styles easy
to compare. Each helper below makes a separate billable model call.

```python
import asyncio

from src.phase1_langchain.models import (
    ainvoke_prompt_example,
    create_chat_model,
    invoke_message_example,
    stream_prompt_example,
)

model = create_chat_model()

response = invoke_message_example(model, "Explain Python generators.")
print(response.text)

async_response = asyncio.run(
    ainvoke_prompt_example(model, "Explain dependency injection.")
)
print(async_response.text)

for text in stream_prompt_example(model, "Explain a message queue."):
    print(text, end="", flush=True)
```

Direct model tool calling is visible separately from the agent:

```python
from src.phase1_langchain.agent import request_study_plan_tool_call
from src.phase1_langchain.models import create_chat_model

model = create_chat_model()
response = request_study_plan_tool_call(
    model,
    "Distribute 12 topics over 4 days.",
)
print(response.tool_calls)
```

This direct call only returns the model's requested tool call. The
`create_agent` path used by the CLI also executes the tool, adds its
`ToolMessage`, calls the model again, and returns a final response.

## LangChain concepts

### What LangChain adds over calling a provider directly

A provider SDK can send input to one provider and return its response. LangChain
adds shared message types, a common model interface, prompt templates, runnable
composition, document and retrieval abstractions, structured-output helpers,
tool schemas, and an agent loop. These abstractions make it easier to connect the
same kinds of components and to change a provider without rewriting all
application code.

The trade-off is another abstraction layer. Provider-specific features may
appear later in LangChain, errors can be harder to trace, and a small application
may not need the extra dependency.

### Message versus prompt

A message is one item in a chat conversation. It has a role, content, and
optional metadata. A `SystemMessage` supplies behavior instructions, a
`HumanMessage` represents user input, and an `AIMessage`
represents model output or requested tool calls.

A prompt is the full input prepared for a model. It may be a plain string, a
list of concrete messages, or a template that creates messages after variables
are supplied. `ChatPromptTemplate` is reusable; a message is already
concrete.

### How prompt | model composition works

LangChain components implement the Runnable interface. The `|` operator
creates a sequence: the prompt template receives a dictionary, formats it into
messages, and passes those messages to the model. Building the sequence makes no
API call. Tokens are consumed only when a method such as `invoke` runs
the sequence.

In this project, the RAG chain is:

```python
structured_model = model.with_structured_output(InterviewAnswer)
rag_chain = RAG_PROMPT | structured_model
```

### invoke, ainvoke, batch, and stream

- `invoke(input)` waits for one complete result.
- `ainvoke(input)` is the awaitable form used by async Python code.
- `batch(inputs)` processes several independent inputs, normally with
  client-side concurrency, and returns complete results.
- `stream(input)` returns an iterator of message chunks as output is
  generated.

These methods share the Runnable interface. They describe how work is executed,
not a different prompt or model.

### Structured output

`with_structured_output(InterviewAnswer)` tells the model integration
to return data matching the Pydantic schema. LangChain converts the schema to
the provider's supported format, parses the response, and validates it.
Application code receives an `InterviewAnswer` instead of manually
parsing a free-form JSON string.

Structured output makes the shape predictable, but it does not guarantee that
the answer is factually correct. The grounding prompt and retrieval quality still
matter.

### Provider-native versus tool-based structured output

Provider-native structured output sends a JSON schema through a provider feature
that constrains the generated response. This is generally the most reliable
option when the selected provider and model support it. The default OpenAI model
in this project supports structured outputs.

Tool-based structured output represents the schema as a tool definition and
asks the model to call that artificial tool with valid arguments. LangChain then
parses the arguments as the result. It is useful when a provider supports tool
calling but does not provide native schema-constrained output.

The artificial structured-output tool should not be confused with
`create_study_plan`, which executes real Python logic.

### What a Document contains

A LangChain `Document` contains:

- `page_content`: the text used for splitting, embedding, and prompting.
- `metadata`: application data such as the source filename.
- an optional identifier.

The Markdown loader in this project is normal Python file I/O. Wrapping the text
in `Document` is LangChain functionality. The splitter copies the
filename metadata into each chunk.

### How chunking affects retrieval

Large chunks preserve more surrounding explanation but can mix unrelated topics
and consume more prompt tokens. Small chunks are more focused but can separate a
claim from the context needed to understand it. Overlap repeats boundary text so
an idea split near an edge is less likely to disappear.

Phase 1 uses 700 characters with 100 characters of overlap. These are learning
defaults, not universal optimum values. Retrieval evaluation should determine
production chunk settings.

### What an embedding represents

An embedding is a vector of numbers produced from text. The vector captures
semantic features learned by the embedding model. Texts with related meanings
should be closer under a similarity measure even when they do not share exact
words.

The numbers are not human-readable facts. They are coordinates used for
comparison. Indexing embeds every chunk; retrieval embeds the question and
compares that query vector with the stored vectors.

### Vector store versus retriever

The vector store owns vectors, documents, and similarity search. This project
uses `InMemoryVectorStore`, so all data disappears when the process
ends.

A retriever is the narrower question-to-documents interface. It accepts a text
query and returns `Document` objects. A vector store can create a
retriever with `as_retriever`, but retrievers can also use non-vector
techniques.

### What happens during a tool call

1. LangChain converts the decorated tool's name, docstring, and typed arguments
   into a schema and gives it to the model.
2. The model returns an `AIMessage` containing a tool-call name and
   arguments.
3. The agent matches the name to the registered tool and validates the arguments.
4. The normal Python function executes.
5. Its result is wrapped in a `ToolMessage` with the matching call ID.
6. The updated message history is sent to the model for a final answer.

Steps 2 and 6 consume model tokens. The arithmetic inside
`create_study_plan` does not.

### Chain versus agent

A chain follows a fixed flow chosen by the programmer. The RAG chain always
retrieves first and generates second, which makes its behavior and maximum model
calls predictable.

An agent lets a model choose an action. The study agent decides whether to call
`create_study_plan`; `create_agent` manages the model/tool
loop. This flexibility adds cost and another possible failure point.

### Why a Python function is not automatically an LLM tool

Python can call any function whose name it knows. A model cannot inspect or
execute an arbitrary local function. It needs a serialized name, description,
and argument schema, plus application code that validates the requested call,
executes the function, and returns the result. The `@tool` decorator
creates that LangChain tool contract.

## Normal Python versus LangChain

| Operation | Type |
| --- | --- |
| Read Markdown with `pathlib` | Normal Python |
| Calculate the study-plan remainder with `divmod` | Normal Python |
| Parse CLI arguments and print output | Normal Python |
| Filter source names against retrieved metadata | Normal Python |
| Load `.env` values | `python-dotenv`, not LangChain |
| Create `Document` and message objects | LangChain |
| Split documents | LangChain text splitter |
| Initialize model integrations | LangChain |
| Embed text and search vectors | LangChain interfaces plus the provider |
| Compose `prompt | model` | LangChain Runnable functionality |
| Turn a function into a tool | LangChain `@tool` |
| Run the model/tool loop | LangChain `create_agent` |

## LLM calls and token consumption

| Location | What happens | Tokens |
| --- | --- | --- |
| `models.invoke_message_example` | Synchronous chat-model call | Chat input and output |
| `models.ainvoke_prompt_example` | Async prompt/model call | Chat input and output |
| `models.stream_prompt_example` | Streaming prompt/model call | Chat input and output |
| `knowledge.build_vector_store` | Embeds every knowledge chunk | Embedding input |
| `rag.answer_knowledge_question`: retriever | Embeds the question, then performs local similarity search | Embedding input for the query |
| `rag.answer_knowledge_question`: RAG chain | Generates the structured grounded answer | Chat input and output |
| `agent.request_study_plan_tool_call` | Model decides whether to request a tool | Chat input and output |
| `agent.run_study_agent` | Agent calls the model before and usually after a tool | Chat input and output for each model call |

Model and embedding initialization do not consume tokens. Creating messages,
formatting prompts, loading and splitting files, constructing the in-memory
store, calculating cosine similarity, running `divmod`, and executing
the study tool do not consume LLM tokens.

For a knowledge question, the current learning flow normally uses one model call
for agent routing, one query-embedding call, and one model call for the RAG
answer. Starting a new CLI process also embeds all knowledge chunks. A valid
study-planning request normally uses two agent model calls and no embeddings.

## Failure modes

- The API key can be missing, invalid, or unauthorized for a selected model.
- Provider requests can time out, be rate-limited, or fail temporarily.
- The in-memory index is rebuilt and all chunks are embedded on every CLI run.
- Poor chunk size or embeddings can retrieve the wrong context.
- Dense retrieval always returns the nearest chunks even when they are unrelated.
  The model is responsible for marking them insufficient in this phase.
- The model can misroute a planning request or fail to request the tool.
- Structured-output generation can fail schema validation or be refused.
- The model can assign inaccurate confidence; it is not a measured probability.
- Source filtering removes invented filenames but cannot prove that every answer
  sentence is supported.
- Invalid study-plan arguments raise a normal Python `ValueError`.
- In-memory data disappears when the process exits.

## When LangChain would be unnecessary

LangChain may be unnecessary for one provider call with a fixed prompt and no
retrieval, tools, structured output, or provider switching. A provider SDK plus a
small Python function would be easier to debug and maintain in that case. Use a
framework when its shared interfaces and composition remove more code than they
add.

## Seven code sections to review manually

1. `src/config.py` and model initialization in `models.py`.
2. Message objects and `invoke`/`ainvoke`/`stream`
   helpers in `models.py`.
3. Markdown loading and source metadata in `knowledge.py`.
4. Splitting, embeddings, vector storage, and retriever creation in
   `knowledge.py`.
5. The grounded prompt, Pydantic schema, and `prompt | model`
   composition in `rag.py`.
6. The remainder calculation in `tools.py` and direct
   `bind_tools` example in `agent.py`.
7. The `create_agent` loop and agent-first CLI routing in
   `agent.py` and `main.py`.

## Tests

The repository intentionally contains only two Phase 1 unit tests:

```bash
pytest -q
```

- Correct remainder distribution for 17 topics over 5 days.
- Insufficient context for an unrelated sourdough question.

The tests use deterministic fake embeddings and a fake structured runnable. They
do not need an API key and never make a real model call.

## Official references

- [LangChain models](https://docs.langchain.com/oss/python/langchain/models)
- [LangChain messages](https://docs.langchain.com/oss/python/langchain/messages)
- [LangChain retrieval](https://docs.langchain.com/oss/python/langchain/retrieval)
- [LangChain tools](https://docs.langchain.com/oss/python/langchain/tools)
- [LangChain agents](https://docs.langchain.com/oss/python/langchain/agents)
- [OpenAI embeddings integration](https://docs.langchain.com/oss/python/integrations/embeddings/openai)
- [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna)

Phase 1 stops here. LangGraph orchestration, MCP, and RAGAS belong to later
phases.
