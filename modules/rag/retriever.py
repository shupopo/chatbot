from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.docstore.document import Document
from .vector_store import VectorStore
from .document_processor import DocumentProcessor
import config

class RAGRetriever:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.MODEL_NAME,
            temperature=config.TEMPERATURE
        )
        self.vector_store = VectorStore()
        self.document_processor = DocumentProcessor()

    def add_documents(self, uploaded_files) -> str:
        """アップロードされたファイルを処理してベクトルストアに追加"""
        if not uploaded_files:
            return "ファイルが選択されていません。"

        all_documents = []
        processed_files = []

        for uploaded_file in uploaded_files:
            try:
                documents = self.document_processor.process_uploaded_file(uploaded_file)
                all_documents.extend(documents)
                processed_files.append(uploaded_file.name)
            except Exception as e:
                return f"ファイル {uploaded_file.name} の処理中にエラーが発生しました: {str(e)}"

        if all_documents:
            try:
                self.vector_store.create_vector_store(all_documents)
                self.vector_store.save_vector_store()
                return f"成功: {len(processed_files)}個のファイルを処理し、{len(all_documents)}個のチャンクを作成しました。\\n処理されたファイル: {', '.join(processed_files)}"
            except Exception as e:
                return f"ベクトルストア作成中にエラーが発生しました: {str(e)}"
        else:
            return "処理可能なコンテンツが見つかりませんでした。"

    def load_existing_documents(self) -> bool:
        """既存のベクトルストアを読み込み"""
        return self.vector_store.load_vector_store()

    def retrieve_and_generate(self, query: str) -> Dict[str, Any]:
        """RAGを使用して質問に回答"""
        # ベクトルストアが空の場合
        if self.vector_store.vector_store is None:
            return {
                "answer": "資料に該当箇所が見当たりません。まず文書をアップロードしてください。",
                "sources": [],
                "is_rag_response": False
            }

        # 関連文書を検索
        relevant_docs = self.vector_store.similarity_search_with_score(query)

        if not relevant_docs:
            return {
                "answer": "資料に該当箇所が見当たりません。",
                "sources": [],
                "is_rag_response": True
            }

        # 関連文書のコンテンツを結合
        context = ""
        sources = []

        for doc, score in relevant_docs:
            context += f"\\n\\n【出典: {doc.metadata.get('source', '不明')} - ページ{doc.metadata.get('page', '不明')}】\\n"
            context += doc.page_content
            sources.append({
                "source": doc.metadata.get('source', '不明'),
                "page": doc.metadata.get('page', '不明'),
                "score": score
            })

        # プロンプトを作成
        system_prompt = """あなたは親切なアシスタントです。提供された文書の内容のみを基に、正確に質問に答えてください。

重要な指示:
1. 提供された文書の内容のみを使用して回答してください
2. 文書に記載されていない情報は推測しないでください
3. 不明な点がある場合は、「資料に該当箇所が見当たりません」と答えてください
4. 回答の根拠となる文書名とページ番号を明記してください"""

        user_prompt = f"""以下の文書を参考に質問に答えてください:

【参考文書】
{context}

【質問】
{query}

【回答】"""

        try:
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ]

            response = self.llm(messages)
            answer = response.content

            return {
                "answer": answer,
                "sources": sources,
                "is_rag_response": True
            }

        except Exception as e:
            return {
                "answer": f"回答生成中にエラーが発生しました: {str(e)}",
                "sources": [],
                "is_rag_response": True
            }

    def get_document_count(self) -> int:
        """保存されている文書数を取得"""
        return self.vector_store.get_document_count()

    def clear_documents(self) -> str:
        """全ての文書をクリア"""
        self.vector_store.clear_vector_store()
        return "全ての文書がクリアされました。"