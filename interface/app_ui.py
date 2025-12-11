# interface/app_ui.py
import streamlit as st
import sys
import os
import time

# --- 路径黑魔法 ---
# 因为我们在子目录运行，需要把根目录加入 path，这样才能 import core/infrastructure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.infrastructure.vector_store import KnowledgeBase
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.agents.orchestrator import BoardOrchestrator

# ==========================================
# 1. 配置页面
# ==========================================
st.set_page_config(
    page_title="Echo-Board MVP",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 注入一些 CSS 让卡片好看点
st.markdown("""
<style>
    .reportview-container {
        margin-top: -2em;
    }
    .stDeployButton {display:none;}
    .stat-box {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .strategist-box {
        background-color: #fcece8; /* 淡红 */
        border-left: 5px solid #ff4b4b;
    }
    .coach-box {
        background-color: #e8f4fc; /* 淡蓝 */
        border-left: 5px solid #1c83e1;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. 核心系统初始化 (伪后端)
# ==========================================
@st.cache_resource(show_spinner="正在唤醒董事会成员...")
def get_orchestrator():
    """
    初始化系统核心。
    使用 cache_resource 确保只会运行一次，除非手动清除缓存。
    """
    print("⚡ [System] Cold Boot Initialization...")
    
    # A. 数据库
    kb = KnowledgeBase(persist_dir="./data/chroma_db", reset_db=False) # 生产模式不建议每次 reset
    
    # B. 数据注入 (MVP为了演示，还是在这里做一下，实际使用可以移到 Sidebar 手动触发)
    # 注意：这里为了防止重复插入，实际代码需要判断是否已经存在
    # 这里我们假设如果你没有数据，就灌入Mock数据
    engine = MemoryIngestionEngine(knowledge_base=kb)
    # 模拟数据
    MOCK_DATA = """
    # 2023-10-25 财务
    ## 消费
    买了新的机械键盘，花了 1200 元。
    # 2023-10-25 工作
    ## 进度
    今天效率不错，写完了接口层。
    """
    engine.process_file(MOCK_DATA, source_name="system_boot_mock.md")
    
    # C. 编排器
    orchestrator = BoardOrchestrator(vector_store=kb)
    return orchestrator

# 获取单例
try:
    orchestrator = get_orchestrator()
except Exception as e:
    st.error(f"系统启动失败: {e}")
    st.stop()

# ==========================================
# 3. 状态管理
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = []

# ==========================================
# 4. 侧边栏 (Sidebar)
# ==========================================
with st.sidebar:
    st.title("🧠 Echo-Board")
    st.caption("v0.1 MVP | Modular Monolith")
    
    st.divider()
    
    # 模拟“每日早会”功能
    if st.button("☀️ 开启每日早会 (Daily Briefing)"):
        briefing_prompt = "请根据我昨天的记录（如果有的话），像开早会一样总结我的状态，并给出今天的建议。"
        st.session_state.messages.append({"role": "user", "content": briefing_prompt})
        # 强制刷新 rerun 从而触发主界面的处理逻辑
        st.rerun()

    st.divider()
    
    if st.button("🧹 清除对话历史"):
        st.session_state.messages = []
        st.rerun()
        
    if st.button("🔄 重载核心系统"):
        st.cache_resource.clear()
        st.rerun()

# ==========================================
# 5. 主聊天界面
# ==========================================

# A. 渲染历史消息
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg["role"] == "user":
            st.markdown(msg["content"])
        else:
            # 如果是 assistant 消息，我们需要判断是不是复杂对象
            # 这里的 msg["content"] 可能存的是最终结论，或者是一个复杂的 dict
            # 为了简单，我们只存最终结论文本。如果需要回放思考过程，需要改数据结构。
            st.markdown(msg["content"])

# B. 处理新输入
if prompt := st.chat_input("告诉董事会你的想法..."):
    # 1. 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. 董事会开始思考 (Visualizing the Chain)
    with st.chat_message("assistant"):
        
        # 创建一个状态容器
        status_container = st.status("🕵️ 史官正在检索档案...", expanded=True)
        
        try:
            # --- 调用后端 (LangGraph) ---
            # 我们在这里手动控制 Orchestrator 的调用，或者让 orchestrator 返回每一步
            # 为了更好的 UI 效果，我们可以稍微 hack 一下 run_meeting
            # 也可以直接拿最终结果，把中间过程打印出来
            
            # Step 1: 运行图
            final_state = orchestrator.run_meeting(prompt)
            
            # Step 2: 更新状态显示
            status_container.update(label="✅ 董事会已达成决议", state="complete", expanded=False)
            
            # --- 渲染“脑裂”辩论现场 (核心亮点) ---
            with st.expander("👁️ 查看董事会辩论记录 (The Internal Debate)", expanded=True):
                
                # 史官证据
                st.markdown(f"**📜 史官 (Archivist) 查到的事实:**")
                st.info(final_state['context'])
                
                # 左右互搏
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🔴 战略官 (Strategist)")
                    st.markdown(f"<div class='stat-box strategist-box'>{final_state['strategist_opinion']}</div>", unsafe_allow_html=True)
                    
                with col2:
                    st.markdown("### 🔵 教练 (Coach)")
                    st.markdown(f"<div class='stat-box coach-box'>{final_state['coach_opinion']}</div>", unsafe_allow_html=True)

            # --- 渲染最终结论 ---
            st.divider()
            st.markdown("### 📝 最终决议 (The Verdict)")
            response_text = final_state['final_verdict']
            st.markdown(response_text)
            
            # 3. 存入历史
            # 注意：存入历史的要是简单的文本，方便下次渲染。
            # 如果想保留辩论卡片，需要更复杂的 Session State 结构。
            # MVP 这里只存最终文本，下次刷新卡片会消失（这是个特性，保持清爽）。
            st.session_state.messages.append({"role": "assistant", "content": response_text})
            
        except Exception as e:
            status_container.update(label="❌ 系统发生错误", state="error")
            st.error(f"Error: {str(e)}")