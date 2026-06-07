import streamlit as st
import os
from datetime import datetime
import config

# ページ設定
st.set_page_config(
    page_title=config.APP_TITLE,
    page_icon="🤖",
    layout="wide"
)

# CSS スタイル
st.markdown("""
<style>
.chat-message {
    padding: 1rem;
    border-radius: 10px;
    margin-bottom: 1rem;
    display: flex;
    flex-direction: column;
    color: #1a1a1a;
}
.user-message {
    background-color: #d0e8ff;
    border-left: 4px solid #2196f3;
}
.bot-message {
    background-color: #e8d5f5;
    border-left: 4px solid #9c27b0;
}
.rag-mode {
    background-color: #c8e6c9;
    border-left: 4px solid #4caf50;
}
.agent-mode {
    background-color: #ffe0b2;
    border-left: 4px solid #ff9800;
}
.source-info {
    background-color: #e0e0e0;
    padding: 0.5rem;
    border-radius: 5px;
    margin-top: 0.5rem;
    font-size: 0.9rem;
    color: #1a1a1a;
}
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """セッション状態を初期化"""
    if 'chatbot' not in st.session_state:
        try:
            print("Starting ChatBot initialization...", flush=True)
            st.info("チャットボットを初期化中です...")
            from chatbot import ChatBot
            st.session_state.chatbot = ChatBot()
            print("ChatBot initialization completed.", flush=True)
        except Exception as e:
            print(f"ChatBot initialization failed: {e}", flush=True)
            st.error("チャットボットの初期化に失敗しました。")
            st.exception(e)
            st.stop()

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'uploaded_files_status' not in st.session_state:
        st.session_state.uploaded_files_status = ""

def validate_required_settings():
    """必須設定を確認"""
    missing = []
    if not config.OPENAI_API_KEY:
        missing.append("OPENAI_API_KEY")
    if not config.SUPABASE_URL:
        missing.append("SUPABASE_URL")
    if not config.SUPABASE_SERVICE_KEY:
        missing.append("SUPABASE_SERVICE_KEY")

    if missing:
        st.error(f"必須設定が不足しています: {', '.join(missing)}")
        st.info("Streamlit Cloud の App settings > Secrets に設定してください。")
        st.stop()

def display_chat_message(message, role, mode=None, sources=None, tools_used=None):
    """チャットメッセージを表示"""
    if role == "user":
        st.markdown(f"""
        <div class="chat-message user-message">
            <strong>👤 ユーザー:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)
    else:
        mode_class = ""
        mode_text = ""
        if mode == "rag":
            mode_class = "rag-mode"
            mode_text = "📚 RAGモード"
        elif mode == "agents":
            mode_class = "agent-mode"
            mode_text = "🔧 Agentsモード"
        else:
            mode_class = "bot-message"
            mode_text = "🤖 チャットボット"

        st.markdown(f"""
        <div class="chat-message {mode_class}">
            <strong>{mode_text}:</strong><br>
            {message}
        </div>
        """, unsafe_allow_html=True)

        # ソース情報を表示（RAGモードの場合）
        if sources and len(sources) > 0:
            source_items = ""
            for i, source in enumerate(sources, 1):
                source_name = source['source'].replace('temp_', '')
                source_items += f"<li>{source_name}（ページ {source['page']}）</li>"

            st.markdown(f"""
            <div class="source-info">
                <strong>📄 参考文書:</strong>
                <ul style="margin: 0.3rem 0 0 0; padding-left: 1.2rem;">{source_items}</ul>
            </div>
            """, unsafe_allow_html=True)

        # 使用ツール情報を表示（Agentsモードの場合）
        if tools_used and len(tools_used) > 0:
            st.markdown(f"""
            <div class="source-info">
                <strong>🔧 使用ツール:</strong> {', '.join(tools_used)}
            </div>
            """, unsafe_allow_html=True)

def main():
    """メイン関数"""
    # ヘッダーを先に描画して、初期化待ちでもスケルトン表示のままにしない
    st.title(config.APP_TITLE)
    st.markdown(config.APP_DESCRIPTION)

    print("Validating required settings...", flush=True)
    validate_required_settings()
    print("Required settings validated.", flush=True)

    initialize_session_state()

    # サイドバー
    with st.sidebar:
        st.header("📁 文書管理")

        # システム状態表示
        status = st.session_state.chatbot.get_system_status()
        st.metric("📄 登録チャンク数", status["document_count"])

        # 登録済み文書一覧
        registered_files = st.session_state.chatbot.get_registered_files()
        if registered_files:
            with st.expander(f"📋 登録済み文書（{len(registered_files)}件）", expanded=True):
                for f in registered_files:
                    st.write(f"- {f}")

        # ファイルアップロード
        uploaded_files = st.file_uploader(
            "文書をアップロード (PDF, TXT, CSV)",
            type=['pdf', 'txt', 'csv'],
            accept_multiple_files=True,
            help="複数のファイルを同時にアップロードできます"
        )

        if uploaded_files:
            if st.button("📤 文書を登録"):
                with st.spinner("文書を処理中..."):
                    result = st.session_state.chatbot.add_documents(uploaded_files)
                    st.session_state.uploaded_files_status = result
                    st.rerun()

        # アップロード結果表示
        if st.session_state.uploaded_files_status:
            if "成功" in st.session_state.uploaded_files_status:
                st.success(st.session_state.uploaded_files_status)
            else:
                st.error(st.session_state.uploaded_files_status)

        st.divider()

        # 文書管理ボタン
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🗑️ 文書クリア"):
                result = st.session_state.chatbot.clear_documents()
                st.success(result)
                st.rerun()

        with col2:
            if st.button("💭 履歴クリア"):
                st.session_state.chat_history = []
                st.session_state.chatbot.clear_conversation_history()
                st.success("チャット履歴をクリアしました")
                st.rerun()

        st.divider()

        # 使用方法
        with st.expander("💡 使用方法"):
            st.markdown("""
            **RAGモード（文書検索）:**
            - PDFやTXTファイルをアップロード
            - アップロードした文書に関する質問をする
            - 例: "働き方改革の基本的な考え方は？"

            **Agentsモード（計算・ツール）:**
            - 数学的計算や特殊な処理
            - 例: "320の15%は？", "√25は？"

            **対応ファイル形式:**
            - PDF: テキスト抽出可能なPDF
            - TXT: プレーンテキスト
            - CSV: 表形式データ
            """)

    # メインチャットエリア
    st.header("💬 チャット")

    # チャット履歴表示
    chat_container = st.container()
    with chat_container:
        for chat in st.session_state.chat_history:
            display_chat_message(
                chat["user_message"],
                "user"
            )
            display_chat_message(
                chat["bot_response"],
                "bot",
                chat.get("mode"),
                chat.get("sources"),
                chat.get("tools_used")
            )

    # ユーザー入力
    with st.form("chat_form", clear_on_submit=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            user_input = st.text_input(
                "質問を入力してください...",
                placeholder="例: 320の15%は？ または アップロードした文書について質問",
                label_visibility="collapsed"
            )

        with col2:
            submitted = st.form_submit_button("送信", use_container_width=True)

    # メッセージ処理
    if submitted and user_input:
        # ユーザーメッセージを履歴に追加
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with st.spinner("回答を生成中..."):
            # チャットボットの応答を取得
            response = st.session_state.chatbot.process_query(user_input)

            # チャット履歴に追加
            chat_entry = {
                "timestamp": timestamp,
                "user_message": user_input,
                "bot_response": response["answer"],
                "mode": response["mode"],
                "sources": response.get("sources", []),
                "tools_used": response.get("tools_used", [])
            }

            st.session_state.chat_history.append(chat_entry)

        # ページを再読み込みして新しいメッセージを表示
        st.rerun()

    # フッター
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        🤖 生成AIチャットボット powered by LangChain & OpenAI<br>
        RAG + Agents ハイブリッドシステム
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
