import os
import pandas as pd
from typing import List, Dict, Any
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
import config

class DocumentProcessor:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            length_function=len,
        )

    def process_pdf(self, file_path: str) -> List[Document]:
        """PDFファイルを処理してDocumentオブジェクトのリストを返す"""
        documents = []
        try:
            reader = PdfReader(file_path)
            filename = os.path.basename(file_path)

            for page_num, page in enumerate(reader.pages):
                text = page.extract_text()
                if text.strip():
                    doc = Document(
                        page_content=text,
                        metadata={
                            "source": filename,
                            "page": page_num + 1,
                            "file_type": "pdf"
                        }
                    )
                    documents.append(doc)
        except Exception as e:
            print(f"PDF処理中にエラーが発生しました: {e}")

        return self._split_documents(documents)

    def process_txt(self, file_path: str) -> List[Document]:
        """TXTファイルを処理してDocumentオブジェクトのリストを返す"""
        documents = []
        try:
            filename = os.path.basename(file_path)
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": filename,
                        "page": 1,
                        "file_type": "txt"
                    }
                )
                documents.append(doc)
        except Exception as e:
            print(f"TXT処理中にエラーが発生しました: {e}")

        return self._split_documents(documents)

    def process_csv(self, file_path: str) -> List[Document]:
        """CSVファイルを処理してDocumentオブジェクトのリストを返す"""
        documents = []
        try:
            filename = os.path.basename(file_path)
            df = pd.read_csv(file_path)

            # CSVの各行をテキストとして変換
            for index, row in df.iterrows():
                text_content = "\n".join([f"{col}: {row[col]}" for col in df.columns])
                doc = Document(
                    page_content=text_content,
                    metadata={
                        "source": filename,
                        "page": index + 1,
                        "file_type": "csv",
                        "row_index": index
                    }
                )
                documents.append(doc)
        except Exception as e:
            print(f"CSV処理中にエラーが発生しました: {e}")

        return self._split_documents(documents)

    def _split_documents(self, documents: List[Document]) -> List[Document]:
        """文書を指定されたチャンクサイズに分割"""
        return self.text_splitter.split_documents(documents)

    def process_uploaded_file(self, uploaded_file) -> List[Document]:
        """Streamlitでアップロードされたファイルを処理"""
        file_extension = uploaded_file.name.split('.')[-1].lower()

        # 一時ファイルとして保存
        temp_file_path = f"./data/temp_{uploaded_file.name}"
        os.makedirs(os.path.dirname(temp_file_path), exist_ok=True)

        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        try:
            if file_extension == 'pdf':
                documents = self.process_pdf(temp_file_path)
            elif file_extension == 'txt':
                documents = self.process_txt(temp_file_path)
            elif file_extension == 'csv':
                documents = self.process_csv(temp_file_path)
            else:
                raise ValueError(f"サポートされていないファイル形式: {file_extension}")

            return documents
        finally:
            # 一時ファイルを削除
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)