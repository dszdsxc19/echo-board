from src.agents.archivist import Archivist
from src.agents.coach import Coach  # 导入新角色
from src.agents.strategist import Strategist
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.infrastructure.vector_store import KnowledgeBase

# 模拟一份"纠结"的数据
# 场景：用户想买很贵的游戏机，但最近没写代码且没钱
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

def main():
    print("🚀 启动 Board Meeting (Debate Mode)...")

    # 1. 基础设施准备
    kb = KnowledgeBase(persist_dir="./data/chroma_db", reset_db=True)
    engine = MemoryIngestionEngine(knowledge_base=kb)
    engine.process_file(MOCK_DATA, source_name="financial_crisis.md")

    # 2. 角色就位
    archivist = Archivist(kb=kb)
    strategist = Strategist()
    coach = Coach()

    # 3. 用户提问
    user_query = "我心情不好，想买个 VR 头显 (3500元) 奖励自己，可以吗？"
    print(f"\n🗣️ 用户提问: {user_query}")

    # ==========================================

    # Step 1: 史官查证 (The Facts)
    # ==========================================
    print("\n" + "="*40)
    print("📜 PHASE 1: FACT FINDING (史官)")
    print("="*40)
    archivist_result = archivist.consult(user_query)
    facts = archivist_result["answer"]
    # print(facts) # 调试时可以打印看看

    # ==========================================
    # Step 2: 战略官发言 (The Thesis)
    # ==========================================
    print("\n" + "="*40)
    print("♟️ PHASE 2: STRATEGIC ANALYSIS (战略官)")
    print("="*40)
    # 战略官基于 事实 + 提问 进行判断
    strat_opinion = strategist.opine(query=user_query, context=facts)
    print(strat_opinion)

    # ==========================================
    # Step 3: 教练发言 (The Antithesis)
    # ==========================================
    print("\n" + "="*40)
    print("🧘 PHASE 3: WELLNESS CHECK (教练)")
    print("="*40)
    # 教练不仅看事实，还要看战略官怎么说，然后决定是支持还是反对
    coach_opinion = coach.opine(
        query=user_query,
        context=facts,
        strategist_opinion=strat_opinion
    )
    print(coach_opinion)

if __name__ == "__main__":
     main()
