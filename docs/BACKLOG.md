1. 接入真实数据 (Real Data Ingestion)
目前的 process_file 还是手动调用的。

任务: 编写一个 Watcher 或者 Scanner。

逻辑: 指定你的 Obsidian 绝对路径，递归读取所有 .md 文件，计算文件 Hash，只处理新增或修改的文件（增量更新），否则每次重启都重跑 Embedding 会让你破产。

2. 提示词工程与评估 (Prompt Engineering & Eval)
你提到“旧想法不生效”，很多时候是因为 Prompt 写得不够好。

任务: 建立一个 tests/eval_cases.py。

逻辑: 收集 10 个你觉得回答得不好（Bad Case）的问题。每次修改 Prompt 后，跑一遍这 10 个问题，人工或用 LLM 评分，确保改进没有导致退步（Regression）。

3. 增加“工具使用” (Tool Use / Function Calling)
现在的 Agent 只能“说话”。

任务: 给战略官一把“枪”。

例子:

如果战略官建议“必须把下周二晚上锁死用来写代码”。

给他一个 GoogleCalendarTool，让他真的去你的日历上建一个 Deep Work 的日程。

这需要修改 LangGraph，增加 ToolNode。