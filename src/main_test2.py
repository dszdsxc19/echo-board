import os
from src.infrastructure.vector_store import KnowledgeBase
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.agents.orchestrator import BoardOrchestrator

# 模拟数据 (继续沿用之前的"买VR"案例)
MOCK_DATA = """
# 2023-10-20 财务记录
## 支出
本月信用卡账单已出，透支 5000 元。
银行卡余额：200 元。

# 2023-10-21 工作日志
## 进度
已经连续三天没有提交 GitHub 代码了。
一直在看 YouTube 视频，感觉很颓废。

# 2023-10-22 心情
## 压力
感觉只要一开始工作就心慌，想通过买买买来解压。
想买那个新出的 VR 头显 (价格 3500 元)。
"""

def setup_system():
    """系统初始化 (Bootstrap)"""
    print("⚙️ 初始化系统组件...")
    # 1. DB
    kb = KnowledgeBase(persist_dir="./data/chroma_db", reset_db=True)
    
    # 2. Ingestion (MVP 每次启动都灌一次数据，实际生产会分开)
    engine = MemoryIngestionEngine(knowledge_base=kb)
    engine.process_file(MOCK_DATA, source_name="financial_crisis.md")
    
    # 3. Orchestrator
    orchestrator = BoardOrchestrator(vector_store=kb)
    return orchestrator

def main():
    # 1. 启动
    orchestrator = setup_system()
    
    # 2. 用户输入
    user_query = "我心情不好，想买个 VR 头显 (3500元) 奖励自己，可以吗？"
    print(f"\n🗣️ 用户: {user_query}\n")
    
    # 3. 召开董事会
    print("🔔 召开董事会会议 (Board Meeting Started)...")
    result_state = orchestrator.run_meeting(user_query)
    
    # 4. 打印最终回执 (The Final Output)
    print("\n" + "="*50)
    print("📝 董事会最终决议 (FINAL VERDICT)")
    print("="*50)
    print(result_state["final_verdict"])
    
    # (可选) 打印调试信息，看看中间过程
    # print("\n[Debug Log]")
    # print(f"Strategist said: {result_state['strategist_opinion'][:50]}...")
    # print(f"Coach said: {result_state['coach_opinion'][:50]}...")

if __name__ == "__main__":
    main()