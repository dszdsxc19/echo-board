import os
from dotenv import find_dotenv
from dotenv.main import load_dotenv
from mem0 import Memory

load_dotenv(find_dotenv())

api_key = os.getenv("OPEN_AI_API_KEY")
base_url = os.getenv("OPEN_AI_API_BASE")
chat_model = os.getenv("CHAT_MODEL")

class UserProfileService:
    def __init__(self, user_id: str = "default_user"):
        config = {
            "llm": {
                "provider": "OpenAI",
                "config": {
                    # Provider-specific settings go here
                    api_key: api_key,
                    model: chat_model,
                    openai_base_url: base_url
                }
            }
        }

        self.m = Memory.from_config(config)
        self.user_id = user_id

    def remember(self, text: str):
        """
        [写入路径]: 让系统记住一个新的事实/偏好
        通常在处理日记或对话结束后调用
        """·
        print(f"🧠 [Mem0] Extracting facts from: {text[:30]}...")
        self.m.add(text, user_id=self.user_id)

    def get_profile(self, query: str) -> str:
        """
        [读取路径]: 获取与当前话题相关的用户画像
        """
        # Mem0 的 search 会返回一个列表，包含提取出的事实
        memories = self.m.search(query, user_id=self.user_id)
        
        if not memories:
            return "No specific user preferences found."
            
        # 格式化为自然语言字符串
        profile_text = "\n".join([f"- {m['memory']}" for m in memories])
        return profile_text

    def get_all_memories(self):
        """获取所有记忆 (用于调试)"""
        return self.m.get_all(user_id=self.user_id)