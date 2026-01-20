import os

from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(find_dotenv())

api_key = os.getenv("OPEN_AI_API_KEY")
base_url = os.getenv("OPEN_AI_API_BASE")
chat_model = os.getenv("CHAT_MODEL")

class BaseBoardMember:
    """董事会成员基类"""
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.llm = ChatOpenAI(
            temperature=0.7,
            model=chat_model,
            api_key=SecretStr(api_key),
            base_url=base_url
        )
        self.system_prompt = system_prompt
