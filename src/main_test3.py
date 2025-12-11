import asyncio
import os
from src.infrastructure.vector_store import KnowledgeBase
from src.agents.orchestrator import BoardOrchestrator
from langchain_core.messages import HumanMessage, SystemMessage
from dotenv import find_dotenv, load_dotenv
from langchain_openai import ChatOpenAI
from pydantic import SecretStr

load_dotenv(find_dotenv())

async def main():
    print("🚀 System Booting...")

    # 1. 初始化 DB (Mock)
    kb = KnowledgeBase(persist_dir="./data/chroma_db", reset_db=False)

    # # 2. 初始化 MCP (Async)
    # # 这一步会启动子进程连接 Firefly MCP Server
    # mcp_tools = await create_mcp_tools()

    # 3. 初始化编排器
    orchestrator = BoardOrchestrator(vector_store=kb)

    # --- Test Case 1: 记账 (CFO Black Box) ---
    q1 = "Add an expense: 50 dollars for KFC"
    print(f"\n🗣️ User: {q1}")
    
    # 注意这里使用了 await
    result = await orchestrator.run_meeting(q1)
    
    if "cfo_result" in result:
        print(f"💰 CFO Output: {result['cfo_result']}")
    else:
        print("🤔 Board Output: ...")

if __name__ == "__main__":
    asyncio.run(main())
