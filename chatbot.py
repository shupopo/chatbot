from typing import Dict, Any
from modules.rag.retriever import RAGRetriever
from modules.agents.agent import AgentManager
import config

class ChatBot:
    def __init__(self):
        self.rag_retriever = RAGRetriever()
        self.agent_manager = AgentManager()

        # 既存の文書を読み込み
        self.rag_retriever.load_existing_documents()

    def process_query(self, query: str) -> Dict[str, Any]:
        """
        クエリを処理し、適切なモード（RAGまたはAgents）を自動選択
        """
        # 空のクエリチェック
        if not query.strip():
            return {
                "answer": "質問を入力してください。",
                "mode": "none",
                "sources": [],
                "tools_used": []
            }

        # エージェント処理が必要かチェック（計算など）
        if self.agent_manager.is_agent_query(query):
            result = self.agent_manager.process_query(query)
            return {
                "answer": result["answer"],
                "mode": "agents",
                "sources": [],
                "tools_used": result.get("tools_used", [])
            }

        # RAG処理を試行
        rag_result = self.rag_retriever.retrieve_and_generate(query)

        # RAGで回答が見つからない場合は、一般的な対話として処理
        if not rag_result.get("is_rag_response") or "資料に該当箇所が見当たりません" in rag_result["answer"]:
            # 文書がない場合は、エージェントで一般的な質問として処理
            if self.rag_retriever.get_document_count() == 0:
                general_result = self.agent_manager.process_query(query)
                return {
                    "answer": general_result["answer"],
                    "mode": "agents",
                    "sources": [],
                    "tools_used": general_result.get("tools_used", [])
                }
            else:
                return {
                    "answer": rag_result["answer"],
                    "mode": "rag",
                    "sources": rag_result.get("sources", []),
                    "tools_used": []
                }

        # RAGで適切な回答が見つかった場合
        return {
            "answer": rag_result["answer"],
            "mode": "rag",
            "sources": rag_result.get("sources", []),
            "tools_used": []
        }

    def add_documents(self, uploaded_files) -> str:
        """文書をRAGシステムに追加"""
        return self.rag_retriever.add_documents(uploaded_files)

    def clear_documents(self) -> str:
        """全ての文書をクリア"""
        return self.rag_retriever.clear_documents()

    def get_document_count(self) -> int:
        """保存されている文書数を取得"""
        return self.rag_retriever.get_document_count()

    def clear_conversation_history(self):
        """会話履歴をクリア"""
        self.agent_manager.clear_memory()

    def get_system_status(self) -> Dict[str, Any]:
        """システムの状態を取得"""
        return {
            "document_count": self.get_document_count(),
            "rag_available": self.rag_retriever.vector_store.vector_store is not None,
            "agents_available": len(self.agent_manager.tools) > 0
        }