import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.7

# Supabase設定
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# RAG設定
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_DOCUMENTS = 3

# Streamlit設定
APP_TITLE = "LangChain RAGチャットボット"
APP_DESCRIPTION = """
LangChain + Supabase (pgvector) を使用したRAGチャットボットです。
PDFをアップロードすると、文書の内容に基づいて質問に回答します。
"""