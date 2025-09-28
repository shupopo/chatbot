import os
from dotenv import load_dotenv

load_dotenv()

# OpenAI設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-3.5-turbo"
TEMPERATURE = 0.7

# RAG設定
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
TOP_K_DOCUMENTS = 3

# ベクトルDB設定
VECTOR_STORE_PATH = "./data/vector_store"

# Streamlit設定
APP_TITLE = "生成AIチャットボット（RAG + Agents）"
APP_DESCRIPTION = """
このチャットボットは以下の機能を提供します：
- **RAGモード**: アップロードされた文書から情報を検索して回答
- **Agentsモード**: 計算や外部ツールを使用した処理
"""