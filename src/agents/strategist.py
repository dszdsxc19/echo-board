from src.agents.board_members import BaseBoardMember
from src.agents.prompts.strategist_prompts import STRATEGIST_SYSTEM_PROMPT

import os
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class Strategist(BaseBoardMember):
    """
    战略官：只看问题和事实，先手发言。
    """
    
    def __init__(self):
        super().__init__("Strategist", STRATEGIST_SYSTEM_PROMPT)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "User Query: {query}\n\n[Fact Context]:\n{context}\n\n[CFO's Financial Report]:\n{financial_report}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def opine(self, query: str, context: str, financial_report: str) -> str:
        """
        发表观点 (Thesis)
        """
        print(f"♟️ [战略官] 正在分析 ROI...")

        
        return self.chain.invoke({
            "query": query,
            "context": context,
            "financial_report": financial_report
        })