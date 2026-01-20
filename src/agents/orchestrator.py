import operator
import time
from typing import Annotated, Callable, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.agents.archivist import Archivist
from src.agents.cfo import CFO
from src.agents.coach import Coach
from src.agents.router import Router
from src.agents.strategist import Strategist
from src.agents.synthesizer import Synthesizer
from src.infrastructure.mem0_service import UserProfileService


# 定义整个辩论过程中的状态数据
class BoardState(TypedDict):
    # --- 上下文层 ---
    query: str                # 用户原始问题
    context: str              # 史官查到的事实
    strategist_opinion: str   # 战略官的观点
    user_profile: str     # Mem0: 用户是什么样的人 (Preferences/Facts) [NEW]

    # --- 辩论层 ---
    coach_opinion: str        # 教练的观点
    final_verdict: str        # 最终决议
    financial_report: str

    # --- 单次执行层 ---
    cfo_result: str           # 纯记账时的返回结果
    messages: Annotated[List[str], operator.add] # (可选) 用于记录完整的对话历史

# 进度更新数据结构
class ProgressUpdate(TypedDict):
    stage: str          # 阶段名称
    message: str        # 进度消息
    start_time: float   # 开始时间戳
    duration: Optional[float]  # 耗时（秒）


class BoardOrchestrator:
    def __init__(self, vector_store, progress_callback: Optional[Callable[[str, str, float], None]] = None):
        """
        Args:
            vector_store: 向量存储实例
            progress_callback: 进度回调函数，接收 (stage: str, message: str, start_time: float) 参数
        """
        # 初始化各个角色
        self.mem0 = UserProfileService(user_id="owner") # 初始化 Mem0
        self.archivist = Archivist(vector_store)
        self.strategist = Strategist()
        self.coach = Coach()
        self.cfo = CFO()
        self.synthesizer = Synthesizer()
        self.router = Router()

        # 进度回调函数
        self.progress_callback = progress_callback

        # 总步骤数（用于计算进度百分比）
        self.total_steps = 4

        # 构建图
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(BoardState)

        # --- 添加节点 (Nodes) ---
        # === [NEW] Profile Node ===
        # 注意：这里是普通的嵌套函数，不需要也不能带 self 参数
        def run_profile_loader(state: BoardState):
            """
            专门负责去 Mem0 查询与当前 Query 相关的用户偏好
            """
            query = state["query"]
            print("🧠 [Mem0] Loading user profile...")
            profile = self.mem0.get_profile(query)
            return {"user_profile": profile}

        def run_archivist(state: BoardState):
            # 史官节点：输入 query，更新 context
            start_time = time.time()
            if self.progress_callback:
                self.progress_callback("史官", "🕵️ 史官正在检索档案...", start_time)
            print("--- Step 1: Archivist ---")
            result = self.archivist.consult(state["query"])
            if self.progress_callback:
                self.progress_callback("史官", "✅ 史官已完成档案检索", start_time)
            return {"context": result["answer"]}

        def run_strategist(state: BoardState):
            # 战略官节点：输入 query + context，更新 strategist_opinion
            start_time = time.time()
            if self.progress_callback:
                self.progress_callback("战略官", "🎯 战略官正在分析形势...", start_time)
            print("--- Step 2: Strategist ---")
            opinion = self.strategist.opine(state["query"], state["context"], state["financial_report"], state["user_profile"])
            if self.progress_callback:
                self.progress_callback("战略官", "✅ 战略官已完成分析", start_time)
            return {"strategist_opinion": opinion}

        def run_coach(state: BoardState):
            # 教练节点：输入 query + context + strategist_opinion，更新 coach_opinion
            start_time = time.time()
            if self.progress_callback:
                self.progress_callback("教练", "💪 教练正在提出指导意见...", start_time)
            print("--- Step 3: Coach ---")
            opinion = self.coach.opine(
                state["query"],
                state["context"],
                state["strategist_opinion"],
                state["user_profile"]
            )
            if self.progress_callback:
                self.progress_callback("教练", "✅ 教练已完成指导", start_time)
            return {"coach_opinion": opinion}

        # === CFO Node 1: 纯执行 (记账) ===
        async def run_cfo_execution(state: BoardState):
            print("💰 [CFO Execution] Processing transaction...")
            result = await self.cfo.execute(state["query"])
            return {"cfo_result": result}

        # === CFO Node 2: 顾问 (查账提供上下文) ===
        async def run_cfo_advisory(state: BoardState):
            print("📊 [CFO Advisory] Analyzing financial status for the board...")

            # 技巧：我们可以稍微修改一下给 CFO 的 Prompt，让他知道现在是查询模式
            # 或者直接把用户的原始问题给他，Agent 通常足够聪明能自己判断
            # 这里为了稳妥，我们构造一个 prompt
            advisory_query = f"User Query: '{state['query']}'. Please provide relevant financial context (balance, recent transactions) to help the board answer this."

            result = await self.cfo.execute(advisory_query)
            return {"financial_report": result}

        def run_synthesizer(state: BoardState):
            # 决议者节点：综合所有信息，输出最终结论
            start_time = time.time()
            if self.progress_callback:
                self.progress_callback("决议者", "🤝 决议者正在综合各方意见...", start_time)
            print("--- Step 4: Synthesizer ---")
            verdict = self.synthesizer.synthesize({
                "query": state["query"],
                "context": state["context"],
                "strategist_opinion": state["strategist_opinion"],
                "coach_opinion": state["coach_opinion"]
            })
            # [NEW] 让系统记住这次的决议
            # 这样下次 Mem0 就能搜到 "User was advised to sleep early on Oct 25"
            self.mem0.remember(f"Interaction Date: Today. User asked: {state['query']}. Decision: {verdict}")
            if self.progress_callback:
                self.progress_callback("决议者", "✅ 董事会已达成决议", start_time)
            return {"final_verdict": verdict}

        # === 1. Define Nodes ===
        # 分支 A 的节点
        workflow.add_node("cfo_execution", run_cfo_execution)

        # 分支 B 的并行节点
        workflow.add_node("archivist", run_archivist) # 返回 {"context": ...}
        workflow.add_node("cfo_advisory", run_cfo_advisory) # 返回 {"financial_report": ...}
        workflow.add_node("profile_loader", run_profile_loader) # [NEW]

        # 汇合后的节点
        workflow.add_node("strategist", run_strategist)
        workflow.add_node("coach", run_coach)
        workflow.add_node("synthesizer", run_synthesizer)

        # === 2. Define Edges ===

        # [关键] 入口路由逻辑
        def route_entry(state: BoardState):
            intent = self.router.decide(state["query"])
            print(f"🚦 [Router] Routing to: {intent}")
            if intent == "finance_execution":
                # 这是一个单一路径
                return "cfo_execution"
            else:
                # [并行触发] 返回一个列表，LangGraph 会自动并行执行这些节点！
                return ["archivist", "cfo_advisory", "profile_loader"]

        # 设置条件入口
        workflow.set_conditional_entry_point(
            route_entry,
            {
                "cfo_execution": "cfo_execution",
                "archivist": "archivist",
                "cfo_advisory": "cfo_advisory",
                # [NEW] 并行入口里还会返回 "profile_loader"，这里也要声明
                "profile_loader": "profile_loader",
            }
        )

        # 分支 A 结束
        workflow.add_edge("cfo_execution", END)

        # 分支 B 汇合逻辑
        # LangGraph 会等待 archivist 和 cfo_advisory 都执行完，
        # 然后把它们的结果合并到 State 中，再传给 strategist
        workflow.add_edge("archivist", "strategist")
        workflow.add_edge("cfo_advisory", "strategist")
        workflow.add_edge("profile_loader", "strategist")

        # 后续线性流程
        workflow.add_edge("strategist", "coach")
        workflow.add_edge("coach", "synthesizer")
        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    # 入口也变成了 async
    async def run_meeting(self, user_query: str):
        initial_state = {"query": user_query}
        final_state = await self.graph.ainvoke(initial_state)
        return final_state
