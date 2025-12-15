import os
from dotenv import find_dotenv
from dotenv.main import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_openai import ChatOpenAI
from mem0 import Memory
from pydantic import SecretStr

load_dotenv(find_dotenv())

api_key = os.getenv("OPEN_AI_API_KEY")
base_url = os.getenv("OPEN_AI_API_BASE")
chat_model = os.getenv("CHAT_MODEL")

os.environ["OPENAI_API_KEY"] = api_key


llm = ChatOpenAI(
    temperature=0.7,
    model=chat_model,
    api_key=SecretStr(api_key),
    base_url=base_url
)
class UserProfileService:
    def __init__(self, user_id: str = "default_user"):

        config = {
            "llm": {
                "provider": "langchain",
                "config": {
                    "model": llm
                }
            },
            "embedder": {
                "provider": "langchain",
                "config": {
                    "model": OllamaEmbeddings(model="nomic-embed-text:latest"),
                }
            },
            "vector_store": {
                "provider": "langchain",
                "config": {
                    "client": Chroma(
                        persist_directory="./mem0/chroma_db",
                        embedding_function=OllamaEmbeddings(model="nomic-embed-text:latest"),
                        collection_name="mem0"  # Required collection name
                    )
                }
            }
        }

        self.m = Memory.from_config(config)
        self.user_id = user_id

    def remember(self, text: str):
        """
        [写入路径]: 让系统记住一个新的事实/偏好
        通常在处理日记或对话结束后调用
        """
        print(f"🧠 [Mem0] Extracting facts from: {text[:30]}...")
        self.m.add(text, user_id=self.user_id)

    def get_profile(self, query: str) -> str:
        """
        [读取路径]: 获取与当前话题相关的用户画像
        """
        # Mem0 的 search 会返回一个列表，元素可能是字符串，也可能是 dict
        memories = self.m.search(query, user_id=self.user_id)

        if not memories:
            return "No specific user preferences found."

        # 兼容字符串 / dict 两种结果格式
        lines = []
        for m in memories:
            if isinstance(m, dict):
                # 官方 SDK 常见字段名：memory 或 text
                text = m.get("memory") or m.get("text") or str(m)
            else:
                text = str(m)
            lines.append(f"- {text}")

        profile_text = "\n".join(lines)
        print("User profile: ", profile_text)
        return profile_text

    def get_all_memories(self):
        """获取所有记忆 (用于调试)"""
        return self.m.get_all(user_id=self.user_id)
