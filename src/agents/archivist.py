# agents/archivist.py
from typing import List, Dict
import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

# 引入我们刚才定义的 Prompt 和下层设施
from src.agents.prompts.archivist_prompts import ARCHIVIST_SYSTEM_PROMPT
# 假设你在 infra 中已经封装好了 KnowledgeBase，如果没有，暂时用 Mock
from src.core.models.domain_models import LifeEvent
from src.infrastructure.vector_store import KnowledgeBase 
from src.infrastructure.llm_factory import llm
from src.infrastructure.obsidian_loader import MemoryIngestionEngine
class Archivist:
    def __init__(self, kb: KnowledgeBase):
        """
        :param vector_store: 已经初始化的向量数据库实例 (KnowledgeBase)
        """
        self.kb = kb
        self.llm = llm
        
        # 组装 Chain
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", ARCHIVIST_SYSTEM_PROMPT),
            ("user", "User Query: {query}\n\n[Context Data]:\n{context}")
        ])
        self.chain = self.prompt | self.llm | StrOutputParser()

    def _format_context(self, docs: List[LifeEvent]) -> str:
        """
        将检索到的 LifeEvent 对象转化为 LLM 易读的字符串格式
        """
        formatted_str = ""
        for i, doc in enumerate(docs):
            # 获取元数据，防止 Key不存在报错
            date = doc.metadata.get("Date/Title", "Unknown Date")
            section = doc.metadata.get("Section", "General")
            content = doc.content.replace("\n", " ")
            
            formatted_str += f"Record #{i+1} [Source: {date} > {section}]:\nContent: {content}\n\n"
        return formatted_str

    def consult(self, query: str, k=5) -> Dict:
        """
        史官的核心工作流：检索 -> 阅读 -> 汇报
        """
        print(f"🕵️ [史官] 正在检索档案库: '{query}'...")
        
        # 1. 检索 (Retrieval)
        # 这里调用我们在 infrastructure 层封装好的 search 方法
        # 假设返回的是 LangChain 的 Document 对象列表
        raw_docs = self.kb.search(query, k=k)
        
        if not raw_docs:
            return {
                "answer": "报告：档案库中未发现与此相关的记录。",
                "raw_docs": []
            }

        # 2. 格式化上下文 (Context Assembly)
        context_str = self._format_context(raw_docs)
        
        # 3. 生成摘要 (Synthesis)
        print("🕵️ [史官] 正在根据证据撰写报告...")
        response_text = self.chain.invoke({
            "query": query,
            "context": context_str
        })

        # 返回结构化结果，供后续的“董事会”使用
        return {
            "query": query,
            "answer": response_text,  # 这是给用户/战略官看的摘要
            "raw_context": context_str, # 这是原始证据
            "source_docs": raw_docs     # 这是原始对象
        }

# 模拟数据
MOCK_DATA = """
# 2023-10-12 架构思考
## 设计原则
软件设计之美在于分离关注点。
KnowledgeBase 只负责存取，IngestionEngine 只负责处理。
这种解耦让未来的测试变得非常容易。

# 2023-10-13 心情日记
## 焦虑时刻
昨晚失眠了，一直在想房贷的事情。
感觉现在的收入结构太单一，抗风险能力差。

# 2023-10-14 工作复盘
## 项目 A 的反思
今天项目 A 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Go 语言在目前的适用性。
目前团队对 Go 的掌握程度不够，导致开发效率低下。

# 2023-10-15 工作复盘
## 项目 B 的反思
今天项目 B 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Python 语言在目前的适用性。
目前团队对 Python 的掌握程度不够，导致开发效率低下。

# 2023-10-16 工作复盘
## 项目 C 的反思
今天项目 C 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Java 语言在目前的适用性。
目前团队对 Java 的掌握程度不够，导致开发效率低下。

# 2023-10-17 工作复盘
## 项目 D 的反思
今天项目 D 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Rust 语言在目前的适用性。
目前团队对 Rust 的掌握程度不够，导致开发效率低下。

# 2023-10-18 工作复盘
## 项目 E 的反思
今天项目 E 的进度非常滞后。主要原因是在架构选型上犹豫太久。
我认为我们需要重新评估 Kotlin 语言在目前的适用性。
目前团队对 Kotlin 的掌握程度不够，导致开发效率低下。

# 2023-10-19 心情日记
## 焦虑时刻
昨晚失眠了，一直在想房贷的事情。
感觉现在的收入结构太单一，抗风险能力差。
"""

def main():
    # 1. 初始化底层存储 (The Warehouse)
    # reset_db=True 会清空之前的测试数据，方便调试
    kb = KnowledgeBase(persist_dir="./data/chroma_db", reset_db=False)
    
    # 2. 初始化加工引擎 (The Worker)
    # 把仓库交给搬运工
    engine = MemoryIngestionEngine(knowledge_base=kb)
    
    # 3. 执行数据注入 (Write Path)
    engine.process_file(MOCK_DATA, source_name="mock_test.md")
    
    # 4. 初始化史官 (Reader Agent)
    # 史官只需要仓库的钥匙 (kb)，不需要知道加工引擎的存在
    archivist = Archivist(kb=kb)
    
    # 5. 执行查询 (Read Path)
    print("\n--- 史官开始工作 ---")
    result = archivist.consult("2023-10-18 我心情很不好？")
    
    print("\n[史官回复]:")
    print(result["answer"])
    
if __name__ == "__main__":
    main()

