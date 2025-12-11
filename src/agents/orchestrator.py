from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 引入之前的角色类
from src.agents.archivist import Archivist
from src.agents.strategist import Strategist
from src.agents.coach import Coach

from typing import TypedDict, List, Annotated
import operator
from langgraph.graph import StateGraph, END

from src.agents.synthesizer import Synthesizer

# 定义整个辩论过程中的状态数据
class BoardState(TypedDict):
    query: str                # 用户原始问题
    context: str              # 史官查到的事实
    strategist_opinion: str   # 战略官的观点
    coach_opinion: str        # 教练的观点
    final_verdict: str        # 最终决议
    messages: Annotated[List[str], operator.add] # (可选) 用于记录完整的对话历史
    
class BoardOrchestrator:
    def __init__(self, vector_store):
        # 初始化各个角色
        self.archivist = Archivist(vector_store)
        self.strategist = Strategist()
        self.coach = Coach()
        self.synthesizer = Synthesizer()

        # 构建图
        self.graph = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(BoardState)

        # --- 添加节点 (Nodes) ---
        
        def run_archivist(state: BoardState):
            # 史官节点：输入 query，更新 context
            print("--- Step 1: Archivist ---")
            result = self.archivist.consult(state["query"])
            return {"context": result["answer"]}

        def run_strategist(state: BoardState):
            # 战略官节点：输入 query + context，更新 strategist_opinion
            print("--- Step 2: Strategist ---")
            opinion = self.strategist.opine(state["query"], state["context"])
            return {"strategist_opinion": opinion}

        def run_coach(state: BoardState):
            # 教练节点：输入 query + context + strategist_opinion，更新 coach_opinion
            print("--- Step 3: Coach ---")
            opinion = self.coach.opine(
                state["query"], 
                state["context"], 
                state["strategist_opinion"]
            )
            return {"coach_opinion": opinion}

        def run_synthesizer(state: BoardState):
            # 决议者节点：综合所有信息，输出最终结论
            print("--- Step 4: Synthesizer ---")
            verdict = self.synthesizer.synthesize({
                "query": state["query"],
                "context": state["context"],
                "strategist_opinion": state["strategist_opinion"],
                "coach_opinion": state["coach_opinion"]
            })
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

