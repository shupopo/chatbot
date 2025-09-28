import os
import pickle
from typing import List, Tuple, Optional
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain.docstore.document import Document
import config

class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(openai_api_key=config.OPENAI_API_KEY)
        self.vector_store = None
        self.documents = []

    def create_vector_store(self, documents: List[Document]) -> None:
        """文書からベクトルストアを作成"""
        if not documents:
            raise ValueError("文書が提供されていません")

        self.documents.extend(documents)

        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            # 既存のベクトルストアに文書を追加
            new_vector_store = FAISS.from_documents(documents, self.embeddings)
            self.vector_store.merge_from(new_vector_store)

    def similarity_search(self, query: str, k: int = config.TOP_K_DOCUMENTS) -> List[Document]:
        """類似度検索を実行"""
        if self.vector_store is None:
            return []

        try:
            results = self.vector_store.similarity_search(query, k=k)
            return results
        except Exception as e:
            print(f"検索中にエラーが発生しました: {e}")
            return []

    def similarity_search_with_score(self, query: str, k: int = config.TOP_K_DOCUMENTS) -> List[Tuple[Document, float]]:
        """スコア付きで類似度検索を実行"""
        if self.vector_store is None:
            return []

        try:
            results = self.vector_store.similarity_search_with_score(query, k=k)
            return results
        except Exception as e:
            print(f"検索中にエラーが発生しました: {e}")
            return []

    def save_vector_store(self, path: str = config.VECTOR_STORE_PATH) -> None:
        """ベクトルストアを保存"""
        if self.vector_store is None:
            print("保存するベクトルストアがありません")
            return

        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # FAISSインデックスを保存
            self.vector_store.save_local(path)

            # 文書メタデータを別途保存
            with open(f"{path}/documents.pkl", "wb") as f:
                pickle.dump(self.documents, f)

            print(f"ベクトルストアを {path} に保存しました")
        except Exception as e:
            print(f"ベクトルストア保存中にエラーが発生しました: {e}")

    def load_vector_store(self, path: str = config.VECTOR_STORE_PATH) -> bool:
        """保存されたベクトルストアを読み込み"""
        try:
            # ディレクトリが存在しない場合は作成
            os.makedirs(path, exist_ok=True)

            if os.path.exists(f"{path}/index.faiss"):
                self.vector_store = FAISS.load_local(path, self.embeddings, allow_dangerous_deserialization=True)

                # 文書メタデータを読み込み
                documents_path = f"{path}/documents.pkl"
                if os.path.exists(documents_path):
                    with open(documents_path, "rb") as f:
                        self.documents = pickle.load(f)

                print(f"ベクトルストアを {path} から読み込みました")
                return True
            else:
                print(f"ベクトルストアファイルが見つかりません。新しく作成されます。")
                return False
        except Exception as e:
            print(f"ベクトルストア読み込み中にエラーが発生しました: {e}")
            return False

    def get_document_count(self) -> int:
        """保存されている文書数を取得"""
        return len(self.documents)

    def clear_vector_store(self) -> None:
        """ベクトルストアをクリア"""
        self.vector_store = None
        self.documents = []
        print("ベクトルストアをクリアしました")