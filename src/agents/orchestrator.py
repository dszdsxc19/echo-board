
# 引入之前的角色类
import operator
import time
from typing import Annotated, Callable, List, Optional, TypedDict

from langgraph.graph import END, StateGraph

from src.agents.archivist import Archivist
from src.agents.coach import Coach
from src.agents.strategist import Strategist
from src.agents.synthesizer import Synthesizer


# 定义整个辩论过程中的状态数据
class BoardState(TypedDict):
    query: str                # 用户原始问题
    context: str              # 史官查到的事实
    strategist_opinion: str   # 战略官的观点
    coach_opinion: str        # 教练的观点
    final_verdict: str        # 最终决议
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
        self.archivist = Archivist(vector_store)
        self.strategist = Strategist()
        self.coach = Coach()
        self.synthesizer = Synthesizer()

        # 进度回调函数
        self.progress_callback = progress_callback

        # 总步骤数（用于计算进度百分比）
        self.total_steps = 4

        # 构建图
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(BoardState)

        # --- 添加节点 (Nodes) ---

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
            opinion = self.strategist.opine(state["query"], state["context"])
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
                state["strategist_opinion"]
            )
            if self.progress_callback:
                self.progress_callback("教练", "✅ 教练已完成指导", start_time)
            return {"coach_opinion": opinion}

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
            if self.progress_callback:
                self.progress_callback("决议者", "✅ 董事会已达成决议", start_time)
            return {"final_verdict": verdict}

        workflow.add_node("archivist", run_archivist)
        workflow.add_node("strategist", run_strategist)
        workflow.add_node("coach", run_coach)
        workflow.add_node("synthesizer", run_synthesizer)

        # --- 定义连线 (Edges) ---
        # 这是一个线性流程 (Linear Flow)，未来可以改成循环
        workflow.set_entry_point("archivist")
        workflow.add_edge("archivist", "strategist")
        workflow.add_edge("strategist", "coach")
        workflow.add_edge("coach", "synthesizer")
        workflow.add_edge("synthesizer", END)

        return workflow.compile()

    def run_meeting(self, user_query: str):
        """外部调用的入口"""
        initial_state = BoardState(query= user_query, context="", strategist_opinion="", coach_opinion="", final_verdict="", messages=[])
        final_state = self.graph.invoke(initial_state)
        return final_state

