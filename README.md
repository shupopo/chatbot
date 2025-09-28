# 生成AIチャットボット（RAG + Agents）

LangChainを使用したRetrieval-Augmented Generation (RAG)とAgentsを組み合わせた生成AIチャットボットです。

## 機能

### 🤖 チャットボット機能
- **RAGモード**: アップロードされた文書（PDF/TXT/CSV）から情報を検索して回答
- **Agentsモード**: 数学計算や外部ツールを使用した処理
- **自動モード切替**: 質問の内容に応じて最適なモードを自動選択

### 📄 対応ファイル形式
- **PDF**: テキスト抽出可能なPDFファイル
- **TXT**: プレーンテキストファイル
- **CSV**: 表形式データ

### 🔧 利用可能ツール
- **Calculator**: 数学計算（四則演算、パーセント計算、平方根、累乗など）

## セットアップ

### 1. 必要な依存関係をインストール

```bash
pip install -r requirements.txt
```

### 2. 環境変数の設定

`.env`ファイルを作成し、OpenAI APIキーを設定：

```bash
cp .env.example .env
```

`.env`ファイルを編集：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. アプリケーションの起動

```bash
streamlit run app.py
```

## 使用方法

### RAGモード
1. サイドバーから文書（PDF/TXT/CSV）をアップロード
2. 「文書を登録」ボタンをクリック
3. アップロードした文書に関する質問を入力

例：
- "働き方改革の基本的な考え方は？"
- "この文書の要約を教えて"

### Agentsモード
数学的計算や特殊な処理が必要な質問を入力

例：
- "320の15%は？"
- "√25は？"
- "2の3乗は？"

## プロジェクト構造

```
chatbot/
├── app.py                          # Streamlitメインアプリ
├── chatbot.py                      # メインチャットボットクラス
├── config.py                       # 設定ファイル
├── requirements.txt                # 依存関係
├── .env.example                    # 環境変数テンプレート
├── modules/
│   ├── rag/                        # RAGモジュール
│   │   ├── __init__.py
│   │   ├── document_processor.py   # 文書処理
│   │   ├── vector_store.py         # ベクトルストア
│   │   └── retriever.py            # RAG検索・生成
│   └── agents/                     # Agentsモジュール
│       ├── __init__.py
│       ├── tools.py                # ツール定義
│       └── agent.py                # エージェント管理
└── data/                           # データディレクトリ
    └── vector_store/               # ベクトルストア保存場所
```

## 技術仕様

- **フレームワーク**: Streamlit
- **AI**: OpenAI GPT-3.5-turbo
- **ベクトルDB**: FAISS (オンメモリ)
- **テキスト処理**: LangChain
- **対応言語**: Python 3.10+

## 設定

`config.py`で以下の設定を変更可能：

- **MODEL_NAME**: 使用するOpenAIモデル (デフォルト: gpt-3.5-turbo)
- **TEMPERATURE**: 生成の温度パラメータ (デフォルト: 0.7)
- **CHUNK_SIZE**: 文書分割のチャンクサイズ (デフォルト: 1000)
- **TOP_K_DOCUMENTS**: 検索で取得する文書数 (デフォルト: 3)

## デプロイ

### Streamlit Community Cloud
1. GitHubにコードをプッシュ
2. Streamlit Community Cloudで新しいアプリを作成
3. 環境変数`OPENAI_API_KEY`を設定
4. デプロイ実行

## ライセンス

MIT License

## 注意事項

- OpenAI APIの使用料金が発生します
- APIキーを安全に管理してください（.envファイルをGitHubにコミットしないでください）
- 大量の文書を処理する場合はAPI使用量にご注意ください