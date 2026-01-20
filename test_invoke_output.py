"""
演示 agent.invoke 和 chain.invoke 输出结构的差异
"""
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI


# 创建一个简单的工具用于 agent
@tool
def get_weather(city: str) -> str:
    """获取城市的天气"""
    return f"{city}的天气是晴天"

# 初始化 LLM
llm = ChatOpenAI(temperature=0)

# ============ 方式 1: Agent.invoke() ============
print("=" * 50)
print("方式 1: Agent.invoke() 的输出结构")
print("=" * 50)

agent = create_agent(
    llm,
    tools=[get_weather],
    system_prompt=SystemMessage(content="你是一个有用的助手")
)

agent_result = agent.invoke({"messages": [HumanMessage(content="北京天气怎么样？")]})
print("\nAgent.invoke() 返回类型:", type(agent_result))
print("Agent.invoke() 返回内容:")
print(agent_result)
print("\nAgent 返回的 keys:", agent_result.keys() if isinstance(agent_result, dict) else "不是字典")
print("\nAgent 返回的 messages 类型:", type(agent_result.get("messages", [])))
print("Agent 返回的最后一条消息类型:", type(agent_result.get("messages", [])[-1]) if agent_result.get("messages") else "无")

# ============ 方式 2: Chain.invoke() (prompt | llm | StrOutputParser) ============
print("\n" + "=" * 50)
print("方式 2: Chain.invoke() 的输出结构")
print("=" * 50)

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个有用的助手"),
    ("user", "{query}")
])
chain = prompt | llm | StrOutputParser()

chain_result = chain.invoke({"query": "北京天气怎么样？"})
print("\nChain.invoke() 返回类型:", type(chain_result))
print("Chain.invoke() 返回内容:")
print(chain_result)

# ============ 方式 3: 不使用 StrOutputParser 的 Chain ============
print("\n" + "=" * 50)
print("方式 3: Chain.invoke() (prompt | llm，不使用 StrOutputParser) 的输出结构")
print("=" * 50)

chain_no_parser = prompt | llm
chain_no_parser_result = chain_no_parser.invoke({"query": "北京天气怎么样？"})
print("\nChain (无 parser).invoke() 返回类型:", type(chain_no_parser_result))
print("Chain (无 parser).invoke() 返回内容:")
print(chain_no_parser_result)
print("\n返回对象的 content 属性:", chain_no_parser_result.content)

print("\n" + "=" * 50)
print("总结:")
print("=" * 50)
print("1. Agent.invoke() 返回: 字典，包含 'messages' 键（消息列表）")
print("2. Chain.invoke() (带 StrOutputParser) 返回: 字符串")
print("3. Chain.invoke() (不带 StrOutputParser) 返回: AIMessage 对象，需要用 .content 获取文本")

