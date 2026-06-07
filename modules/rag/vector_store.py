from typing import List, Tuple
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
from supabase import create_client
import config

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        self.supabase = create_client(config.SUPABASE_URL, config.SUPABASE_SERVICE_KEY)

    def create_vector_store(self, documents: List[Document]) -> None:
        if not documents:
            raise ValueError("文書が提供されていません")

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        embeddings = self.embeddings.embed_documents(texts)

        rows = []
        for text, metadata, embedding in zip(texts, metadatas, embeddings):
            rows.append({
                "content": text,
                "metadata": metadata,
                "embedding": embedding,
            })

        self.supabase.table("documents").insert(rows).execute()

    def similarity_search(self, query: str, k: int = config.TOP_K_DOCUMENTS) -> List[Document]:
        results = self._search(query, k)
        return [
            Document(page_content=r["content"], metadata=r["metadata"])
            for r in results
        ]

    def similarity_search_with_score(self, query: str, k: int = config.TOP_K_DOCUMENTS) -> List[Tuple[Document, float]]:
        results = self._search(query, k)
        return [
            (Document(page_content=r["content"], metadata=r["metadata"]), r["similarity"])
            for r in results
        ]

    def _search(self, query: str, k: int) -> list:
        query_embedding = self.embeddings.embed_query(query)
        result = self.supabase.rpc("match_documents", {
            "query_embedding": query_embedding,
            "match_count": k,
        }).execute()
        return result.data or []

    def get_document_count(self) -> int:
        try:
            result = self.supabase.table("documents").select("id", count="exact").execute()
            return result.count or 0
        except Exception as e:
            print(f"ドキュメント数取得中にエラーが発生しました: {e}")
            return 0

    def get_registered_files(self) -> List[str]:
        try:
            result = self.supabase.table("documents").select("metadata").execute()
            sources = set()
            for row in result.data or []:
                name = row.get("metadata", {}).get("source", "")
                if name:
                    sources.add(name.replace("temp_", ""))
            return sorted(sources)
        except Exception as e:
            print(f"ファイル一覧取得中にエラーが発生しました: {e}")
            return []

    def clear_vector_store(self) -> None:
        try:
            self.supabase.table("documents").delete().neq("id", 0).execute()
        except Exception as e:
            print(f"ベクトルストアクリア中にエラーが発生しました: {e}")
