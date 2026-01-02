# interface/app_ui.py
import asyncio
import os
import sys
import time

import streamlit as st

# --- 路径黑魔法 ---
# 因为我们在子目录运行，需要把根目录加入 path，这样才能 import core/infrastructure
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.agents.orchestrator import BoardOrchestrator
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
from src.infrastructure.vector_store import KnowledgeBase

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

# 全局进度状态存储
def initialize_session_state():
    """初始化 session_state 中的进度相关变量"""
    if "progress_updates" not in st.session_state:
        st.session_state.progress_updates = []
    if "meeting_start_time" not in st.session_state:
        st.session_state.meeting_start_time = None
    if "sync_progress" not in st.session_state:
        st.session_state.sync_progress = None

# 在模块加载时立即初始化
initialize_session_state()

def progress_callback(stage: str, message: str, start_time: float):
    """
    进度回调函数 - 接收 orchestrator 的进度更新并存储到 session_state
    线程安全地更新 Streamlit 状态
    Args:
        stage: 阶段名称
        message: 进度消息
        start_time: 步骤开始时间戳
    """
    # 确保 session_state 已初始化
    initialize_session_state()

    # 计算耗时
    duration = time.time() - start_time

    # 安全地追加进度更新
    st.session_state.progress_updates.append({
        "stage": stage,
        "message": message,
        "start_time": start_time,
        "duration": duration
    })

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
    mock_data = """
    # 2023-10-25 财务
    ## 消费
    买了新的机械键盘，花了 1200 元。
    # 2023-10-25 工作
    ## 进度
    今天效率不错，写完了接口层。
    """
    engine.process_file(mock_data, source_name="system_boot_mock.md")

    # C. 编排器 - 传入进度回调函数
    orchestrator = BoardOrchestrator(vector_store=kb, progress_callback=progress_callback)
    return orchestrator, engine

# 获取单例
try:
    orchestrator, ingestion_engine = get_orchestrator()
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

    # 模拟"每日早会"功能
    if st.button("☀️ 开启每日早会 (Daily Briefing)"):
        briefing_prompt = "请根据我昨天的记录（如果有的话），像开早会一样总结我的状态，并给出今天的建议。"
        st.session_state.messages.append({"role": "user", "content": briefing_prompt})
        # 强制刷新 rerun 从而触发主界面的处理逻辑
        st.rerun()

    st.divider()

    # 同步功能区域
    st.markdown("### 📂 数据同步")
    folder_path = st.text_input("输入 Obsidian 库路径:", placeholder="/path/to/your/obsidian/vault")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("🔄 同步数据", disabled=not folder_path):
            if folder_path and os.path.exists(folder_path):
                # 显示同步进度
                sync_status = st.status("正在同步数据...", expanded=True)
                sync_progress = st.progress(0)
                sync_text = st.empty()
                sync_file_text = st.empty()

                # 创建日志容器
                log_container = st.empty()

                try:
                    # 记录开始时间
                    start_time = time.time()

                    # 获取文件夹中所有md文件
                    md_files = []
                    for root, dirs, files in os.walk(folder_path):
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                        for file in files:
                            if file.endswith(".md"):
                                md_files.append(os.path.join(root, file))

                    total_files = len(md_files)
                    total_size_bytes = 0

                    # 第一遍扫描：计算总文件大小 (Bytes) - ⚡ Bolt Optimization: Replace full read with os.path.getsize
                    for file_path in md_files:
                        try:
                            total_size_bytes += os.path.getsize(file_path)
                        except Exception:
                            pass

                    if total_files == 0:
                        sync_status.update(label="⚠️ 未找到 Markdown 文件", state="warning")
                        st.stop()

                    # 逐步处理文件
                    processed = 0
                    processed_bytes = 0
                    total_content_length = 0 # Track this for final stats

                    # 初始化日志列表
                    processed_files = []

                    # ⚡ Bolt Optimization: Batch process events
                    all_collected_events = []
                    all_file_contents = []

                    for file_path in md_files:
                        try:
                            # 读取文件内容
                            with open(file_path, "r", encoding="utf-8") as f:
                                content = f.read()

                            file_size = len(content.encode('utf-8')) # Approximate byte size for progress

                            relative_path = os.path.relpath(file_path, folder_path)

                            # 更新当前文件显示
                            sync_file_text.markdown(
                                f"**正在处理**: {relative_path} "
                                f"({len(content)} 字符)"
                            )

                            # 处理文件 (不立即持久化)
                            events = ingestion_engine.process_file(content, source_name=relative_path, persist=False)
                            all_collected_events.extend(events)
                            all_file_contents.append(content)

                            processed += 1
                            processed_bytes += file_size
                            total_content_length += len(content)

                            # 记录已处理的文件
                            processed_files.append({
                                "file": relative_path,
                                "chars": len(content),
                                "status": "✅"
                            })

                            # 更新日志显示
                            log_text = "**已处理的文件:**\n\n"
                            for item in processed_files[-10:]:  # 只显示最近10个
                                log_text += f"- {item['status']} {item['file']} ({item['chars']} 字符)\n"
                            log_container.markdown(log_text)

                            # 更新进度
                            if total_size_bytes > 0:
                                progress_percent = min((processed_bytes / total_size_bytes) * 100, 100)
                            else:
                                progress_percent = 100

                            sync_progress.progress(int(progress_percent))
                            sync_text.text(
                                f"进度: {processed}/{total_files} 文件 | "
                                f"{processed_bytes}/{total_size_bytes} Bytes "
                                f"({progress_percent:.1f}%)"
                            )

                        except Exception as e:
                            error_msg = f"跳过文件 {file_path}: {e}"
                            processed_files.append({
                                "file": relative_path,
                                "error": str(e),
                                "status": "❌"
                            })
                            log_container.markdown(
                                f"**❌ 错误**: {error_msg}\n\n"
                                f"**已处理的文件** ({len(processed_files)} 个):\n"
                                + "\n".join([
                                    f"- {item['status']} {item['file']} ({item.get('chars', 'N/A')} 字符)"
                                    for item in processed_files[-10:]
                                ])
                            )
                            st.warning(error_msg)

                    # 批量保存到向量数据库
                    if all_collected_events:
                        sync_file_text.text("⚡ 正在批量保存到数据库...")
                        ingestion_engine.save_events(all_collected_events)

                    if all_file_contents:
                        sync_file_text.text("⚡ 正在批量提取记忆到 Mem0...")
                        ingestion_engine.save_memories(all_file_contents)

                    # 同步完成
                    total_time = time.time() - start_time
                    sync_status.update(
                        label=f"✅ 同步完成! 处理了 {processed} 个文件",
                        state="complete",
                        expanded=False
                    )
                    sync_progress.progress(100)
                    sync_text.text(f"总耗时: {total_time:.2f}s | 总字符数: {total_content_length}")

                    # 最终日志显示
                    final_log = f"**✅ 同步完成! 处理了 {processed}/{total_files} 个文件**\n\n"
                    final_log += f"**总耗时**: {total_time:.2f}s | **总字符数**: {total_content_length}\n\n"
                    final_log += "**所有处理的文件**:\n\n"

                    for item in processed_files:
                        if item['status'] == "✅":
                            final_log += f"- ✅ {item['file']} ({item['chars']} 字符)\n"
                        else:
                            final_log += f"- ❌ {item['file']}: {item.get('error', '未知错误')}\n"

                    log_container.markdown(final_log)

                    # 存储同步结果到session_state
                    st.session_state.sync_progress = {
                        "status": "complete",
                        "processed": processed,
                        "total": total_files,
                        "content_length": total_content_length,
                        "files": processed_files
                    }

                except Exception as e:
                    sync_status.update(label="❌ 同步失败", state="error")
                    st.error(f"同步过程中发生错误: {e}")
            else:
                st.error("路径不存在，请检查输入的路径是否正确")

    with col2:
        if st.button("🗑️ 清除", disabled=not folder_path):
            st.rerun()

    # 显示最近同步结果
    if st.session_state.sync_progress and st.session_state.sync_progress.get("status") == "complete":
        progress = st.session_state.sync_progress
        st.success(
            f"✅ 上次同步: {progress.get('processed', 0)}/{progress.get('total', 0)} 文件 | "
            f"{progress.get('content_length', 0)} 字符"
        )

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
if not st.session_state.messages:
    # Render Welcome Screen
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1>👋 Welcome to Echo-Board</h1>
        <p style="color: #666; font-size: 1.1em;">Your Personal Board of Directors</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="stat-box strategist-box">
            <h3>🔴 The Strategist</h3>
            <p>Focuses on long-term goals, efficiency, and brutal honesty. Helps you prioritize.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="stat-box coach-box">
            <h3>🔵 The Coach</h3>
            <p>Focuses on well-being, sustainability, and personal growth. Ensures you don't burn out.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.caption("👈 Check the sidebar to **Sync Data** or start a **Daily Briefing**.")

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

        # 确保 session_state 已初始化
        initialize_session_state()

        # 清空之前的进度记录
        st.session_state.progress_updates = []
        st.session_state.meeting_start_time = time.time()
        last_update_count = 0

        # 创建一个状态容器，初始状态
        status_container = st.status("📝 准备开始董事会会议...", expanded=True)

        # 创建进度条组件
        progress_bar = st.progress(0)
        progress_text = st.empty()

        try:
            # --- 调用后端 (LangGraph) ---
            # Step 1: 运行图 (在单独的线程中执行以便实时更新UI)
            import threading

            final_state = {}

            def run_orchestrator():
                # 在单独线程中运行异步的 run_meeting
                final_state["result"] = asyncio.run(orchestrator.run_meeting(prompt))

            thread = threading.Thread(target=run_orchestrator)
            thread.start()

            # Step 2: 实时显示进度更新
            total_steps = 4  # 总步骤数
            while thread.is_alive():
                current_count = len(st.session_state.progress_updates)
                if current_count > last_update_count:
                    # 有新的进度更新
                    latest_update = st.session_state.progress_updates[-1]

                    # 更新状态容器
                    status_container.update(
                        label=f"{latest_update['stage']}: {latest_update['message']}",
                        state="running"
                    )

                    # 计算进度百分比
                    progress_percent = min((current_count / total_steps) * 100, 100)
                    progress_bar.progress(int(progress_percent))

                    # 显示进度文本和时间信息
                    elapsed_time = time.time() - st.session_state.meeting_start_time
                    progress_text.markdown(
                        f"**进度**: {current_count}/{total_steps} ({progress_percent:.0f}%) | "
                        f"**已用时间**: {elapsed_time:.1f}s"
                    )

                    last_update_count = current_count
                time.sleep(0.1)  # 避免过度消耗CPU

            thread.join()

            # 完成后显示最终状态
            if st.session_state.progress_updates:
                latest_update = st.session_state.progress_updates[-1]
                status_container.update(
                    label=f"✅ {latest_update['message']}",
                    state="complete",
                    expanded=False
                )

                # 进度条设置为100%
                progress_bar.progress(100)
                total_time = time.time() - st.session_state.meeting_start_time
                progress_text.markdown(
                    f"**进度**: 4/4 (100%) | **总耗时**: {total_time:.2f}s ✅"
                )
            else:
                status_container.update(
                    label="✅ 董事会已达成决议",
                    state="complete",
                    expanded=False
                )

            # --- 展示详细进度历史 ---
            if st.session_state.progress_updates and len(st.session_state.progress_updates) > 0:
                with st.expander("📊 查看董事会会议进度记录", expanded=False):
                    st.markdown("**会议进度详情：**")

                    # 创建表格显示进度
                    for i, update in enumerate(st.session_state.progress_updates, 1):
                        # 计算相对于会议开始的时间
                        if st.session_state.meeting_start_time:
                            relative_time = update['start_time'] - st.session_state.meeting_start_time
                        else:
                            relative_time = 0

                        # 格式化耗时
                        duration_str = f"{update['duration']:.2f}s" if update.get('duration') else "N/A"

                        st.markdown(
                            f"{i}. **{update['stage']}**: {update['message']} "
                            f"| ⏱️ 耗时: {duration_str} "
                            f"| ⏰ 相对时间: +{relative_time:.2f}s"
                        )

                    # 添加统计信息
                    if st.session_state.meeting_start_time:
                        st.divider()
                        total_time = time.time() - st.session_state.meeting_start_time
                        st.markdown(
                            f"**总耗时**: {total_time:.2f}s | "
                            f"**平均每步**: {total_time/4:.2f}s"
                        )

            # --- 渲染“脑裂”辩论现场 (核心亮点) ---
            with st.expander("👁️ 查看董事会辩论记录 (The Internal Debate)", expanded=True):

                # 史官证据
                st.markdown("**📜 史官 (Archivist) 查到的事实:**")
                st.info(final_state['result']['context'])

                # 左右互搏
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("### 🔴 战略官 (Strategist)")
                    st.markdown(f"<div class='stat-box strategist-box'>{final_state['result']['strategist_opinion']}</div>", unsafe_allow_html=True)

                with col2:
                    st.markdown("### 🔵 教练 (Coach)")
                    st.markdown(f"<div class='stat-box coach-box'>{final_state['result']['coach_opinion']}</div>", unsafe_allow_html=True)

            # --- 渲染最终结论 ---
            st.divider()
            st.markdown("### 📝 最终决议 (The Verdict)")
            response_text = final_state['result']['final_verdict']
            st.markdown(response_text)

            # 3. 存入历史
            # 注意：存入历史的要是简单的文本，方便下次渲染。
            # 如果想保留辩论卡片，需要更复杂的 Session State 结构。
            # MVP 这里只存最终文本，下次刷新卡片会消失（这是个特性，保持清爽）。
            st.session_state.messages.append({"role": "assistant", "content": response_text})

        except Exception as e:
            status_container.update(label="❌ 系统发生错误", state="error")
            st.error(f"Error: {str(e)}")
