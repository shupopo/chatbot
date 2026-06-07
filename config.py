import os
from dotenv import load_dotenv

load_dotenv()

def get_setting(name: str):
    value = os.getenv(name)
    if value:
        return value

    try:
        import streamlit as st
        return st.secrets.get(name)
    except Exception:
        return None

# OpenAI設定
OPENAI_API_KEY = get_setting("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.7

# Supabase設定
SUPABASE_URL = get_setting("SUPABASE_URL")
SUPABASE_SERVICE_KEY = get_setting("SUPABASE_SERVICE_KEY")

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
