import os
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(find_dotenv())

api_key = os.getenv("OPEN_AI_API_KEY")
base_url = os.getenv("OPEN_AI_API_BASE")
chat_model = os.getenv("CHAT_MODEL")

assert api_key, "OPEN_AI_API_KEY 环境变量未设置"
assert base_url, "OPEN_AI_API_BASE 环境变量未设置"
assert chat_model, "CHAT_MODEL 环境变量未设置"

# 或者使用环境变量
llm = ChatOpenAI(
    temperature=0.2,
    model=chat_model,
    api_key=SecretStr(api_key),
    base_url=base_url
)

# 创建消息
messages = [
    SystemMessage(content="你是一个有用的 AI 助手"),
    HumanMessage(content="你好")
]

# 调用模型
response = llm.invoke(messages)
print(response.content)
