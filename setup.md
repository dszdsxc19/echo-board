# Local embeeding
Ref: https://docs.langchain.com/oss/python/integrations/text_embedding/ollama

brew install ollama 

自启动
brew services start ollama

# embdding models： https://ollama.com/search?c=embedding
ollama pull nomic-embed-text

ollama list

# embedding 不需要 ollama run
uv add langchain-ollama
uv add langchain-chroma

chorma embedding setup: 
- https://docs.langchain.com/oss/python/integrations/vectorstores/chroma
- https://docs.langchain.com/oss/python/integrations/text_embedding/ollama

# 大模型
- z.ai https://docs.bigmodel.cn/cn/guide/develop/langchain/introduction
- langchain anthropic: https://docs.langchain.com/oss/python/integrations/chat/anthropic
- 模型价格： https://open.bigmodel.cn/pricing

## 拓展 数据源，我的痛点是财务数据（数字难以感知）

选型，使用 Firefly III（而不是Beancount之类的）

docker-compose 启动：https://docs.firefly-iii.org/how-to/firefly-iii/installation/docker/

docker compose -f docker-compose.yml up -d --pull=always

mcp server: https://github.com/etnperlong/firefly-iii-mcp/?tab=readme-ov-file

http://localhost:3000/mcp 连接

# Langchain MCP: https://docs.langchain.com/oss/python/langchain/mcp#http

# Langchain Agents: https://docs.langchain.com/oss/python/langchain/agents

Zhipu 结构化输出有问题：https://docs.bigmodel.cn/cn/guide/capabilities/struct-output

Langchain 短期记忆：https://docs.langchain.com/oss/python/langchain/short-term-memory#read-short-term-memory-in-a-tool

核心结论：指定 thread_id 不代表绝对不失效，关键取决于 checkpointer 是否开启持久化存储。
关键场景拆解
若使用持久化 checkpointer（如 PostgresSaver、RedisSaver）
只要 thread_id 不变，后续无论何时接入（哪怕关闭会话、重启客户端），都能通过该 ID 读取到完整对话历史，短期记忆不会失效。
本质是对话历史存在数据库 / 缓存中，thread_id 只是 “检索钥匙”，数据本身不会因会话中断消失。
若使用非持久化 checkpointer（如默认的 InMemorySaver）
就算后续指定相同 thread_id，一旦遇到服务重启、进程关闭或内存清理，内存中的对话历史会被清空。
此时 thread_id 还在，但对应的记忆数据已消失，相当于 “钥匙还在，锁里的东西丢了”，仍会失效。
需要我帮你整理一份 **“指定 thread_id + 持久化 checkpointer” 的实操步骤 ** 吗？包含 RedisSaver 配置、thread_id 复用代码，确保记忆长期不失效。

智谱余额查看：https://bigmodel.cn/finance-center/finance/overview

