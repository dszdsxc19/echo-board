import sys
from langchain_mcp_adapters.client import MultiServerMCPClient
import asyncio

async def create_mcp_tools():
    """
    初始化 MCP 客户端并获取工具列表。
    """
    client = MultiServerMCPClient(
        {
            "firefly-iii": {
                "transport": "http",
                "url": "http://localhost:3000/mcp",
            }
        }
    )

    # 建立连接并获取工具 (这是最关键的一步)
    # 这一步会自动把 MCP Tool 转换为 LangChain Tool 对象
    print("🔌 正在连接 MCP Servers...")
    tools = await client.get_tools()
    print(f"✅ 成功加载 {len(tools)} 个 MCP 工具: {[t.name for t in tools]}")
    
    return tools

if __name__ == "__main__":
    tools = asyncio.run(create_mcp_tools())
    print(tools)
