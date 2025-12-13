from typing import Literal
from pydantic import BaseModel, Field, SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
import os
from dotenv import find_dotenv, load_dotenv

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
        self.llm = ChatOpenAI(
            temperature=0,
            model=chat_model,
            api_key=SecretStr(api_key),
            base_url=base_url
        ) # 用 mini 足够了，速度快
        self.structured_llm = self.llm.with_structured_output(RouteDecision)

        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """
            You are the **Gatekeeper** of the Echo-Board system.
            Your job is to route the user's input to the correct department.

            # Departments
            1. **Finance Execution (CFO)**:
               - Keywords: "spend", "bought", "cost", "balance", "how much money", "record this".
               - Intent: The user wants to perform a database write operation (accounting) or a precise database query.
               - Example: "I just spent $50 on KFC." -> finance_execution
               - Example: "What's my bank balance?" -> finance_execution

            2. **Board Advisory (Board Meeting)**:
               - Keywords: "should I", "feeling", "anxious", "analyze", "review", "plan".
               - Intent: The user needs advice, synthesis, debate, or reflection.
               - Example: "I feel guilty about spending $50 on KFC." -> board_advisory (Needs coaching, not just recording)
               - Example: "Can I afford a new iPhone?" -> board_advisory (Needs Strategist ROI analysis + CFO data)

            # Tie-Breaker
            If the query involves BOTH numbers and feelings/advice, route to **Board Advisory**. The Board can call the CFO if needed later.

            # Output Format
            IMPORTANT: You must return a valid JSON object (not a string, not an array) with exactly these two fields:
            
            "intent": "finance_execution" or "board_advisory",
            "reasoning": "your explanation here"

            Do NOT use brackets like [finance_execution]. Return a proper JSON object.
            """),
            ("user", "User Input: {query}")
        ])

    def decide(self, query: str) -> str:
        """
        返回 'finance_execution' 或 'board_advisory'
        """
        chain = self.prompt | self.structured_llm
        print(f"🚦 [Router] Query 开始执行路由决策: {query}")
        result = chain.invoke({"query": query})
        print(f"🚦 [Router] 路由决策结果: {result}")
        print(f"🚦 [Router] Routing to: {result.intent} (Reason: {result.reasoning})")
        return result.intent
