from typing import Dict, Any
from langchain.agents import AgentType, initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from .tools import ToolManager
import config

class AgentManager:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.MODEL_NAME,
            temperature=config.TEMPERATURE
        )
        self.tool_manager = ToolManager()
        self.tools = self.tool_manager.get_tools()

        # メモリの初期化
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )

        # エージェントの初期化
        self.agent = initialize_agent(
            tools=self.tools,
            llm=self.llm,
            agent=AgentType.CHAT_CONVERSATIONAL_REACT_DESCRIPTION,
            verbose=True,
            memory=self.memory,
            handle_parsing_errors=True
        )

    def process_query(self, query: str) -> Dict[str, Any]:
        """エージェントを使用してクエリを処理"""
        try:
            response = self.agent.run(query)
            return {
                "answer": response,
                "is_agent_response": True,
                "tools_used": self._extract_tools_used(response)
            }
        except Exception as e:
            return {
                "answer": f"エージェント処理中にエラーが発生しました: {str(e)}",
                "is_agent_response": True,
                "tools_used": []
            }

    def is_agent_query(self, query: str) -> bool:
        """クエリがエージェント処理を必要とするかを判定"""
        return self.tool_manager.is_math_query(query)

    def _extract_tools_used(self, response: str) -> list:
        """レスポンスから使用されたツールを抽出"""
        tools_used = []
        if "Calculator" in response or "計算" in response:
            tools_used.append("Calculator")
        return tools_used

    def clear_memory(self):
        """会話履歴をクリア"""
        self.memory.clear()

    def get_memory(self) -> str:
        """現在の会話履歴を取得"""
        return str(self.memory.buffer)