from src.agents.board_members import BaseBoardMember
from src.agents.prompts.strategist_prompts import STRATEGIST_SYSTEM_PROMPT

import os
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from src.agents.prompts.synthesizer import SYNTHESIZER_SYSTEM_PROMPT

class Synthesizer(BaseBoardMember):
    """
    综合官：综合所有信息，输出最终结论。
    """
    def __init__(self):
        super().__init__("Synthesizer", SYNTHESIZER_SYSTEM_PROMPT)
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("user", "User Query: {query}\n\n[Fact Context]:\n{context}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def synthesize(self, data: dict) -> str:
        """
        综合所有信息，输出最终结论。
        """
        print(f"♟️ [综合官] 正在综合所有信息...")
        return self.chain.invoke({
            "query": data["query"],
            "context": data["context"],
            "strategist_opinion": data["strategist_opinion"],
            "coach_opinion": data["coach_opinion"]
        })
