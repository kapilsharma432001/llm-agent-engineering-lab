"""Configuration for the Interview Preparation Assistant."""

import os
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

CHAT_MODEL = os.getenv("INTERVIEW_CHAT_MODEL", "openai:gpt-5.6-luna")
EMBEDDING_MODEL = os.getenv(
    "INTERVIEW_EMBEDDING_MODEL",
    "openai:text-embedding-3-small",
)
KNOWLEDGE_DIRECTORY = PROJECT_ROOT / "knowledge"

CHUNK_SIZE = 700
CHUNK_OVERLAP = 100
RETRIEVER_K = 4
