from langchain.tools import Tool
from langchain.chains import LLMMathChain
from langchain.chat_models import ChatOpenAI
import config
import re

class MathTool:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=config.OPENAI_API_KEY,
            model_name=config.MODEL_NAME,
            temperature=0
        )
        self.llm_math = LLMMathChain.from_llm(self.llm)

    def calculate(self, query: str) -> str:
        """数学的計算を実行"""
        try:
            result = self.llm_math.run(query)
            return f"計算結果: {result}"
        except Exception as e:
            return f"計算エラー: {str(e)}"

class ToolManager:
    def __init__(self):
        self.math_tool = MathTool()

    def get_tools(self):
        """利用可能なツールのリストを返す"""
        return [
            Tool(
                name="Calculator",
                func=self.math_tool.calculate,
                description="""数学的計算を実行するツールです。
                以下のような計算に使用できます:
                - 基本的な四則演算 (足し算、引き算、掛け算、割り算)
                - パーセント計算
                - 平方根、累乗
                - 三角関数

                使用例:
                - "320の15%は？" → "320 * 0.15"
                - "√25" → "sqrt(25)"
                - "2の3乗" → "2**3"
                """
            )
        ]

    def is_math_query(self, query: str) -> bool:
        """クエリが数学的計算を必要とするかを判定"""
        math_patterns = [
            r'\d+\s*[+\-*/]\s*\d+',  # 基本的な演算
            r'\d+\s*の\s*\d+%',       # パーセント計算
            r'\d+%',                  # パーセント
            r'計算|足し算|引き算|掛け算|割り算|％|パーセント|平方根|累乗|√',
            r'[+\-*/=]',             # 演算記号
            r'\d+\s*\+\s*\d+',       # 足し算
            r'\d+\s*-\s*\d+',        # 引き算
            r'\d+\s*×\s*\d+',        # 掛け算
            r'\d+\s*÷\s*\d+',        # 割り算
        ]

        for pattern in math_patterns:
            if re.search(pattern, query):
                return True

        return False