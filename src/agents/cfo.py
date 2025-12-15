import asyncio

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage

from src.agents.board_members import BaseBoardMember
from src.agents.prompts.cfo_prompts import CFO_SYSTEM_PROMPT
from src.mcp.firefly_iii import create_mcp_tools


class CFO(BaseBoardMember):
    """
    CFO：管理财务，记录交易。
    """

    def __init__(self):
        super().__init__("CFO", CFO_SYSTEM_PROMPT)
        # 注意：教练的输入多了一个 'strategist_opinion'
        self._tools = None
        self.agent_executor = None
        self._init_lock = asyncio.Lock()

    async def _ensure_agent(self):
        """
        延迟初始化 Agent，解决 tools 需要异步创建的问题。
        """
        if self.agent_executor:
            return

        async with self._init_lock:
            if self._tools is None:
                self._tools = await create_mcp_tools()
            self.agent_executor = create_agent(
                self.llm,
                self._tools,
                system_prompt=SystemMessage(content=self.system_prompt),
            )

    async def execute(self, query: str) -> str:
        """
        全异步执行。
        Graph 只需要调用这个方法，等待结果即可。
        不需要知道里面调用了什么 Tool。
        """
        await self._ensure_agent()
        # invoke 返回的是一个字典，这里我们关心其中的对话消息列表
        result = await self.agent_executor.ainvoke({"messages": [HumanMessage(query)]})

        messages = result.get("messages", []) if isinstance(result, dict) else []
        # 从消息列表中，反向查找最后一条 AIMessage
        last_ai_message = None
        for msg in reversed(messages):
            if isinstance(msg, AIMessage):
                last_ai_message = msg
                break

        if last_ai_message is not None:
            cfo_output = last_ai_message.content
        else:
            # 兜底：如果没有找到 AIMessage，就把原始结果转成字符串返回
            cfo_output = str(result)

        print("CFO Output: ", cfo_output)
        return cfo_output
