import json
import os
import re
from typing import Literal

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os

load_dotenv(find_dotenv())

api_key = os.getenv("OPEN_AI_API_KEY")
base_url = os.getenv("OPEN_AI_API_BASE")
chat_model = os.getenv("CHAT_MODEL")

# 定义结构化输出
class RouteDecision(BaseModel):
    intent: Literal["finance_execution", "board_advisory"] = Field(
        ...,
        description="The classification of the user's intent."
    )
    reasoning: str = Field(..., description="Why you made this decision.")

class Router:
    def __init__(self):
        if not chat_model or not api_key:
            raise ValueError("CHAT_MODEL and OPEN_AI_API_KEY must be set")
        self.llm = ChatOpenAI(
            temperature=0,
            model=chat_model,
            api_key=SecretStr(api_key),
            base_url=base_url
        )  # 用 mini 足够了，速度快

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are the **Gatekeeper** of the Echo-Board system.
            Your job is to route the user's input to the correct department.

            # Departments
            1. **Finance Execution (CFO)**:
               - Keywords: "spend", "bought", "cost", "balance", "how much money", "record this".
               - Intent: The user wants to perform a database write operation (accounting) or a precise database query.
               - Example: "I just spent $50 on KFC." -> json object: "intent": "finance_execution", "reasoning": "The user wants to record a transaction."
               - Example: "What's my bank balance?" -> json object: "intent": "finance_execution", "reasoning": "The user wants to query a balance."

            2. **Board Advisory (Board Meeting)**:
               - Keywords: "should I", "feeling", "anxious", "analyze", "review", "plan".
               - Intent: The user needs advice, synthesis, debate, or reflection.
               - Example: "I feel guilty about spending $50 on KFC." -> json object: "intent": "board_advisory", "reasoning": "The user needs coaching, not just recording."
               - Example: "Can I afford a new iPhone?" -> json object: "intent": "board_advisory", "reasoning": "The user needs Strategist ROI analysis + CFO data."

            # Tie-Breaker
            If the query involves BOTH numbers and feelings/advice, route to **Board Advisory**. The Board can call the CFO if needed later.

            # Output Format (JSON object)
            You MUST respond with ONLY a valid JSON object in this format:
            "intent": "finance_execution" | "board_advisory", "reasoning": "your reasoning here"
            Do not include any other text, explanation, or formatting outside the JSON object.
            """),
            ("user", "User Input: {query}")
        ])

    def _parse_json_from_response(self, response_text: str) -> dict:
        """
        从响应文本中提取 JSON 对象
        """
        # 尝试提取 JSON 对象（可能被代码块包裹或直接是 JSON）
        # 首先尝试查找代码块中的 JSON
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 如果没有代码块，尝试直接查找 JSON 对象
            json_match = re.search(r'\{.*?\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                json_str = response_text.strip()

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"⚠️ [Router] JSON 解析错误: {e}, 原始响应: {response_text}")
            raise ValueError(f"无法从响应中解析 JSON: {response_text}")

    def decide(self, query: str) -> str:
        """
        返回 'finance_execution' 或 'board_advisory'
        """
        chain = self.prompt | self.llm
        print(f"🚦 [Router] Query 开始执行路由决策: {query}")
        response = chain.invoke({"query": query})

        # 获取响应文本
        if hasattr(response, 'content'):
            content = response.content
            if isinstance(content, str):
                response_text = content
            elif isinstance(content, list):
                # 如果是消息列表，提取文本内容
                response_text = " ".join(str(msg) if hasattr(msg, 'content') else str(msg) for msg in content)
            else:
                response_text = str(content)
        else:
            response_text = str(response)

        # 解析 JSON
        json_data = self._parse_json_from_response(response_text)

        # 使用 Pydantic 模型验证
        result = RouteDecision(**json_data)

        print(f"🚦 [Router] 路由决策结果: {result.model_dump()}")
        print(f"🚦 [Router] Routing to: {result.intent} (Reason: {result.reasoning})")
        return result.intent
