from typing import List, Tuple
import requests
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
import config

REQUEST_TIMEOUT_SECONDS = 10

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        self.base_url = f"{config.SUPABASE_URL}/rest/v1"
        self.headers = {
            "apikey": config.SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {config.SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

    def _request(self, method, path, **kwargs):
        url = f"{self.base_url}{path}"
        kwargs.setdefault("timeout", REQUEST_TIMEOUT_SECONDS)
        resp = requests.request(method, url, headers=self.headers, **kwargs)
        resp.raise_for_status()
        return resp

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

        self._request("POST", "/documents", json=rows)

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
        resp = self._request("POST", "/rpc/match_documents", json={
            "query_embedding": query_embedding,
            "match_count": k,
        })
        return resp.json()

    def get_document_count(self) -> int:
        try:
            headers = {**self.headers, "Prefer": "count=exact"}
            resp = requests.get(
                f"{self.base_url}/documents?select=id",
                headers=headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            content_range = resp.headers.get("content-range", "")
            if "/" in content_range:
                total = content_range.split("/")[1]
                return int(total) if total != "*" else 0
            return len(resp.json())
        except Exception as e:
            print(f"ドキュメント数取得中にエラーが発生しました: {e}")
            return 0

    def get_registered_files(self) -> List[str]:
        try:
            resp = requests.get(
                f"{self.base_url}/documents?select=metadata",
                headers=self.headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
            resp.raise_for_status()
            sources = set()
            for row in resp.json():
                name = row.get("metadata", {}).get("source", "")
                if name:
                    sources.add(name.replace("temp_", ""))
            return sorted(sources)
        except Exception as e:
            print(f"ファイル一覧取得中にエラーが発生しました: {e}")
            return []

    def clear_vector_store(self) -> None:
        try:
            requests.delete(
                f"{self.base_url}/documents?id=neq.0",
                headers=self.headers,
                timeout=REQUEST_TIMEOUT_SECONDS,
            ).raise_for_status()
        except Exception as e:
            print(f"ベクトルストアクリア中にエラーが発生しました: {e}")
